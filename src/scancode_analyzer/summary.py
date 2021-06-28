#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter
import attr

"""
Data Format and example output of analyzer summary, having unique
license detection issues and statistics.

codebase_level:

    - license_detection_issues_summary: SummaryLicenseIssues

        - unique_license_detection_issues: list of UniqueIssue
            - issue_categoryentifier: 1
            - files: list of FileRegions
                - path: "path/to/occurrence"
                - start_line: 1
                - end_line: 2
            - license_detection_issue: LicenseDetectionIssue

        - statistics: StatisticsLicenseIssues
            - total_files_with_license: 43
            - total_files_with_license_detection_issues: 17
            - total_unique_license_detection_issues: 3

            - issue_category_counts:
                - imperfect-match-coverage: 2
                - unknown-match: 1

            - issue_classification_id_counts:
                - text-lic-text-fragments: 1
                - notice-has-unknown-match: 1
                - reference-low-coverage-refs: 1

            - license_info_type_flags_counts:
                - license_text: 1
                - license_notice: 1
                - license_reference: 1

            - analysis_confidence_counts:
                - high: 1
                - medium: 2
                - low: 0
"""

@attr.s
class SummaryLicenseIssues:
    """
    Codebase level summary of License Detection Issues.
    """
    statistics = attr.ib()
    unique_license_detection_issues = attr.ib(factory=list)
    
    def to_dict(self):
        return attr.asdict(self)

    @staticmethod
    def summarize(license_issues, count_has_license, count_files_with_issues):
        """
        Generate summary with Unique Issues and Statistics.
        """
        unique_issues = UniqueIssue.get_unique_issues(
            license_issues,
        )
        statistics=StatisticsLicenseIssues.generate_statistics(
            license_issues=license_issues,
            count_unique_issues=len(unique_issues),
            count_has_license=count_has_license,
            count_files_with_issues=count_files_with_issues,
        )

        return SummaryLicenseIssues(
            unique_license_detection_issues=unique_issues,
            statistics=statistics,
        )


@attr.s
class StatisticsLicenseIssues:
    """
    All statistics on License Detection Issues from the analysis.
    """
    total_files_with_license = attr.ib(type=int)
    total_files_with_license_detection_issues = attr.ib(type=int)
    total_unique_license_detection_issues = attr.ib(type=int, default=0)

    # Stats on analyzer.LicenseDetectionIssue.issue_category
    issue_category_counts = attr.ib(factory=dict)
    # Stats on analyzer.LicenseDetectionIssue.issue_type.classification_id
    issue_classification_id_counts = attr.ib(factory=dict)

    # Stats on analyzer.LicenseDetectionIssue.issue_type.analysis_confidence
    analysis_confidence_counts = attr.ib(factory=dict)
    # Stats on the 4 flags of analyzer.LicenseDetectionIssue.issue_type
    # i.e. is_license['text','notice','tag','reference']
    license_info_type_counts = attr.ib(factory=dict)

    @staticmethod
    def generate_statistics(
        license_issues, count_unique_issues, count_has_license, count_files_with_issues
    ):
        """
        Get all unique license detection issues for the scan
        and their occurances, from all the issues.

        :param license_issues: list of LicenseDetectionIssue
        :param count_unique_issues: int
            Number of unique license detection issues
        :param count_has_license int:
            Number of files having license information
        :param count_files_with_issues: int
            Number of files having license detection issues
        :returns UniqueLicenseIssues: list of UniqueIssue
        """
        issue_statistics = dict(Counter((
            issue.issue_category for issue in license_issues
        )))
        issue_type_statistics = dict(Counter((
            issue.issue_type.classification_id
            for issue in license_issues
        )))

        flags_statistics = {
            "license_text": sum((
                issue.issue_type.is_license_text
                for issue in license_issues
            )),
            "license_notice": sum((
                issue.issue_type.is_license_notice
                for issue in license_issues
            )),
            "license_tag": sum((
                issue.issue_type.is_license_tag
                for issue in license_issues
            )),
            "license_reference": sum((
                issue.issue_type.is_license_reference
                for issue in license_issues
            )),
        }
        
        license_info_type_statistics = {
            flag: count
            for flag, count in flags_statistics.items()
            if count
        }

        analysis_confidence_statistics = dict(Counter((
            issue.issue_type.analysis_confidence for issue in license_issues
        )))

        return StatisticsLicenseIssues(
            total_files_with_license=count_has_license,
            total_files_with_license_detection_issues=count_files_with_issues,
            total_unique_license_detection_issues=count_unique_issues,
            issue_category_counts=issue_statistics,
            issue_classification_id_counts=issue_type_statistics,
            license_info_type_counts=license_info_type_statistics,
            analysis_confidence_counts=analysis_confidence_statistics,
        )


@attr.s
class UniqueIssue:
    """
    An unique License Detection Issue.
    """

    unique_identifier = attr.ib(type=int)
    license_detection_issue = attr.ib()
    files = attr.ib(factory=list)
    
    @staticmethod
    def get_formatted_unique_issue(
        license_issue, files, unique_identifier
    ):
        return UniqueIssue(
            license_detection_issue=license_issue.to_dict(),
            files=files,
            unique_identifier = unique_identifier,
        )

    @staticmethod
    def get_unique_issues(license_issues):
        """
        Get all unique license detection issues for the scan
        and their occurances, from all the issues.

        :param license_issues: list of LicenseDetectionIssue
        :returns UniqueLicenseIssues: list of UniqueIssue
        """
        identifiers = get_identifiers(license_issues)
        unique_issue_category_counts = dict(Counter(identifiers))

        unique_license_issues = []
        for issue_number, (unique_issue_identifier, counts) in enumerate(
            unique_issue_category_counts.items(), start=1,
        ):
            file_regions = (
                issue.file_regions[0]
                for issue in license_issues
                if unique_issue_identifier in [issue.identifier, issue.identifier_for_unknown_intro]
            )
            all_issues = (
                issue
                for issue in license_issues
                if unique_issue_identifier in [issue.identifier, issue.identifier_for_unknown_intro]
            )
            unique_license_issues.append(
                UniqueIssue.get_formatted_unique_issue(
                    files=list(file_regions),
                    license_issue=next(all_issues),
                    unique_identifier=issue_number,
                )
            )

        return unique_license_issues


def get_identifiers(license_issues):
    """
    Get identifiers for all license detection issues.

    :param license_issues: list of LicenseDetectionIssue
    :returns identifiers: list of tuples
    """
    identifiers = (
        issue.identifier if issue.issue_category != "unknown-match"
        else issue.identifier_for_unknown_intro
        for issue in license_issues
    )
    return identifiers
