#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl

from results_analyze import analyzer

MISSING_OPTIONS_MESSAGE = (
    "The scan must be run with these options: "
    "--license --license-text --is-license-text --classify --info"
)


@post_scan_impl
class ResultsAnalyzer(PostScanPlugin):
    """
    Add the "license_detection_issues" list which has the analysis, type information
    and suggested license match for each license match issue.
    """

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

        all_license_issues = []
        count_has_license = 0

        for resource in codebase.walk():
            if not resource.is_file:
                continue

            # Case where a license scan was not performed
            if not hasattr(resource, "licenses"):
                codebase.errors.append(msg)
                break

            # Where the resource does not have any detected license
            license_matches = getattr(resource, "licenses", [])
            if not license_matches:
                continue

            # Case where any attribute essential for analysis is missing
            if not is_analyzable(resource):
                codebase.errors.append(msg)
                break

            count_has_license += 1
            try:
                ars = list(analyzer.LicenseDetectionIssue.from_license_matches(
                    license_matches=license_matches,
                    is_license_text=getattr(resource, "is_license_text", False),
                    is_legal=getattr(resource, "is_legal", False),
                    path=getattr(resource, "path"),
                ))
                all_license_issues.extend(ars)
                resource.license_detection_issues = [ar.to_dict() for ar in ars]

            except Exception as e:
                msg = f"Cannot analyze scan for license scan errors: {str(e)}"
                resource.scan_errors.append(msg)
            codebase.save_resource(resource)


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
