#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import attr

from commoncode.testcase import FileBasedTesting
from commoncode.resource import Resource
from commoncode.resource import VirtualCodebase
from commoncode.resource import build_attributes_defs
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from file_io import load_json
from results_analyze.analyzer_plugin import is_analyzable
from results_analyze.analyzer_plugin import ResultsAnalyzer
from results_analyze.analyzer_plugin import MISSING_OPTIONS_MESSAGE
from results_analyze.analyzer_plugin import LicenseMatch



class AnalyzerPlugin(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/analyzer-plugins/")
    missing_options_full_msg = (
        "Cannot analyze scan for license detection errors, because "
        "required attributes are missing. " + MISSING_OPTIONS_MESSAGE,
    )

    def test_analyze_results_plugin(self):
        test_dir = self.get_test_loc("scan-files/")
        result_file = self.get_temp_file("json")
        args = [
            "--license",
            "--info",
            "--license-text",
            "--is-license-text",
            "--classify",
            test_dir,
            "--json-pp",
            result_file,
            "--analyze-license-results",
        ]
        run_scan_click(args)
        check_json_scan(
            self.get_test_loc("results_analyzer_expected.json"),
            result_file,
            remove_file_date=True,
        )

    def test_analyze_results_plugin_load_from_json_analyze(self):

        input_json = self.get_test_loc("sample_files_result.json")
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
            self.get_test_loc("results_analyzer_from_sample_json_expected.json"),
            result_file,
        )

    @staticmethod
    def test_is_analyzable_returns_true_if_all_attributes_are_present():
        data = {
            "licenses": [{"matched_text": "MIT License"}],
            "is_license_text": True,
            "is_legal": False,
        }
        test_resource = create_mock_resource(data)
        assert is_analyzable(test_resource)

    @staticmethod
    def test_is_analyzable_returns_false_if_no_matched_text():
        data = {
            "licenses": [{"key": "mit"}],
            "is_license_text": False,
            "is_legal": False,
        }
        test_resource = create_mock_resource(data)
        assert not is_analyzable(test_resource)

    @staticmethod
    def test_is_analyzable_returns_false_missing_is_legal():
        data = {
            "licenses": [{"matched_text": "MIT License"}],
            "is_license_text": True,
        }
        test_resource = create_mock_resource(data)
        assert not is_analyzable(test_resource)

    @staticmethod
    def test_is_analyzable_returns_false_missing_is_license_text():
        data = {
            "licenses": [{"matched_text": "MIT License"}],
            "is_legal": False,
        }
        test_resource = create_mock_resource(data)
        assert not is_analyzable(test_resource)

    @staticmethod
    def test_is_analyzable_returns_false_if_missing_all():
        data = {}
        test_resource = create_mock_resource(data)
        assert not is_analyzable(test_resource)

    def test_process_codebase_adds_error_if_missing_is_legal(self):
        codebase = initialize_and_analyze_mock_codebase(
            self.get_test_loc("sample_files_missing_legal.json")
        )

        assert len(codebase.errors) == 1
        assert codebase.errors.pop() == self.missing_options_full_msg

    def test_process_codebase_adds_error_if_missing_is_license_text(self):
        codebase = initialize_and_analyze_mock_codebase(
            self.get_test_loc("sample_files_missing_is_license_text.json")
        )

        assert len(codebase.errors) == 1
        assert codebase.errors.pop() == self.missing_options_full_msg

    def test_process_codebase_adds_error_if_missing_license_text(self):
        codebase = initialize_and_analyze_mock_codebase(
            self.get_test_loc("sample_files_missing_license_text.json")
        )

        assert len(codebase.errors) == 1
        assert codebase.errors.pop() == self.missing_options_full_msg

    def test_process_codebase_adds_error_if_missing_license(self):
        codebase = initialize_and_analyze_mock_codebase(
            self.get_test_loc("sample_files_missing_licenses.json")
        )

        assert len(codebase.errors) == 1
        assert codebase.errors.pop() == self.missing_options_full_msg

    def test_validate_resource_raise_exception_if_analysis_error(self):
        input_json = self.get_test_loc("sample_file_make_analysis_fail.json")
        codebase = VirtualCodebase(input_json)
        analyzer_plugin = ResultsAnalyzer()

        try:
            analyzer_plugin.process_codebase(codebase=codebase)
            self.fail(msg="Exception not raised")
        except Exception:
            pass


def create_mock_resource(data):
    """
    Create a new resource subclass and return an instance of that subclass using the provided the
    data dictionary.
    """
    resource_attributes = build_attributes_defs(data)

    resource_class = attr.make_class(
        name="MockResource", attrs=resource_attributes, slots=True, bases=(Resource,)
    )

    resource = resource_class(
        name="name",
        location="/foo/bar",
        path="some/path/name",
        rid=24,
        pid=23,
        is_file=True,
        **data
    )

    return resource


def initialize_and_analyze_mock_codebase(input_json):
    codebase = VirtualCodebase(input_json)
    analyzer_plugin = ResultsAnalyzer()
    analyzer_plugin.process_codebase(codebase=codebase)
    return codebase


class TestLicenseMatch(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/analyzer-plugins/")
    
    def test_from_files_license_empty_list(self):

        license_matches = LicenseMatch.from_files_licenses([])
        assert license_matches == []
        
    def test_from_files_license_one_match(self):
        test_file = self.get_test_loc("from_files_license_one_match.json")
        license_matches_serialized = load_json(test_file)
        [license_match_serialized] = license_matches_serialized
        license_rule_serialized = license_match_serialized["matched_rule"]
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        [license_match] = license_matches
        
        assert len(license_matches) == 1
        assert license_match.license_expression == license_rule_serialized[
            "license_expression"
        ]
        assert license_match.is_license_intro == license_rule_serialized[
            "is_license_intro"
        ]
        assert license_match.start_line == license_match_serialized["start_line"]
        assert license_match.matcher == license_rule_serialized["matcher"]
        assert license_match.match_coverage == license_rule_serialized["match_coverage"]
        assert license_match.matched_length == license_rule_serialized["matched_length"]
        assert license_match.matched_text == license_match_serialized["matched_text"]
        assert license_match.matched_length == license_rule_serialized["matched_length"]

    def test_from_files_license_multiple_match_simple_few(self):
        test_file = self.get_test_loc(
            "from_files_license_multiple_match_simple_few.json"
        )
        license_matches_serialized = load_json(test_file)
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        assert len(license_matches) == 2
        
    def test_from_files_license_multiple_match_simple_many(self):
        test_file = self.get_test_loc(
            "from_files_license_multiple_match_simple_many.json"
        )
        license_matches_serialized = load_json(test_file)
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        assert len(license_matches) == 7

    def test_from_files_license_two_match_complex(self):
        test_file = self.get_test_loc("from_files_license_two_match_complex.json")
        license_matches_serialized = load_json(test_file)
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        assert len(license_matches) == 1
        
    def test_from_files_license_three_match_complex(self):
        test_file = self.get_test_loc("from_files_license_three_match_complex.json")
        license_matches_serialized = load_json(test_file)
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        assert len(license_matches) == 1
        
    def test_from_files_license_match_simple_and_complex(self):
        test_file = self.get_test_loc(
            "from_files_license_match_simple_and_complex.json"
        )
        license_matches_serialized = load_json(test_file)
        license_matches = LicenseMatch.from_files_licenses(license_matches_serialized)
        assert len(license_matches) == 4

