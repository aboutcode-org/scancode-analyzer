#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
from collections import Counter

from licensedcode.tokenize import query_tokenizer

# All values of match_coverage less than this value are taken as
# `near-perfect-match-coverage` cases
NEAR_PERFECT_MATCH_COVERAGE_THR = 100

# Values of match_coverage less than this are taken as `imperfect-match-coverage` cases
IMPERFECT_MATCH_COVERAGE_THR = 95

# How many Lines in between has to be present for two matches being of a different group
# (i.e. and therefore, different rule)
LINES_THRESHOLD = 4

# Threshold Values of start line and rule length for a match to likely be a false positive
# (more than the start_line threshold and less than the rule_length threshold)
FALSE_POSITIVE_START_LINE_THRESHOLD = 1000
FALSE_POSITIVE_RULE_LENGTH_THRESHOLD = 3

# Whether to Use the NLP BERT Models
USE_LICENSE_CASE_BERT_MODEL = False
USE_FALSE_POSITIVE_BERT_MODEL = False

ISSUE_CASES_VERSION = 0.1


ISSUE_CATEGORIES = {
    "imperfect-match-coverage": (
        "The license detection is inconclusive with high confidence, because only "
        "a small part of the rule text is matched."
    ),
    "near-perfect-match-coverage": (
        "The license detection is conclusive with a medium confidence because "
        "because most, but not all of the rule text is matched."
    ),
    "extra-words": (
        "The license detection is conclusive with high confidence because all the "
        "rule text is matched, but some unknown extra words have been inserted in "
        "the text."
    ),
    "false-positive": (
        "The license detection is inconclusive, and is unlikely to be about a "
        "license as a piece of code/text is detected.",
    ),
    "unknown-match": (
        "The license detection is inconclusive, as the license matches have "
        "been matched to rules having unknown as their license key"
    ),
}


@attr.s
class IssueType:
    ANALYSIS_CONFIDENCES = {
        "high": "High confidence",
        "medium": "Medium confidence",
        "low": "Low confidence",
    }

    classification_id = attr.ib(type=str)
    classification_description = attr.ib(type=str)
    analysis_confidence = attr.ib(
        type=str, validator=attr.validators.in_(ANALYSIS_CONFIDENCES)
    )

    is_license_text = attr.ib(default=False)
    is_license_notice = attr.ib(default=False)
    is_license_tag = attr.ib(default=False)
    is_license_reference = attr.ib(default=False)
    is_license_intro = attr.ib(default=False)

    is_suggested_matched_text_complete = attr.ib(default=True)


ISSUE_TYPES_BY_CLASSIFICATION = {
    "text-legal-lic-files": IssueType(
        is_license_text=True,
        classification_id="text-legal-lic-files",
        classification_description=(
            "The matched text is present in a file whose name is a known "
            "legal filename."
        ),
        analysis_confidence="high",
        is_suggested_matched_text_complete=False,
    ),
    "text-non-legal-lic-files": IssueType(
        is_license_text=True,
        classification_id="text-non-legal-lic-files",
        classification_description=(
            "The matched license text is present in a file whose name is not "
            "a known legal filename."
        ),
        analysis_confidence="medium",
        is_suggested_matched_text_complete=False,
    ),
    "text-lic-text-fragments": IssueType(
        is_license_text=True,
        classification_id="text-lic-text-fragments",
        classification_description=(
            "Only parts of a larger license text are detected."
        ),
        analysis_confidence="low",
        is_suggested_matched_text_complete=False,
    ),
    "notice-and-or-with-notice": IssueType(
        is_license_notice=True,
        classification_id="notice-and-or-with-notice",
        classification_description=(
            "A notice with a complex license expression "
            "(i.e. exceptions, choices or combinations)."
        ),
        analysis_confidence="medium",
    ),
    "notice-single-key-notice": IssueType(
        is_license_notice=True,
        classification_id="notice-single-key-notice",
        classification_description="A notice with a single license.",
        analysis_confidence="high",
    ),
    "notice-has-unknown-match": IssueType(
        is_license_notice=True,
        classification_id="notice-has-unknown-match",
        classification_description=(
            "License notices with unknown licenses detected."
        ),
        analysis_confidence="medium",
    ),
    "notice-false-positive": IssueType(
        is_license_notice=True,
        classification_id="notice-has-unknown-match",
        classification_description=(
            "A piece of code/text is incorrectly detected as a license."
        ),
        analysis_confidence="medium",
    ),
    "tag-tag-coverage": IssueType(
        is_license_tag=True,
        classification_id="tag-tag-coverage",
        classification_description="A part of a license tag is detected",
        analysis_confidence="high",
    ),
    "tag-other-tag-structures": IssueType(
        is_license_tag=True,
        classification_id="tag-other-tag-structures",
        classification_description=(
            "A new/common structure of tags are detected with scope for being "
            "handled differently."
        ),
        analysis_confidence="high",
    ),
    "tag-false-positive": IssueType(
        is_license_tag=True,
        classification_id="tag-other-tag-structures",
        classification_description=(
            "A piece of code/text is incorrectly detected as a license."
        ),
        analysis_confidence="medium",
    ),
    # `reference` sub-cases
    "reference-lead-in-or-unknown-refs": IssueType(
        is_license_reference=True,
        classification_id="reference-lead-in-or-unknown-refs",
        classification_description=(
            "Lead-ins to known license references are detected."
        ),
        analysis_confidence="medium",
    ),
    "reference-low-coverage-refs": IssueType(
        is_license_reference=True,
        classification_id="reference-low-coverage-refs",
        classification_description="License references with a incomplete match.",
        analysis_confidence="medium",
    ),
    "reference-to-local-file": IssueType(
        is_license_reference=True,
        classification_id="reference-to-local-file",
        classification_description=(
            "Matched to an unknown rule as the license information is present in "
            "another file, which is referred to in this matched piece of text."
        ),
        analysis_confidence="high",
    ),
    "reference-false-positive": IssueType(
        is_license_reference=True,
        classification_id="reference-false-positive",
        classification_description=(
            "A piece of code/text is incorrectly detected as a license."
        ),
        analysis_confidence="medium",
    ),
    "intro-unknown-match": IssueType(
        is_license_reference=True,
        classification_id="intro-unknown-match",
        classification_description=(
            "A piece of common introduction to a license text/notice/reference is "
            "detected."
        ),
        analysis_confidence="medium",
    ),
}


@attr.s
class SuggestedLicenseMatch:
    """
    After analysis of a license detection issue, an alternate license detection is
    suggested which attempts to rectify the issues.
    """
    license_expression = attr.ib(type=str)
    matched_text = attr.ib(type=str)


@attr.s
class FileRegion:
    """
    A file has one or more file-regions, which are separate regions of the file
    containing some license information (separated by code/text/others in between),
    and identified by a start line and an end line.
    """
    path = attr.ib(type=str)
    start_line = attr.ib(type=int)
    end_line = attr.ib(type=int)


@attr.s
class LicenseDetectionIssue:
    """
    An LicenseDetectionIssue object corresponds to a license detection issue for a
    file-region, containing one/multiple license matches.
    A file has one or more file-regions, which are separate regions of the file
    containing some license information (separated by code/text/others in between),
    and identified by a start line and an end line.
    """

    issue_category = attr.ib(
        type=str, validator=attr.validators.in_(ISSUE_CATEGORIES))
    issue_description = attr.ib(type=str)

    issue_type = attr.ib()

    suggested_license = attr.ib()
    original_licenses = attr.ib()

    file_regions = attr.ib(default=attr.Factory(list))

    def to_dict(self, is_summary=True):
        if is_summary:
            return attr.asdict(
                self, filter=lambda attr, value: attr.name not in [
                    "file_regions"],
            )
        else:
            return attr.asdict(
                self, filter=lambda attr, value: attr.name not in ["path"],
            )

    @property
    def identifier(self):
        """
        This is an identifier for a issue, based on it's underlying license matches.
        """
        data = []
        for license_match in self.original_licenses:
            identifier = (license_match.rule_identifier,
                          license_match.match_coverage,)
            data.append(identifier)

        return tuple(data)

    @property
    def identifier_for_unknown_intro(self):
        """
        This is an identifier for a issue, which is an unknown license intro,
        based on it's underlying license matches.
        """
        data = []
        for license_match in self.original_licenses:
            tokenized_matched_text = tuple(
                query_tokenizer(license_match.matched_text))
            identifier = (
                license_match.rule_identifier,
                license_match.match_coverage,
                tokenized_matched_text,
            )
            data.append(identifier)

        return tuple(data)

    @staticmethod
    def format_analysis_result(issue_category, issue_type, license_matches, path):
        """
        Format the analysis result to generate an LicenseDetectionIssue object for
        this license detection issue.

        :param issue_category: str
            One of ISSUE_CATEGORIES.
        :param issue_type: str
            One of ISSUE_TYPES_BY_CLASSIFICATION.
        :param license_matches: list
            All matches for a license detection issue (for a file-region), each a
            LicenseMatch object.
        :param path: str
            Path of the resource where the license issue exists
        """
        # Don't generate LicenseDetectionIssue objects for correct License Detections.
        if issue_category == "correct-license-detection":
            return None

        start_line, end_line = get_start_end_line(license_matches)
        license_expression, matched_text = get_license_match_suggestion(
            license_matches, issue_category, issue_type
        )

        license_detection_issue = LicenseDetectionIssue(
            issue_category=issue_category,
            issue_description=ISSUE_CATEGORIES[issue_category],
            issue_type=ISSUE_TYPES_BY_CLASSIFICATION[issue_type],
            suggested_license=SuggestedLicenseMatch(
                license_expression=license_expression, matched_text=matched_text
            ),
            original_licenses=license_matches,
            file_regions=[FileRegion(
                path=path,
                start_line=start_line,
                end_line=end_line,
            )],
        )

        modify_analysis_confidence(license_detection_issue)

        return license_detection_issue

    @staticmethod
    def from_license_matches(
        license_matches, path=None, is_license_text=False, is_legal=False,
    ):
        """
        Group `license_matches` into file-regions and for each license detection issue,
        return a LicenseDetectionIssue object containing the issue, issue type and
        suggested license match, with the original reported matches.

        :param license_matches: list
            List of LicenseMatch.
        :param path: str
            Path of the resource where the license issue exists
        :param is_license_text: bool
            True if most of a file is license text.
        :param is_legal: bool
            True if the file has a common legal name.
        """
        if not license_matches:
            return []

        if not is_license_text:
            groups_of_license_matches = group_matches(license_matches)
        else:
            groups_of_license_matches = [license_matches]
        return analyze_matches(
            groups_of_license_matches, path, is_license_text, is_legal
        )


def is_correct_detection(license_matches):
    """
    Return True if all the license matches in a file-region are correct
    license detections, as they are either SPDX license tags, or the file content has
    a exact match with a license hash.

    :param license_matches: list
        List of LicenseMatch.
    """
    matchers = (license_match.matcher for license_match in license_matches)
    return all(matcher in ("1-hash", "4-spdx-id") for matcher in matchers)


def is_match_coverage_less_than_threshold(license_matches, threshold):
    """
    Returns True if any of the license matches in a file-region has a `match_coverage`
    value below the threshold.

    :param license_matches: list
        List of LicenseMatch.
    :param threshold: int
        A `match_coverage` threshold value in between 0-100
    """
    coverage_values = (
        license_match.match_coverage for license_match in license_matches
    )
    return any(coverage_value < threshold for coverage_value in coverage_values)


def calculate_query_coverage_coefficient(license_match):
    """
    Calculates a `query_coverage_coefficient` value for that match. For a match:
    1. If this value is 0, i.e. `score`==`match_coverage`*`rule_Relevance`, then
       there are no extra words in that license match.
    2. If this value is a +ve number, i.e. `score`!=`match_coverage`*`rule_Relevance`,
       then there are extra words in that match.

    :param matched_license: LicenseMatch.
    """
    score_coverage_relevance = (
        license_match.match_coverage * license_match.rule_relevance
    ) / 100

    return score_coverage_relevance - license_match.score


def is_extra_words(license_matches):
    """
    Return True if any of the license matches in a file-region has extra words. Having
    extra words means contains a perfect match with a license/rule, but there are some
    extra words in addition to the matched text.

    :param license_matches: list
        List of LicenseMatch.
    """
    match_query_coverage_diff_values = (
        calculate_query_coverage_coefficient(license_match)
        for license_match in license_matches
    )
    return any(
        match_query_coverage_diff_value > 0
        for match_query_coverage_diff_value in match_query_coverage_diff_values
    )


def is_false_positive(license_matches):
    """
    Return True if all of the license matches in a file-region are false positives.
    False Positive occurs when other text/code is falsely matched to a license rule,
    because it matches with a one-word license rule with it's `is_license_tag` value as
    True. Note: Usually if it's a false positive, there's only one match in that region.

    :param license_matches: list
        List of LicenseMatch.
    """
    start_line_region = min(
        license_match.start_line for license_match in license_matches
    )
    match_rule_length_values = [
        license_match.rule_length for license_match in license_matches
    ]

    if start_line_region > FALSE_POSITIVE_START_LINE_THRESHOLD and any(
        match_rule_length_value <= FALSE_POSITIVE_RULE_LENGTH_THRESHOLD
        for match_rule_length_value in match_rule_length_values
    ):
        return True

    match_is_license_tag_flags = (
        license_match.is_license_tag for license_match in license_matches
    )
    return all(
        (is_license_tag_flag and match_rule_length == 1)
        for is_license_tag_flag, match_rule_length in zip(
            match_is_license_tag_flags, match_rule_length_values
        )
    )


def has_unknown_matches(license_matches):
    """
    Return True if any on the license matches has a license match with an
    `unknown` rule identifier.

    :param license_matches: list
        List of LicenseMatch.
    """
    match_rule_identifiers = (
        license_match.rule_identifier for license_match in license_matches
    )
    match_rule_license_expressions = (
        license_match.license_expression for license_match in license_matches
    )
    return any(
        "unknown" in identifier for identifier in match_rule_identifiers
    ) or any(
        "unknown" in license_expression
        for license_expression in match_rule_license_expressions
    )


def get_analysis_for_region(license_matches):
    """
    Analyse license matches from a file-region, and determine if the license detection
    in that file region is correct or it is wrong/partially-correct/false-positive or
    has extra words.

    :param license_matches: list
        List of LicenseMatch.
    """
    # Case where all matches have `matcher` as `1-hash` or `4-spdx-id`
    if is_correct_detection(license_matches):
        return "correct-license-detection"

    # Case where at least one of the matches have `match_coverage`
    # below IMPERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches, IMPERFECT_MATCH_COVERAGE_THR
    ):
        return "imperfect-match-coverage"

    # Case where at least one of the matches have `match_coverage`
    # below NEAR_PERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches, NEAR_PERFECT_MATCH_COVERAGE_THR
    ):
        return "near-perfect-match-coverage"

    # Case where at least one of the match have extra words
    elif is_extra_words(license_matches):
        return "extra-words"

    # Case where even though the matches have perfect coverage, they have
    # matches with `unknown` rule identifiers
    elif has_unknown_matches(license_matches):
        return "unknown-match"

    # Case where the match is a false positive
    elif is_false_positive(license_matches):
        if not USE_FALSE_POSITIVE_BERT_MODEL:
            return "false-positive"
        else:
            return determine_false_positive_case_using_bert(license_matches)

    # Cases where Match Coverage is a perfect 100 for all matches
    else:
        return "correct-license-detection"


def is_license_case(license_matches, license_case):
    """
    Get the type of license_match_case for a group of license matches in a file-region.

    :param license_matches: list
        List of LicenseMatch.
    :param license_case: string
        One of the 4 boolean flag attributes of a match, i.e. is it text/notice/tag/ref
    """
    match_is_license_case_flags = (
        getattr(license_match, license_case) for license_match in license_matches
    )
    return any(
        match_is_license_case for match_is_license_case in match_is_license_case_flags
    )


def get_issue_rule_type(license_matches, is_license_text, is_legal):
    """
    For a group of matches (with some issue) in a file-region, classify them into
    groups according to their potential license rule type (text/notice/tag/reference).

    :param license_matches: list
        List of LicenseMatch.
    :param is_license_text: bool
    :param is_legal: bool
    """
    # Case where at least one of the matches is matched to a license `text` rule.
    if (
        is_license_text
        or is_legal
        or is_license_case(license_matches, "is_license_text")
    ):
        return "text"

    # Case where at least one of the matches is matched to a license `notice` rule.
    elif is_license_case(license_matches, "is_license_notice"):
        return "notice"

    # Case where at least one of the matches is matched to a license `tag` rule.
    elif is_license_case(license_matches, "is_license_tag"):
        return "tag"

    # Case where at least one of the matches is matched to a license `reference` rule.
    elif is_license_case(license_matches, "is_license_reference"):
        return "reference"

    # Case where the matches are matched to a license `intro` rule.
    elif is_license_case(license_matches, "is_license_intro"):
        return "intro"


def get_license_text_issue_type(is_license_text, is_legal):
    """
    Classifies the license detection issue into one of ISSUE_TYPES_BY_CLASSIFICATION,
    where it is a license text.
    """
    if is_legal:
        if is_license_text:
            return "text-legal-lic-files"
        else:
            return "text-lic-text-fragments"
    else:
        return "text-non-legal-lic-files"


def get_license_notice_issue_type(license_matches, issue_category):
    """
    Classifies the license detection issue into one of ISSUE_TYPES_BY_CLASSIFICATION,
    where it is a license notice.
    """
    license_expression_connectors = ["AND", "OR", "WITH"]

    match_rule_license_expressions = [
        license_match.license_expression for license_match in license_matches
    ]

    if issue_category == "false-positive":
        return "notice-false-positive"
    elif issue_category == "unknown-match":
        return "notice-has-unknown-match"
    elif all(
        any(
            license_expression_connector in license_expression
            for license_expression_connector in license_expression_connectors
        )
        for license_expression in match_rule_license_expressions
    ):
        return "notice-and-or-with-notice"
    elif any(
        "unknown" in license_expression
        for license_expression in match_rule_license_expressions
    ):
        return "notice-has-unknown-match"
    else:
        return "notice-single-key-notice"


def get_license_tag_issue_type(issue_category):
    """
    Classifies the license detection issue into one of ISSUE_TYPES_BY_CLASSIFICATION,
    where it is a license tag.
    """
    if issue_category == "false-positive":
        return "tag-false-positive"
    else:
        return "tag-tag-coverage"


def get_license_reference_issue_type(license_matches, issue_category):
    """
    Classifies the license detection issue into one of ISSUE_TYPES_BY_CLASSIFICATION,
    where it is a license reference.
    """
    match_rule_identifiers = [
        license_match.rule_identifier for license_match in license_matches
    ]

    if issue_category == "false-positive":
        return "reference-false-positive"
    elif any("lead" in identifier for identifier in match_rule_identifiers) or any(
        "unknown" in identifier for identifier in match_rule_identifiers
    ) or issue_category == "unknown-match":
        return "reference-lead-in-or-unknown-refs"
    else:
        return "reference-low-coverage-refs"


def get_issue_type(
    license_matches, is_license_text, is_legal, issue_category, issue_rule_type
):
    """
    Classifies the license detection issue into one of ISSUE_TYPES_BY_CLASSIFICATION
    """
    if issue_rule_type == "text":
        return get_license_text_issue_type(is_license_text, is_legal)
    elif issue_rule_type == "notice":
        return get_license_notice_issue_type(license_matches, issue_category)
    elif issue_rule_type == "tag":
        return get_license_tag_issue_type(issue_category)
    elif issue_rule_type == "reference":
        return get_license_reference_issue_type(license_matches, issue_category)
    elif issue_rule_type == "intro":
        return "intro-unknown-match"


def get_issue_rule_type_using_bert(license_matches):
    raise NotImplementedError


def determine_false_positive_case_using_bert(license_matches):
    raise NotImplementedError


def merge_string_without_overlap(string1, string2):
    """
    Merge two Strings that doesn't have any common substring.
    """
    return string1 + "\n" + string2


def merge_string_with_overlap(string1, string2):
    """
    Merge two Strings that has a common substring.
    """
    idx = 0
    while not string2.startswith(string1[idx:]):
        idx += 1
    return string1[:idx] + string2


def get_start_end_line(license_matches):
    """
    Returns start and end line for a license detection issue, from the
    license match(es).
    """
    start_line = min(
        [license_match.start_line for license_match in license_matches])
    end_line = max(
        [license_match.end_line for license_match in license_matches])
    return start_line, end_line


def predict_license_expression(license_matches):
    """
    Return the best-effort predicted license expression given a list of LicenseMatch
    objects.
    """
    unknown_expressions = ['unknown', 'warranty-disclaimer']

    license_expressions = (
        license_match.license_expression for license_match in license_matches
    )
    known_expressions = [
        le for le in license_expressions if le not in unknown_expressions
    ]
    if not known_expressions:
        return "unknown"

    license_expressions_counts = dict(Counter(known_expressions).most_common())
    highest_count = list(license_expressions_counts.values())[0]

    top_license_expressions = [
        expression
        for expression, count in license_expressions_counts.items()
        if count == highest_count
    ]

    if len(top_license_expressions) == 1:
        return top_license_expressions[0]

    top_license_matches = [
        license_match
        for license_match in license_matches
        if license_match.license_expression in top_license_expressions
    ]

    max_match_length = max([
        license_match.matched_length
        for license_match in top_license_matches
    ])
    license_expression_prediction = next(
        license_match.license_expression
        for license_match in top_license_matches
        if license_match.matched_length is max_match_length
    )
    return license_expression_prediction


def get_license_match_suggestion(license_matches, issue_category, issue_type):
    """
    Suggest a license match rectifying the license detection issue.

    :param license_matches:
        List of LicenseMatch.
    :param issue_category:
        One of LicenseDetectionIssue.ISSUE_CATEGORIES.
    :param issue_type:
        One of LicenseDetectionIssue.ISSUE_TYPES_BY_CLASSIFICATION
    :returns license_expression:
        A complete license expression from all the licenses matches.
    :returns matched_text:
        A complete matched text from all the licenses matches.
    """
    license_expression = None
    matched_text = None

    if issue_category != "correct-license-detection":
        if len(license_matches) == 1:
            [match] = license_matches
            license_expression = match.license_expression
            matched_text = match.matched_text
        else:
            if issue_type == "notice-and-or-with-notice":
                match = license_matches[0]
                license_expression = match.license_expression
                matched_text = match.matched_text
            else:
                license_expression = predict_license_expression(
                    license_matches)
                matched_text = consolidate_matches(license_matches)

    return license_expression, matched_text


def consolidate_matches(license_matches):
    """
    Create a complete matched_text from a group of Matches, which are in the same
    license detection issue, i.e. in the same file-region.
    The license matches are incorrect matches and has fragments of a larger text,
    but, may not contain the entire text even after consolidating.
    """
    matched_text = None
    string_end_line = None
    is_first_group = True

    for license_match in license_matches:
        if is_first_group:
            string_end_line = license_match.end_line
            matched_text = license_match.matched_text
            is_first_group = False
            continue
        else:
            present_start_line = license_match.start_line
            present_end_line = license_match.end_line
            present_text = license_match.matched_text

        # Case: Has a line-overlap
        if string_end_line == present_start_line:
            matched_text = merge_string_with_overlap(
                matched_text, present_text)
            string_end_line = present_end_line

        # Case: Boundary doesn't overlap but just beside
        elif string_end_line < present_start_line:
            matched_text = merge_string_without_overlap(
                matched_text, present_text)
            string_end_line = present_end_line

        # Case: Deep Overlaps (Of more than one lines)
        elif string_end_line > present_start_line:
            if string_end_line < present_end_line:
                matched_text = merge_string_with_overlap(
                    matched_text, present_text)
                string_end_line = present_end_line

    return matched_text


def analyze_region_for_license_scan_issues(license_matches, is_license_text, is_legal):
    """
    On a group of license matches (grouped on the basis of location in file),
    perform steps of analysis to determine if the license match is correct or if it has
    any issues. In case of issues, divide the issues into groups of commonly occurring
    license detection issues.

    :param license_matches: list
        List of LicenseMatch.
    :param is_license_text: bool
    :param is_legal: bool
    :return issue_category: str
        One of LicenseDetectionIssue.ISSUE_CATEGORIES.
    :returns issue_type: str
        One of LicenseDetectionIssue.ISSUE_TYPES_BY_CLASSIFICATION
    """
    issue_category = get_analysis_for_region(license_matches)
    issue_type = None

    # If one of the matches in the file-region has issues, classify the type of issue
    # into further types of issues
    if issue_category != "correct-license-detection":

        if not USE_LICENSE_CASE_BERT_MODEL:
            issue_rule_type = get_issue_rule_type(
                license_matches,
                is_license_text,
                is_legal,
            )
        else:
            issue_rule_type = get_issue_rule_type_using_bert(license_matches)

        issue_type = get_issue_type(
            license_matches,
            is_license_text,
            is_legal,
            issue_category,
            issue_rule_type,
        )

    return issue_category, issue_type


def modify_analysis_confidence(license_detection_issue):
    """
    Modify the analysis confidence to a more precise one from the default confidences
    in LicenseDetectionIssue.ISSUE_TYPES_BY_CLASSIFICATION, by using more analysis
    information.

    :param license_detection_issue:
        A LicenseDetectionIssue object.
    """
    if (
        license_detection_issue.issue_category == "extra-words"
        or license_detection_issue.issue_category == "near-perfect-match-coverage"
    ):
        license_detection_issue.issue_type.analysis_confidence = "high"
    elif (
        license_detection_issue.issue_category == "false-positive"
        or license_detection_issue.issue_category == "unknown-match"
    ):
        license_detection_issue.issue_type.analysis_confidence = "low"


def group_matches(license_matches, lines_threshold=LINES_THRESHOLD):
    """
    Given a list of `matches` yield lists of grouped matches together where each
    group is less than `lines_threshold` apart.
    Each item in `matches` is a ScanCode matched license using the structure
    that is found in the JSON scan results.

    :param license_matches: list
        List of LicenseMatch.
    :param lines_threshold: int
        The maximum space that can exist between two matches for them to be
        considered in the same file-region.
    :returns: list generator
        A list of groups, where each group is a list of matches in the same file-region.
    """
    group_of_license_matches = []
    for license_match in license_matches:
        if not group_of_license_matches:
            group_of_license_matches.append(license_match)
            continue
        previous_match = group_of_license_matches[-1]
        is_in_group = license_match.start_line <= previous_match.end_line + lines_threshold
        if is_in_group:
            group_of_license_matches.append(license_match)
            continue
        else:
            yield group_of_license_matches
            group_of_license_matches = [license_match]

    yield group_of_license_matches


def analyze_matches(groups_of_license_matches, path, is_license_text, is_legal):
    """
    Analyze all license detection issues in a file, for license detection issues.

    :param all_groups_of_license_matches: list generator
        A list of groups, where each group is a list of matches (in a file-region).
    :param path: str
        Path of the resource where the license issue exists
    :param is_license_text: bool
    :param is_legal: bool
    :returns: list generator
        A list of LicenseDetectionIssue objects one for each license detection
        issue.
    """
    for group_of_license_matches in groups_of_license_matches:
        issue_category, issue_type = analyze_region_for_license_scan_issues(
            license_matches=group_of_license_matches,
            is_license_text=is_license_text,
            is_legal=is_legal,
        )
        license_detection_issue = LicenseDetectionIssue.format_analysis_result(
            issue_category, issue_type, group_of_license_matches, path
        )
        if license_detection_issue:
            yield license_detection_issue
