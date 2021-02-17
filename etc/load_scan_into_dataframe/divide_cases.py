#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

# All values of match_coverage less than this value is taken as incorrect scans
MATCH_COVERAGE_THR = 100

# How many Lines in between has to be present for two matches being of a different group
# (i.e. and therefore, different rule)
LINES_THRESHOLD = 4


class DivideCases:

    def __init__(self):
        """
        Constructor for DivideCases, initializes some lists of Scan Attributes.
        """

        # Boolean Column Fields which has License Class Information
        self.license_class_bools = ["is_license_text_lic", "is_license_notice", "is_license_tag",
                                    "is_license_reference"]

        # Rule Attributes that are relevant in Rule Creation/Review
        self.craft_rule_fields = ["path", "key", "matched_length", "start_line", "end_line", "matched_text",
                                  "match_class"]

    @staticmethod
    def get_values_low_match_coverages_or_score(df):
        """
        There are two cases where scans are likely to be wrong and needs a seperate Rule:-
        1. Low Match Coverage in one of the Matches in a File/Location
        2. `score != match_coverage * rule_relevance` because even though the rule is entirely matched,
        there's some extra words in the `matched_text`

        :param df : pd.DataFrame
            File wise DataFrame, i.e. No of Rows is Number of matches in a File
        :return mask_series : pd.Series
            An Array of Values, same for all Rows, one for each match in `df`
        """

        # If any of the matches has non-perfect `match_coverage` (i.e. case 1 in docstring)
        low_coverage_mask = df["match_coverage"] < MATCH_COVERAGE_THR
        is_low_coverage = low_coverage_mask.any()

        # If any of the matches has extra words (i.e. case 2 in docstring)
        extra_words_mask = df["query_coverage_diff"] > 0
        is_extra_words = extra_words_mask.any()

        # Assign Values according to Case respectively, and 0 if correct license Scan
        if is_low_coverage:
            value = 1
        elif is_extra_words:
            value = 2
        else:
            value = 0

        # All matches in this location has the same value, because if one match has non-perfect `match_coverage`,
        # all the other matches, i.e. other fragments will be required to craft the Rule.
        mask_series = pd.Series(value, index=np.arange(df.shape[0]))

        return mask_series

    @staticmethod
    def select_2_aho_3_seq_scans(dataframe):
        """
        Only select `matcher` values 2 (`2-aho`) and 3 (`3-seq`) because other values, 1 (`1-hash) and 4 (`4-spdx-id`)
        means that there was an exact match. We only need the incorrect matches, which are present in the
        first two cases only.

        :param dataframe: pd.DataFrame
        :return: dataframe.query(): pd.DataFrame
            Return rows of `dataframe` where the query is True
        """
        return dataframe.query("matcher == 2 and matcher == 3")

    def get_incorrect_scan_cases(self, all_scans_df):
        """
        Combines the two functions `get_values_low_match_coverages_or_score` and `select_2_aho_3_seq_scans` to select
        all incorrect scans. `select_2_aho_3_seq_scans` is an initial faster cleaning step,
        and `get_values_low_match_coverages_or_score`

        :param all_scans_df: pd.DataFrame
        :return: all_incorrect_scans_df: pd.DataFrame
            Return rows of `all_scans_df` where there are Incorrect Scans.
        """

        # Adding column `query_coverage_diff` with the difference between `match_coverage * rule_relevance` and `score`
        # if this is positive, there are extra words
        all_scans_df["query_coverage_diff"] = ((all_scans_df["match_coverage"] * all_scans_df["rule_relevance"]) / 100
                                               - all_scans_df["score"]).values

        # Select only scans with matcher value `2-aho` and `3-seq` i.e. remove scans that are surely correct
        scans_2_aho_3_seq = self.select_2_aho_3_seq_scans(all_scans_df)

        # Apply `get_values_low_match_coverages_or_score` File Wise, and results are stacked in mask_values
        mask_values = scans_2_aho_3_seq.groupby(level="file_sha1").apply(self.get_values_low_match_coverages_or_score)
        scans_2_aho_3_seq["score_coverage_based_groups"] = mask_values.values

        # Only Select Files with Low Match Coverage or Matches with Low Score and Extra Words
        all_incorrect_scans_df = scans_2_aho_3_seq.query("score_coverage_based_groups != 0")

        return all_incorrect_scans_df

    @staticmethod
    def get_id_match_cov_tuples(df):
        """
        Convert a Two Row DataFrame having "identifier" and "match_coverage" to list of tuples
        This is to easily determine unique cases

        :param df: pd.DataFrame
        :return list_tuples: list
            List of Tuples, pre File
        """
        list_tuples = tuple(df.itertuples(index=False, name=None))

        return list_tuples

    def get_unique_cases_files(self, non_unique_df):
        """
        In a Project, a lot of License Texts/Notices/Referances/Tags are reused, so if all of them are detected wrongly,
        We need only one unique instance of those cases, to craft a Rule.

        :param non_unique_df: pd.DataFrame
            DataFrame with all cases
        :return non_unique_df.query(): pd.DataFrame
            Only those rows of DataFrame which are unique cases i.e. where the query is True
        """

        # Data Frame with only "identifier" and "match_coverage" columns. A set of these two would ideally be unique
        # for each unique case
        id_coverage_df = non_unique_df.loc[:, ["identifier", "match_coverage"]]

        # Apply `get_id_match_cov_tuples` to every File
        # `file_level_id_match_cov` is a Series, one row for every File, and containing a List Of Tuples per File
        file_level_id_match_cov = id_coverage_df.groupby(level="file_sha1").apply(self.get_id_match_cov_tuples)

        # Create a DataFrame for Efficient removing of duplicates
        file_tuples = pd.DataFrame(file_level_id_match_cov, columns=["tuples"])

        # Only Keep Unique Tuples
        series_unique = file_tuples["tuples"].drop_duplicates(keep='first')

        # Create a Mask with the Unique Files having Value True
        file_tuples["mask"] = pd.Series(False, index=file_tuples.index)
        file_tuples.loc[series_unique.index, "mask"] = True

        # Keep all Matches of a Unique File, i.e. here a list of Tuples Column is expanded so each tuple will have
        # A new row, with mask value True if the File was marked as a Unique File
        mask_df = file_tuples.explode("tuples")
        non_unique_df.loc[:, ["mask_unique"]] = mask_df["mask"].values

        return non_unique_df.query("mask_unique == True")

    @staticmethod
    def get_match_class(df):
        """
        For a Group of Matches, predict their License Class Type.
        Can be License Text/Notice/Tag/Reference. [This order is in their order of importance]
        Usually if in a group has a match with a higher importance (say, license notice) and several matches of
        lower importance (say license references), then it's likely that the original text is of that former class,
        the higher importance class (i.e. license notice).

        :param df: pd.DataFrame
            Has these four Columns -> DivideCases.license_class_bools
        :return:
        """
        # Create Series with same number of Rows as `df` DataFrame
        match_class_series = pd.Series(np.nan, index=np.arange(df.shape[0]))

        # Performs Columns wise Addition of Boolean Columns
        counts = df.sum()

        # Fills the Series with Values according to their Importance Order
        if counts["is_license_text_lic"]:
            match_class_series.fillna(1, inplace=True)
        elif counts["is_license_notice"]:
            match_class_series.fillna(2, inplace=True)
        elif counts["is_license_tag"]:
            match_class_series.fillna(3, inplace=True)
        elif counts["is_license_reference"]:
            match_class_series.fillna(4, inplace=True)

        return match_class_series

    def get_groups_by_location_and_class(self, df):
        """
        Group Matches by Location, if overlapping/distance between them lower than a threshold, and then for each group
        determine their license class, by using function `get_match_class`
        This is applied by File, i.e. `df` has information of one file.

        :param df: pd.DataFrame
            DataFrame with Each Row being a match in that File
        :return grouped_df: pd.DataFrame
            With two columns 'match_group_number' & 'match_class', same number of rows as `df`, i.e. one row per match.
        """

        # Number of Rows in `df`
        num_matches_file = df.shape[0]

        # Initialize Series Arrays where Location wise Group and License Class Information will be entered
        match_class_series = pd.Series(0, index=np.arange(num_matches_file))
        group_number_series = pd.Series(0, index=np.arange(num_matches_file))

        # Initialize Numerical Indexing for easier Slicing of Rows (i.e. selecting a group of contagious Rows)
        df.index = pd.RangeIndex(start=0, stop=num_matches_file)

        # Initialize Start/End counters for both lines numbers and their numerical Index values for the current match
        start_line_present_match, end_line_present_match = list(df.loc[0, ["start_line", "end_line"]].values)
        start_line_idx, end_line_idx = [0, 0]

        # Initialize present group number counter and the Group No of first match to 1
        group_number_series[0] = present_group_number = 1

        # Loop through the Matches, starting from the second match
        for match in range(1, num_matches_file):

            # Get Start and End line for the current match
            start_line, end_line = list(df.loc[match, ["start_line", "end_line"]].values)

            # If present match falls in the present group
            if start_line <= (end_line_present_match + LINES_THRESHOLD):

                # Mark this match as under the present group and extend group end Index
                group_number_series[match] = present_group_number
                end_line_idx = match

                # If `end_line` outside current line Boundaries, then Update Boundaries
                if end_line > end_line_present_match:
                    end_line_present_match = end_line

            # If present match doesn't fall in the present group
            # i.e. the start_line is outside threshold
            elif start_line > (end_line_present_match + LINES_THRESHOLD):

                # Increase group number, and mark this match as in a new group
                present_group_number += 1
                group_number_series[match] = present_group_number

                # Get License Class for the previous Group of Matches and Update to the corresponding rows of
                # match_class_series Series
                match_class_series[start_line_idx:end_line_idx + 1] = self.get_match_class(
                    df.loc[start_line_idx:end_line_idx, self.license_class_bools])

                # Update Group Index to point to the current group
                start_line_idx, end_line_idx = [match, match]

                # Update Line Boundaries
                end_line_present_match = end_line

        # Get License Class for the previous Group of Matches and Update `match_class_series` for the
        # Last Group of matches
        match_class_series[start_line_idx:end_line_idx + 1] = self.get_match_class(
            df.loc[start_line_idx:end_line_idx, self.license_class_bools])

        # Create a DataFrame with the columns as the Group and License Class information, with the Series Arrays
        grouped_df = pd.DataFrame({'match_group_number': group_number_series, 'match_class': match_class_series})

        return grouped_df

    def group_matches_by_location_and_class(self, dataframe):
        """
        Apply `get_groups_by_location_and_class` to Every File, to group them by Location and then determine the
        type of License of those particular groups.

        :param dataframe: pd.DataFrame
        :return dataframe: pd.DataFrame
            Same instance of DataFrame which was the input, With two more columns `match_group_number` and `match_class`
        """
        # Stacks output DataFrames from all Files into One DataFrame `grouped_by_location_class`
        grouped_by_location_class = dataframe.groupby(level="file_sha1").apply(self.get_groups_by_location_and_class)

        # Add Group by Location and License Type information to main Dataframe
        dataframe["match_group_number"] = grouped_by_location_class["match_group_number"].values
        dataframe["match_class"] = grouped_by_location_class["match_class"].values

        return dataframe

    @staticmethod
    def merge_string_without_overlap(s1, s2):
        """
        Merge two Strings that doesn't have any common substring.

        :param s1: string
        :param s2: string
        :return: string
            Merged String
        """
        return s1 + "\n" + s2

    @staticmethod
    def merge_string_with_overlap(s1, s2):
        """
        Merge two Strings that has a common substring.

        :param s1: string
        :param s2: string
        :return: string
            Merged String
        """
        i = 0
        while not s2.startswith(s1[i:]):
            i += 1
        return s1[:i] + s2

    @staticmethod
    def predict_key(df):
        """
        Return the License Key of the match with the highest "matched_length".
        This cannot always predict the correct license key, but is a reasonable prediction which comes true in
        most cases.

        :param df:
        :return: string
        """
        return df.iloc[df["matched_length"].argmax(), :]["key"]

    def craft_rule_text(self, df, group_number):
        """
        Craft Rule from a group of Matches.

        :param df: pd.DataFrame
            Rows are Matches from the same location wise group.
        :param group_number:
        :return rule_df:
        """

        # No of matches in this group
        num_matches = df.shape[0]

        string_start_line, string_end_line = list(df.loc[df.index[0], ["start_line", "end_line"]].values)
        rule_text = df.loc[df.index[0], "matched_text"]

        for match in range(1, num_matches):

            # Gets Start/End counters lines numbers and the `matched_text` for the current match
            present_start_line, present_end_line, present_text = list(
                df.loc[df.index[match], ["start_line", "end_line", "matched_text"]].values)

            # If String Bounderies Overlap
            if string_end_line == present_start_line:

                rule_text = self.merge_string_with_overlap(rule_text, present_text)
                string_end_line = present_end_line

            # Boundary doesn't overlap but just beside
            elif string_end_line < present_start_line:

                rule_text = self.merge_string_without_overlap(rule_text, present_text)
                string_end_line = present_end_line

            # Deep Overlaps (Of more than one lines)
            elif string_end_line > present_start_line:

                if string_end_line < present_end_line:
                    rule_text = self.merge_string_with_overlap(rule_text, present_text)
                    string_end_line = present_end_line

        # Predict Key of the crafted Rule based on the keys of the fragment matches
        key_prediction = self.predict_key(df.loc[:, ["key", "matched_length"]])
        path, rule_class = list(df.loc[df.index[0], ["path", "match_class"]].values)

        # Creates a Single Row DataFrame with the Crafted Rule Text and other Attributes
        rule_df = pd.DataFrame(columns=list(["path", "key", "rule_class", "start_line", "end_line", "rule_text"]))
        rule_df.loc[group_number] = [path, key_prediction, rule_class, string_start_line, string_end_line, rule_text]

        return rule_df

    def get_rules_by_group(self, df):
        """
        We already have Group of  Matches by Location, and this Function crafts Rules out of all these, for each
        of these groups, in a File.

        :param df: pd.DataFrame
            DataFrame with Each Row being a match in that File .
        :return all_rules_file_df: pd.DataFrame
            All Generated Rules From a File
        """

        # Number of Rows in `df`
        num_matches_file = df.shape[0]

        # Initialize Numerical Indexing for easier Slicing of Rows
        df.index = pd.RangeIndex(start=0, stop=num_matches_file)

        # Initialize Start/End counters having numerical Index values for the current match
        start_group_idx, end_group_idx = [0, 0]

        # Initialize present group number counter
        present_group_number = 1

        # Initialize List that will have all Rule DataFrames
        rule_df_list = []

        # Loop through the Matches, starting from the second match
        for match in range(1, num_matches_file):

            # Get Group Number for the current match
            match_group_number = df.loc[match, "match_group_number"]

            # If Current Match in the Next Group
            if match_group_number > present_group_number:

                # Craft a Rule with all the matches in the previous Group
                rule_df = self.craft_rule_text(df.loc[start_group_idx:end_group_idx, self.craft_rule_fields],
                                               present_group_number)
                rule_df_list.append(rule_df)

                present_group_number += 1

                # Update Both Group Indexes
                start_group_idx, end_group_idx = [match, match]

            # If Current Match in the Current Group
            else:

                # Update End Index to extend to current match
                end_group_idx = match

        # Get License Rule for the Last Group of Matches
        rule_df = self.craft_rule_text(df.loc[start_group_idx:end_group_idx, self.craft_rule_fields],
                                       present_group_number)
        rule_df_list.append(rule_df)

        # Concat all Rule DataFrames in the List into one DataFrame
        all_rules_file_df = pd.concat(rule_df_list)

        return all_rules_file_df

    def craft_rules_by_group(self, df):
        """
        Apply `get_rules_by_group` to matches in each Files, to craft rules.

        :param df:
        :return generated_rules:
        """
        generated_rules = df.groupby(level="file_sha1").apply(self.get_rules_by_group)

        return generated_rules

    @staticmethod
    def get_possible_false_positives(df):
        """
        Separate and return cases which could be False Positives.
        They are License Tags and most of them are erroneously matched with one-word rules.

        :param df:
        :return df.query():
            Rows from `df` which has possible False Positive Cases
        """
        return df.query("is_license_tag == True and rule_length == 1")

    def divide_cases(self, dataframe):
        """
        Separate and Group Wrong License Detections.

        :param dataframe: pd.DataFrame
        :return all_dataframes: list
            List of Separate Grouped DataFrames
        """
        possible_false_positives_df = self.get_possible_false_positives(dataframe)

        incorrect_scans_df = self.get_incorrect_scan_cases(dataframe)

        unique_incorrect_scans_df = self.get_unique_cases_files(incorrect_scans_df)

        grouped_df = self.group_matches_by_location_and_class(unique_incorrect_scans_df)

        lic_text_df = grouped_df.query("is_license_text_file == True or is_legal == True or match_class == 1")
        lic_tag_df = grouped_df.query("match_class == 3")
        lic_notice_df = grouped_df.query("match_class == 2")
        lic_ref_df = grouped_df.query("match_class == 4")

        all_dataframes = [lic_text_df, lic_tag_df, lic_notice_df, lic_ref_df, possible_false_positives_df]

        return all_dataframes
