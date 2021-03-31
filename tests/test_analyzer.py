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

from file_io import load_json

from results_analyze import analyzer
from results_analyze.analyzer_summary import get_identifiers
from results_analyze.analyzer_plugin import LicenseMatch

@attr.s
class MockLicenseMatch:
    """
    This is a mock of LicenseMatch where all attributes are optional.
    """
    license_expression = attr.ib(default=None)
    score = attr.ib(default=None)
    start_line = attr.ib(default=None)
    end_line = attr.ib(default=None)
    rule_identifier = attr.ib(default=None)
    is_license_text = attr.ib(default=None)
    is_license_notice = attr.ib(default=None)
    is_license_reference = attr.ib(default=None)
    is_license_tag = attr.ib(default=None)
    is_license_intro = attr.ib(default=None)
    matcher = attr.ib(default=None)
    matched_length = attr.ib(default=None)
    rule_length = attr.ib(default=None)
    match_coverage = attr.ib(default=None)
    rule_relevance = attr.ib(default=None)
    matched_text = attr.ib(default=None)
    

class TestAnalyzer(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/analyzer/")

    def test_analyzer_is_correct_detection_case_all_3_seq(self):
        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_all_3_seq.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert not analyzer.is_correct_detection(license_matches)

    def test_analyzer_is_correct_detection_case_all_1_hash(self):
        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_all_1_hash.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_correct_detection(license_matches)

    def test_analyzer_is_correct_detection_case_mixed_123(self):
        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_mixed_123.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert not analyzer.is_correct_detection(license_matches)

    def test_analyzer_is_correct_detection_case_mixed_14(self):
        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_mixed_14.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_correct_detection(license_matches)

    def test_analyzer_is_match_coverage_less_than_threshold_low(self):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_low.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_match_coverage_less_than_threshold(
            license_matches, threshold=analyzer.IMPERFECT_MATCH_COVERAGE_THR
        )

    def test_analyzer_is_match_coverage_less_than_threshold_near_perfect(self):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_near_perfect.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_match_coverage_less_than_threshold(
            license_matches, threshold=analyzer.NEAR_PERFECT_MATCH_COVERAGE_THR
        )
        assert not analyzer.is_match_coverage_less_than_threshold(
            license_matches, threshold=analyzer.IMPERFECT_MATCH_COVERAGE_THR
        )

    def test_analyzer_is_match_coverage_less_than_threshold_perfect(self):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_perfect.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert not analyzer.is_match_coverage_less_than_threshold(
            license_matches, threshold=analyzer.NEAR_PERFECT_MATCH_COVERAGE_THR
        )

    def test_analyzer_query_coverage_coefficient_not_extra_words_correct_detection(
        self,
    ):
        test_file = self.get_test_loc(
            "analyzer_calculate_query_coverage_coefficient_not_extra_words_correct_det.json"
        )
        [license_match] = load_license_matches_from_json(test_file)
        assert analyzer.calculate_query_coverage_coefficient(license_match) == 0

    def test_analyzer_calculate_query_coverage_coefficient_not_extra_words_low_coverage(
        self,
    ):
        test_file = self.get_test_loc(
            "analyzer_calculate_query_coverage_coefficient_not_extra_words_low_coverage.json"
        )
        [license_match] = load_license_matches_from_json(test_file)
        assert analyzer.calculate_query_coverage_coefficient(license_match) == 0

    def test_analyzer_calculate_query_coverage_coefficient_is_extra_words(self):
        test_file = self.get_test_loc("analyzer_is_extra_words_true_one.json")
        license_matches = load_license_matches_from_json(test_file)
        for license_match in license_matches:
            assert analyzer.calculate_query_coverage_coefficient(license_match) > 0

    def test_analyzer_is_extra_words_true_one(self):
        test_file = self.get_test_loc("analyzer_is_extra_words_true_one.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_extra_words(license_matches)

    def test_analyzer_is_extra_words_false(self):
        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_all_3_seq.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert not analyzer.is_extra_words(license_matches)

    def test_analyzer_is_false_positive_true(self):
        test_file = self.get_test_loc("analyzer_is_false_positive_true.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_false_positive(license_matches)

    def test_analyzer_is_false_positive_false_tag(self):
        test_file = self.get_test_loc("analyzer_is_false_positive_false_tag.json")
        license_matches = load_license_matches_from_json(test_file)
        assert not analyzer.is_false_positive(license_matches)
        
    def test_analyzer_has_unknown_matches_1(self):
        test_file = self.get_test_loc("analyzer_has_unknown_matches_1.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.has_unknown_matches(license_matches)
        
    def test_analyzer_has_unknown_matches_2(self):
        test_file = self.get_test_loc("analyzer_has_unknown_matches_2.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.has_unknown_matches(license_matches)
        
    def test_analyzer_get_analysis_for_region_case_unknown_match(self):
        test_file = self.get_test_loc("analyzer_has_unknown_matches_2.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_id = analyzer.get_analysis_for_region(license_matches)
        assert issue_id == "unknown-match"

    def test_analyzer_get_analysis_for_region_case_correct_hash(self):

        test_file = self.get_test_loc(
            "analyzer_is_correct_detection_case_all_1_hash.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "correct-license-detection"

    def test_analyzer_get_analysis_for_region_case_correct_aho(self):
        test_file = self.get_test_loc(
            "analyzer_get_analysis_for_region_correct_aho.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "correct-license-detection"

    def test_analyzer_get_analysis_for_region_case_incorrect_low_coverage(self):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_low.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "imperfect-match-coverage"

    def test_analyzer_get_analysis_for_region_case_incorrect_near_perfect_coverage(
        self,
    ):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_near_perfect.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "near-perfect-match-coverage"

    def test_analyzer_get_analysis_for_region_case_incorrect_extra_words(self):
        test_file = self.get_test_loc("analyzer_is_extra_words_true.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "extra-words"

    def test_analyzer_get_analysis_for_region_case_incorrect_false_positives(self):
        test_file = self.get_test_loc("analyzer_is_false_positive_true.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "false-positive"

    def test_analyzer_get_analysis_for_region_case_false_positive_true_1(self):
        test_file = self.get_test_loc("analyze_for_scan_errors_false_positive_1.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "false-positive"

    def test_analyzer_get_analysis_for_region_case_false_positive_true_2(self):
        test_file = self.get_test_loc("analyze_for_scan_errors_false_positive_2.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_category = analyzer.get_analysis_for_region(license_matches)
        assert issue_category == "false-positive"

    def test_analyzer_is_license_case_mixed_text(self):
        test_file = self.get_test_loc("analyzer_is_license_case_mix_text.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_text")

    def test_analyzer_is_license_case_all_notice(self):
        test_file = self.get_test_loc("analyzer_is_license_case_all_notice.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_notice")

    def test_analyzer_is_license_case_mixed_notice(self):
        test_file = self.get_test_loc(
            "analyzer_is_match_coverage_less_than_threshold_low.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_notice")

    def test_analyzer_is_license_case_one_reference(self):
        test_file = self.get_test_loc("analyzer_is_license_case_one_reference.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_reference")

    def test_analyzer_is_license_case_mixed_tag(self):
        test_file = self.get_test_loc("analyzer_is_license_case_mix_tag.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_tag")

    def test_analyzer_is_license_case_all_ref(self):
        test_file = self.get_test_loc("analyzer_is_license_case_all_reference.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_reference")
        
    def test_analyzer_is_license_case_intro(self):
        test_file = self.get_test_loc("analyzer_is_license_case_intro_one.json")
        license_matches = load_license_matches_from_json(test_file)
        assert analyzer.is_license_case(license_matches, "is_license_intro")
        
    def test_analyzer_get_error_rule_type_case_notice(self):
        test_file = self.get_test_loc("analyzer_is_license_case_intro_one.json")
        license_matches = load_license_matches_from_json(test_file)
        issue_rule_type = analyzer.get_issue_rule_type(
            license_matches,
            is_license_text=False,
            is_legal=False,
        )
        assert issue_rule_type == "intro"

    def test_analyzer_get_error_rule_type_case_notice(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_rule_type = analyzer.get_issue_rule_type(
            license_matches,
            is_license_text=False,
            is_legal=False,
        )
        assert issue_rule_type == "notice"

    def test_get_error_rule_sub_type_case_multiple_or(self):
        test_file = self.get_test_loc(
            "get_error_rule_sub_type_case_notice_multiple_keys.json"
        )
        matches = load_license_matches_from_json(test_file)
        issue_type = analyzer.get_issue_type(
            license_matches=matches,
            is_license_text=False,
            is_legal=False,
            issue_category="imperfect-match-coverage",
            issue_rule_type="notice",
        )
        assert issue_type == "notice-and-or-with-notice"

    def test_get_issue_type_case_single_key(self):
        test_file = self.get_test_loc(
            "get_error_rule_sub_type_case_notice_single_key.json"
        )
        matches = load_license_matches_from_json(test_file)
        issue_type = analyzer.get_issue_type(
            license_matches=matches,
            is_license_text=False,
            is_legal=False,
            issue_category="imperfect-match-coverage",
            issue_rule_type="notice",
        )
        assert issue_type == "notice-single-key-notice"

    def test_get_license_notice_issue_type_case_notice_unknown(self):
        test_file = self.get_test_loc(
            "get_error_rule_sub_type_case_notice_unknown.json"
        )
        matches = load_license_matches_from_json(test_file)
        issue_type = analyzer.get_license_notice_issue_type(
            license_matches=matches, issue_category="imperfect-match-coverage"
        )
        assert issue_type == "notice-has-unknown-match"

    def test_get_issue_type_case_ref_lead_in(self):
        test_file = self.get_test_loc("get_error_rule_sub_type_case_ref_lead_in.json")
        matches = load_license_matches_from_json(test_file)
        issue_type = analyzer.get_issue_type(
            license_matches=matches,
            is_license_text=False,
            is_legal=False,
            issue_category="imperfect-match-coverage",
            issue_rule_type="reference",
        )
        assert issue_type == "reference-lead-in-or-unknown-refs"

    def test_get_issue_type_case_ref_unknown(self):
        test_file = self.get_test_loc("get_error_rule_sub_type_case_ref_unknown.json")
        matches = load_license_matches_from_json(test_file)
        issue_type = analyzer.get_issue_type(
            license_matches=matches,
            is_license_text=False,
            is_legal=False,
            issue_category="imperfect-match-coverage",
            issue_rule_type="reference",
        )
        assert issue_type == "reference-lead-in-or-unknown-refs"

    def test_merge_string_without_overlap(self):
        test_file = self.get_test_loc("merge_strings_test_strings.json")
        strings = load_json(test_file)
        merged_string = analyzer.merge_string_without_overlap(
            strings["merge_without_overlap_string_1"],
            strings["merge_without_overlap_string_2"],
        )

        assert merged_string == strings["merge_without_overlap"]

    def test_merge_string_with_overlap(self):
        test_file = self.get_test_loc("merge_strings_test_strings.json")
        strings = load_json(test_file)
        merged_string = analyzer.merge_string_with_overlap(
            strings["merge_with_overlap_string_1"],
            strings["merge_with_overlap_string_2"],
        )

        assert merged_string == strings["merge_with_overlap"]

    def test_get_start_end_line(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments_group_1.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        start_line, end_line = analyzer.get_start_end_line(license_matches)
        assert start_line == 14
        assert end_line == 34

    def test_predict_license_expression(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments_group_1.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        expectation_file = self.get_test_loc("consolidated_match_expected.json")
        [expected_prediction] = load_license_matches_from_json(expectation_file)
        license_expression = analyzer.predict_license_expression(license_matches)
        assert license_expression == expected_prediction.license_expression

    def test_get_license_match_suggestion(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments_group_1.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        expectation_file = self.get_test_loc("consolidated_match_expected.json")
        [expected_match] = load_license_matches_from_json(expectation_file)
        license_expression, matched_text = analyzer.get_license_match_suggestion(
            license_matches, issue_category="imperfect-match-coverage", issue_type="__"
        )
        assert matched_text == expected_match.matched_text
        assert license_expression == expected_match.license_expression

    def test_consolidate_matches(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments_group_1.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        expectation_file = self.get_test_loc("consolidated_match_expected.json")
        [expected_match] = load_license_matches_from_json(expectation_file)
        matched_text = analyzer.consolidate_matches(license_matches)
        assert matched_text == expected_match.matched_text

    def test_get_identifiers(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments_group_1.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issues = analyzer.LicenseDetectionIssue.from_license_matches(
            license_matches=license_matches,
            path="path/to/group_matches_by_location_analyze_result.json",
            is_license_text=False,
            is_legal=False,
        )
        result = list(get_identifiers([next(issues)]))
        expected = [(
            ('lead-in_unknown_67.RULE', 100.0),
            ('lgpl_bare_single_word.RULE', 100.0),
            ('lead-in_unknown_67.RULE', 100.0),
            ('lgpl_bare_single_word.RULE', 100.0),
            ('bsd-new_145.RULE', 100.0),
            ('agpl-3.0-plus_112.RULE', 90.83),
            ('lead-in_unknown_77.RULE', 100.0),
        )]
        assert result == expected
        
    def test_get_identifier_unknown_intro(self):
        test_file = self.get_test_loc("analyzer_is_license_case_intro_one.json")
        license_matches = load_license_matches_from_json(test_file)
        issue = analyzer.LicenseDetectionIssue.from_license_matches(
            license_matches=license_matches,
            path="path/to/group_matches_by_location_analyze_result.json",
            is_license_text=False,
            is_legal=False,
        )
        result = list(get_identifiers(issue))
        expected = [(
            (
                'license-intro_26.RULE',
                100.0,
                (
                    'this', 'file', 'and', 'its', 'contents', 'are', 'licensed',
                    'under', 'the', 'timescale', 'license',
                )
            ),
        )]
        assert result == expected

    def test_analyzer_analyze_region_for_license_scan_issues_notice(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments.json"
        )
        license_matches = load_license_matches_from_json(test_file)

        issue_category, issue_type = analyzer.analyze_region_for_license_scan_issues(
            license_matches, is_license_text=False, is_legal=False
        )
        assert issue_type == "notice-has-unknown-match"

    def test_analyzer_analyze_region_for_license_scan_issues_intro(self):
        test_file = self.get_test_loc(
            "analyzer_is_license_case_intro_many.json"
        )
        license_matches = load_license_matches_from_json(test_file)
        issue_id, issue_type = analyzer.analyze_region_for_license_scan_issues(
            license_matches, is_license_text=False, is_legal=False
        )
        assert issue_id == "unknown-match"
        assert issue_type == "intro-unknown-match"

    def test_analyzer_group_matches_boundary_case_lines_threshold(self):
        license_matches = [
            MockLicenseMatch(start_line=14, end_line=14),
            MockLicenseMatch(start_line=19, end_line=19),
        ]
        grouped_matches = analyzer.group_matches(
            license_matches=license_matches,
            lines_threshold=analyzer.LINES_THRESHOLD
        )
        assert len(list(grouped_matches)) == 2

    # TODO: don't group false positives together
    def test_analyzer_group_matches_multiple_false_positives(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_multiple_false_positives.json"
        )
        ungrouped_matches = load_license_matches_from_json(test_file)
        grouped_matches = analyzer.group_matches(
            ungrouped_matches, analyzer.LINES_THRESHOLD
        )
        assert len(list(grouped_matches)) == 3

    def test_analyzer_group_matches_notice_reference_fragments(self):
        test_file = self.get_test_loc(
            "analyzer_group_matches_notice_reference_fragments.json"
        )
        ungrouped_matches = load_license_matches_from_json(test_file)
        grouped_matches = analyzer.group_matches(
            ungrouped_matches, analyzer.LINES_THRESHOLD
        )
        assert len(list(grouped_matches)) == 2


class TestFromLicenseMatches(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/analyzer/")

    def test_analyze_license_matches_return_empty_list_with_none_matches(self):
        results = analyzer.LicenseDetectionIssue.from_license_matches(None)
        assert results == []

    def test_analyze_license_matches_return_empty_list_with_empty_matches(self):
        results = analyzer.LicenseDetectionIssue.from_license_matches([])
        assert results == []

    def test_dont_group_license_matches_in_high_license_text_files(self):
        test_file = self.get_test_loc("dont_group_matches_in_legal_file.json")
        file_scan_result = load_json(test_file)
        matched_licences = LicenseMatch.from_files_licenses(
            file_scan_result["licenses"]
        )
        is_license_text = True
        is_legal = file_scan_result["is_legal"]
        issues = analyzer.LicenseDetectionIssue.from_license_matches(
            license_matches=matched_licences,
            path="path/to/dont_group_matches_in_legal_file.json",
            is_license_text=is_license_text,
            is_legal=is_legal,
        )
        assert len(list(issues)) == 1
        

    def test_group_license_matches_by_location_and_analyze(self):
        # TODO: Add Explanation for all creation of test Files from scancode scan results
        test_file = self.get_test_loc("group_matches_by_location_analyze.json")
        expected_file = self.get_test_loc(
            "group_matches_by_location_analyze_result.json"
        )
        file_scan_result = load_json(test_file)
        expected = load_json(expected_file)
        matched_licences = LicenseMatch.from_files_licenses(
            file_scan_result["licenses"]
        )
        is_license_text = file_scan_result["is_license_text"]
        is_legal = file_scan_result["is_legal"]
        ars = analyzer.LicenseDetectionIssue.from_license_matches(
            license_matches=matched_licences,
            path="path/to/group_matches_by_location_analyze_result.json",
            is_license_text=is_license_text,
            is_legal=is_legal,
        )
        results = [ar.to_dict(is_summary=False) for ar in ars]
        assert results == expected

def load_license_matches_from_json(json_file):
    license_matches = load_json(json_file)
    license_matches = LicenseMatch.from_files_licenses(license_matches)
    return license_matches
