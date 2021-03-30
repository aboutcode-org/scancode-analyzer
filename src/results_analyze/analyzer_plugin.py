#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import traceback

import attr
from license_expression import Licensing

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl

from results_analyze import analyzer
from results_analyze import analyzer_summary


MISSING_OPTIONS_MESSAGE = (
    "The scan must be run with these options: "
    "--license --license-text --is-license-text --classify --info"
)


@post_scan_impl
class ResultsAnalyzer(PostScanPlugin):
    """
    Analyze license detections for potential issues.
    """

    codebase_attributes = {
        "license_detection_issues_summary": attr.ib(default=attr.Factory(dict))
    }

    resource_attributes = {
        "license_detection_issues": attr.ib(default=attr.Factory(list))
    }

    sort_order = 80

    options = [
        PluggableCommandLineOption(
            ("--analyze-license-results",),
            is_flag=True,
            default=False,
            help="Performs a license detection analysis to detect different kinds of "
            "potential license detection issues in scancode. "
            + MISSING_OPTIONS_MESSAGE,
            help_group=POST_SCAN_GROUP,
        ),
    ]

    def is_enabled(self, analyze_license_results, **kwargs):
        return analyze_license_results

    def process_codebase(self, codebase, **kwargs):
        msg = (
            "Cannot analyze scan for license detection errors, because "
            "required attributes are missing. " + MISSING_OPTIONS_MESSAGE,
        )

        license_issues = []
        count_has_license = 0
        count_files_with_issues = 0

        for resource in codebase.walk():
            if not resource.is_file:
                continue

            # Case where a license scan was not performed
            if not hasattr(resource, "licenses"):
                codebase.errors.append(msg)
                break

            # Where the resource does not have any detected license
            license_matches_serialized = getattr(resource, "licenses", [])
            if not license_matches_serialized:
                continue

            # Case where any attribute essential for analysis is missing
            if not is_analyzable(resource):
                codebase.errors.append(msg)
                break

            count_has_license += 1
            
            try:
                license_matches = LicenseMatch.from_files_licenses(
                    license_matches_serialized
                )
            except KeyError as e:
                trace = traceback.format_exc()
                msg = f"Cannot convert scancode data to LicenseMatch class: {e}\n{trace}"
                codebase.errors.append(msg)
                raise ScancodeDataChangedError(msg)
            
            try:
                ars = list(analyzer.LicenseDetectionIssue.from_license_matches(
                    license_matches=license_matches,
                    is_license_text=getattr(resource, "is_license_text", False),
                    is_legal=getattr(resource, "is_legal", False),
                    path=getattr(resource, "path"),
                ))
                if ars:
                    count_files_with_issues += 1
                license_issues.extend(ars)
                resource.license_detection_issues = [
                    ar.to_dict(is_summary=False)
                    for ar in ars
                ]

            except Exception as e:
                trace = traceback.format_exc()
                msg = f"Cannot analyze scan for license scan errors: {e}\n{trace}"
                resource.scan_errors.append(msg)
            codebase.save_resource(resource)
            

        try:
            summary = analyzer_summary.SummaryLicenseIssues.summarize(
                license_issues,
                count_has_license,
                count_files_with_issues,
            )
            codebase.attributes.license_detection_issues_summary.update(
                summary.to_dict(),
            )

        except Exception as e:
            trace = traceback.format_exc()
            msg = f"Cannot summarize license detection issues: {e}\n{trace}"
            resource.scan_errors.append(msg)
        codebase.save_resource(resource)


class ScancodeDataChangedError(Exception):
    """
    Raised when the scan results data format does not match what we expect.
    """
    pass
    

@attr.s
class LicenseMatch:
    """
    Represent a license match to a rule.
    """
    license_expression = attr.ib()
    score = attr.ib()
    start_line = attr.ib()
    end_line = attr.ib()
    rule_identifier = attr.ib()
    is_license_text = attr.ib()
    is_license_notice = attr.ib()
    is_license_reference = attr.ib()
    is_license_tag = attr.ib()
    is_license_intro = attr.ib()
    matcher = attr.ib()
    matched_length = attr.ib()
    rule_length = attr.ib()
    match_coverage = attr.ib()
    rule_relevance = attr.ib()
    matched_text = attr.ib()
    
    @classmethod
    def from_files_licenses(cls, license_matches):
        """
        Return LicenseMatch built from the scancode files.licenses data structure.
        """
        matches = []
        licensing = Licensing()
        # Whenever we have multiple matches with the same expression, we want to only
        # keep the first and skip the secondary matches
        skip_secondary_matches = 0
        
        for license_match in license_matches:
            if skip_secondary_matches:
                skip_secondary_matches -= 1
                continue
            
            matched_rule = license_match["matched_rule"]
            # key = license_match["key"]
            license_expression = matched_rule["license_expression"]
            expression_keys = licensing.license_keys(license_expression)
            
            if len(expression_keys) != 1:
                skip_secondary_matches = len(expression_keys) - 1                
            
            matches.append(
                cls(
                    license_expression = license_expression,
                    score = license_match["score"],
                    start_line = license_match["start_line"],
                    end_line = license_match["end_line"],
                    rule_identifier = matched_rule["identifier"],
                    is_license_text = matched_rule["is_license_text"],
                    is_license_notice = matched_rule["is_license_notice"],
                    is_license_reference = matched_rule["is_license_reference"],
                    is_license_tag = matched_rule["is_license_tag"],
                    is_license_intro = matched_rule["is_license_intro"],
                    matcher = matched_rule["matcher"],
                    matched_length = matched_rule["matched_length"],
                    rule_length = matched_rule["rule_length"],
                    match_coverage = matched_rule["match_coverage"],
                    rule_relevance = matched_rule["rule_relevance"],
                    matched_text = license_match["matched_text"],
                )
            )
        
        return matches

    def to_dict(self):
        return attr.asdict(self)


def is_analyzable(resource):
    """
    Return True if resource has all the data required for the analysis.
    Return False if any of the essential attributes are missing from the resource.
    :param resource: commoncode.resource.Resource
    """
    license_matches = getattr(resource, "licenses", [])
    has_is_license_text = hasattr(resource, "is_license_text")
    has_is_legal = hasattr(resource, "is_legal")
    has_matched_text = all("matched_text" in match for match in license_matches)

    return has_is_license_text and has_matched_text and has_is_legal
