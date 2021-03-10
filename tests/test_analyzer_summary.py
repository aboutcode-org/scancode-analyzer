#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import os

from commoncode.testcase import FileBasedTesting
from commoncode.resource import VirtualCodebase
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from results_analyze import analyzer
from results_analyze.df_file_io import DataIOJSON
from results_analyze.analyzer_summary import SummaryLicenseIssues
from results_analyze.analyzer_summary import StatisticsLicenseIssues
from results_analyze.analyzer_summary import UniqueIssue


class AnalyzerPluginSummary(FileBasedTesting):
    test_data_dir = os.path.join(
        os.path.dirname(__file__), 
        "data/analyzer-plugins/"
    )

    def test_analyze_results_plugin_load_from_json_analyze_summary(self):
    
        input_json = self.get_test_loc(
            "sample_files_result_same_unique_issues.json"
        )
        result_file = self.get_temp_file("json")
        args = [
            "--from-json",
            input_json,
            "--json-pp",
            result_file,
            "--analyze-license-results",
        ]
        run_scan_click(args)
        check_json_scan(
            self.get_test_loc(
                "results_analyzer_from_sample_json_expected_summary.json"
            ),
            result_file,
        )


class TestSummaryLicenseIssues(FileBasedTesting):
    test_data_dir = os.path.join(
        os.path.dirname(__file__),
        "data/analyzer-summary/"
    )

    @staticmethod
    def test_analyzer_summary_empty_list():
        summary = SummaryLicenseIssues.summarize([], 0, 0)
        assert summary.statistics.total_files_with_license_detection_issues == 0
        assert summary.statistics.issue_category_counts == {}
        assert summary.statistics.license_info_type_counts == {}
        assert summary.statistics.analysis_confidence_counts == {}
        assert summary.unique_license_detection_issues == []
        
    def test_analyzer_summary_statistics_one_issue(self):
        input_json = self.get_test_loc("one_issue.json")
        all_issues = get_all_license_issues_in_codebase(input_json)
        summary = attr.asdict( 
            SummaryLicenseIssues.summarize(all_issues, 1, 1)
        )
        expected_file = self.get_test_loc("one_issue_summary.json")
        expected_summary = DataIOJSON.load_json(expected_file)
        assert summary == expected_summary


class TestStatisticsLicenseIssues(FileBasedTesting):
    test_data_dir = os.path.join(
        os.path.dirname(__file__),
        "data/analyzer-summary/"
    )

    @staticmethod
    def test_analyzer_summary_statistics_empty_list():
        stats = StatisticsLicenseIssues.generate_statistics([], 0, 0, 0)
        assert stats.total_files_with_license_detection_issues == 0
        assert stats.issue_category_counts == {}
        assert stats.license_info_type_counts == {}
        assert stats.analysis_confidence_counts == {}

    def test_analyzer_summary_statistics_one_issue(self):
        input_json = self.get_test_loc("one_issue.json")
        all_issues = get_all_license_issues_in_codebase(input_json)
        stats = attr.asdict( 
            StatisticsLicenseIssues.generate_statistics(all_issues, 1, 1, 1)
        )
        expected_file = self.get_test_loc("one_issue_summary.json")
        expected_summary = DataIOJSON.load_json(expected_file)
        assert stats == expected_summary["statistics"]


class TestUniqueIssue(FileBasedTesting):
    test_data_dir = os.path.join(
        os.path.dirname(__file__),
        "data/analyzer-summary/"
    )

    @staticmethod
    def test_analyzer_summary_get_unique_issues_empty_list():
        unique_license_issues = UniqueIssue.get_unique_issues([])
        assert unique_license_issues == []
        

    def test_analyzer_summary_get_unique_issues_socat_count(self):
        
        input_json = self.get_test_loc("multiple_files_same_issues_socat.json")
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_license_issues = UniqueIssue.get_unique_issues(
            all_issues
        )
        assert len(unique_license_issues) == 1
        
    def test_analyzer_summary_get_unique_issues_socat_all_occurrences(self):
        
        input_json = self.get_test_loc("multiple_files_same_issues_socat.json")
        expected_file = self.get_test_loc(
            "multiple_files_same_issues_socat_file_regions.json"
        )
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_license_issues = UniqueIssue.get_unique_issues(
            all_issues
        )
        unique_issue = unique_license_issues.pop()
        file_regions = unique_issue.files
        unique_issue_file_regions = [
            attr.asdict(file_region)
            for file_region in file_regions
        ]
        expected_file_regions = DataIOJSON.load_json(expected_file)
        assert unique_issue_file_regions == expected_file_regions
        
    def test_analyzer_summary_get_unique_issues_iptables_count(self):
        
        input_json = self.get_test_loc(
            "multiple_files_same_issues_iptables.json"
        )
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_issues = UniqueIssue.get_unique_issues(all_issues)
        assert len(unique_issues) == 1
        
    def test_analyzer_summary_get_unique_issues_iptables_all_occurrences(self):
        
        input_json = self.get_test_loc(
            "multiple_files_same_issues_iptables.json"
        )
        expected_file = self.get_test_loc(
            "multiple_files_same_issues_iptables_file_regions.json"
        )
        expected_file_regions = DataIOJSON.load_json(expected_file)
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_issues = UniqueIssue.get_unique_issues(all_issues)
        unique_issue = unique_issues.pop()
        unique_issue_file_regions = [
            attr.asdict(file_region)
            for file_region in unique_issue.files
        ]
        assert unique_issue_file_regions == expected_file_regions

    def test_analyzer_summary_get_unique_issues_mixed_1(self):
        
        input_json = self.get_test_loc("multiple_files_mixed_issues_1.json")
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_issues = UniqueIssue.get_unique_issues(all_issues)
        assert len(unique_issues) == 2
        
    def test_analyzer_summary_get_unique_issues_mixed_2(self):
            
        input_json = self.get_test_loc("multiple_files_mixed_issues_2.json")
        all_issues = get_all_license_issues_in_codebase(input_json)
        unique_issues = UniqueIssue.get_unique_issues(all_issues)
        assert len(unique_issues) == 5

    def test_analyzer_summary_get_formatted_unique_issue(self):
        input_json = self.get_test_loc("one_issue.json")
        [issue] = get_all_license_issues_in_codebase(input_json)
        unique_issue = UniqueIssue.get_formatted_unique_issue(
            issue,
            [issue.file_regions],
            1
        )
        assert all(
            key not in unique_issue.license_detection_issue
            for key in ["path", "identifier"]
        )
        assert type(unique_issue.license_detection_issue) == dict
        assert len(unique_issue.license_detection_issue['original_licenses']) == 1


def get_all_license_issues_in_codebase(input_json):
    
    codebase = VirtualCodebase(input_json)
    all_license_issues = []

    for resource in codebase.walk():

        ars = list(analyzer.LicenseDetectionIssue.from_license_matches(
            license_matches=getattr(resource, "licenses", []),
            is_license_text=getattr(resource, "is_license_text", False),
            is_legal=getattr(resource, "is_legal", False),
            path=getattr(resource, "path"),
        ))
        all_license_issues.extend(ars)

    return all_license_issues
