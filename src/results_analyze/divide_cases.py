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

# Raise Error in case of Chained Assignment as that has unpredictable consequences
# Docs - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
pd.options.mode.chained_assignment = 'raise'  # default='warn'

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

        self.license_class_dict = {1: 'license_text',  2: 'license_notice', 3: 'license-tag', 4: 'license-reference'}

    # TODO: Add another threshold and grouping based on stats (near-perfect scores, maybe 85/90 to 100)
    @staticmethod
    def get_values_low_match_coverages_or_score(df):
        """
        There are two cases where scans are likely to be wrong and needs a separate Rule:-
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
    def get_mask_2_aho_3_seq_scans(dataframe):
        """
        Only select `matcher` values 2 (`2-aho`) and 3 (`3-seq`) because other values, 1 (`1-hash) and 4 (`4-spdx-id`)
        means that there was an exact match. We only need the incorrect matches, which are present in the
        first two cases only.

        :param dataframe: pd.DataFrame
        :return: dataframe.query(): pd.DataFrame
            Return rows of `dataframe` where the query is True
        """
        return np.bitwise_or(dataframe.matcher == 2, dataframe.matcher == 3)

    def get_incorrect_scan_cases(self, all_scans_df):
        """
        Combines the two functions `get_values_low_match_coverages_or_score` and `select_2_aho_3_seq_scans` to select
        all incorrect scans. `select_2_aho_3_seq_scans` is an initial faster cleaning step, that removes scans with
        `1-hash` and `4-spdx-id` as matchers. Then `get_values_low_match_coverages_or_score` selects files which
        contain at least one incorrect scan. These incorrect scans are also grouped into two classes, the ones with
        low (<100) match coverage, and the ones where `score != match_coverage * rule_relevance`

        :param all_scans_df: pd.DataFrame
        :return: all_incorrect_scans_df: pd.DataFrame
            Return rows of `all_scans_df` where there are Incorrect Scans.
        """
        # Select only scans with matcher value `2-aho` and `3-seq` i.e. remove scans that are surely correct
        mask_2_aho_3_seq_scans = self.get_mask_2_aho_3_seq_scans(all_scans_df)
        scans_2_aho_3_seq = all_scans_df[mask_2_aho_3_seq_scans]

        # Apply `get_values_low_match_coverages_or_score` File Wise, and results are stacked in mask_values
        mask_values = scans_2_aho_3_seq.groupby(level="file_sha1").apply(self.get_values_low_match_coverages_or_score)
        all_scans_df.loc[mask_2_aho_3_seq_scans, "score_coverage_based_groups"] = mask_values.values

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

    def get_unique_cases_mask(self, non_unique_df):
        """
        In a DataFrame, makes tuples for each file, containing "identifier" and "match_coverage" value pairs, so that
        if any file has the same tuples, they have the same case of license detection inaccuracy.

        :param non_unique_df: pd.DataFrame
            DataFrame with all incorrect cases i.e. where at least one match has an imperfect match coverage
        :return mask_df: pd.DataFrame
            Dataframe with value True on only those rows of DataFrame which are unique cases.
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
        file_tuples.loc[:, "mask"] = pd.Series(False, index=file_tuples.index)
        file_tuples.loc[series_unique.index, "mask"] = True

        # Keep all Matches of a Unique File, i.e. here a list of Tuples Column is expanded so each tuple will have
        # A new row, with mask value True if the File was marked as a Unique File
        mask_df = file_tuples.explode("tuples")

        return mask_df

    def set_unique_cases_files(self, dataframe):
        """
        In a Project, a lot of License Texts/Notices/References/Tags are reused, so if all of them are detected wrongly,
        We need only one unique instance of those cases, to craft a Rule. This function selects only one instance of
        those unique incorrect scans, and discards all other repetitions.

        :param dataframe: pd.DataFrame
            DataFrame with all cases
        """
        mask_incorrect_scans = (dataframe.score_coverage_based_groups != 0)
        incorrect_scans_df = dataframe[mask_incorrect_scans]

        mask_df = self.get_unique_cases_mask(incorrect_scans_df)
        dataframe.loc[mask_incorrect_scans, "mask_unique"] = mask_df["mask"].values

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
        Selects all unique incorrect scans by creating a boolean mask.
        Then applies `get_groups_by_location_and_class` to Every File, to group them by Location and then determine the
        type of License of those particular groups. Then uses the mask to make write the location/license class
        information to the respective DataFrame rows.

        :param dataframe: pd.DataFrame
            Dataframe containing all unique incorrect license detections.
        """
        # Stacks output DataFrames from all Files into One DataFrame `grouped_by_location_class`
        unique_incorrect_scans_mask = np.bitwise_and(dataframe.score_coverage_based_groups != 2, dataframe.mask_unique)
        unique_incorrect_scans_df = dataframe[unique_incorrect_scans_mask]

        location_and_class_groups = unique_incorrect_scans_df.groupby(level="file_sha1").apply(
                                                                                self.get_groups_by_location_and_class)

        # Add Group by Location and License Type information to main Dataframe
        dataframe.loc[unique_incorrect_scans_mask, "match_group_number"] = location_and_class_groups[
                                                                                        "match_group_number"].values
        dataframe.loc[unique_incorrect_scans_mask, "match_class"] = location_and_class_groups["match_class"].values

    @staticmethod
    def get_possible_false_positives(dataframe):
        """
        Separate and mark cases which could be False Positives, in the DataFrame, inplace.
        They are License Tags and most of them are erroneously matched with one-word rules.

        :param dataframe:
            DataFrame containing all the Scan Results.
        """
        possible_false_positives_mask = np.bitwise_and(dataframe.is_license_tag, dataframe.rule_length == 1)
        dataframe.loc[possible_false_positives_mask, "match_class"] = 5

    # TODO: Implement SubClasses in Match Classes
    @staticmethod
    def initialize_dataframe_rows(dataframe):
        """
         Initialize rows in the DataFrame for marking them into different cases. The new rows are:
            - query_coverage_diff
            - score_coverage_based_groups
            - mask_unique
            - match_group_number
            - match_class

         :param dataframe:
             DataFrame containing all the Scan Results.
         """
        # Adding column `query_coverage_diff` with the difference between `match_coverage * rule_relevance` and `score`
        # if this is positive, there are extra words
        dataframe.loc[:, "query_coverage_diff"] = ((dataframe["match_coverage"] * dataframe["rule_relevance"]) / 100
                                            - dataframe["score"]).values

        # initialize row for for group by License Scores
        dataframe.loc[:, "score_coverage_based_groups"] = 0

        # initialize row for Unique/Non-unique (True/False) License Detection Errors
        dataframe.loc[:, "mask_unique"] = False

        # initialize rows for group by Location and License Type information
        dataframe.loc[:, "match_group_number"] = 0
        dataframe.loc[:, "match_class"] = 0

    def divide_cases_in_groups(self, dataframe):
        """
        Separate and Group Wrong License Detections.

        :param dataframe: pd.DataFrame
            DataFrame containing all the Scan Results.
        """
        self.initialize_dataframe_rows(dataframe)

        self.get_possible_false_positives(dataframe)

        self.get_incorrect_scan_cases(dataframe)

        # Only Select Files with Low Match Coverage or Matches with Low Score and Extra Words
        self.set_unique_cases_files(dataframe)

        self.group_matches_by_location_and_class(dataframe)


class CraftRules:

    def __init__(self):

        # Rule Attributes that are relevant in Rule Creation/Review
        self.craft_rule_fields = ["path", "key", "matched_length", "start_line", "end_line", "matched_text",
                                  "match_class"]

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
        Craft Rule from a group of Matches, which are in the same location group.

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

            # If String Boundaries Overlap
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
        Apply `get_rules_by_group` to matches in each File, to craft rules for each location based group, for all files.

        :param df:
        :return generated_rules:
        """
        generated_rules = df.groupby(level="file_sha1").apply(self.get_rules_by_group)

        return generated_rules
