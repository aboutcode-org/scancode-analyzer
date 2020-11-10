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

import numpy as np
import pandas as pd
import os

from commoncode.testcase import FileBasedTesting

from results_analyze.divide_cases import DivideCases, CraftRules
from tests.load_test_data import TestDataIO


class TestDivideCases(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/')

    def test_initialize_dataframe(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-test-dfs-store.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'main_rule_df')
        expected_columns = ['query_coverage_diff',
                            'score_coverage_based_groups',
                            'mask_unique',
                            'match_group_number',
                            'match_class']

        assert dataframe.shape[1] == 36

        divide_cases.initialize_dataframe_rows(dataframe)
        last_five_columns = list(dataframe.columns[-5:].values)

        assert dataframe.shape[1] == 41
        assert expected_columns == last_five_columns

    def test_get_possible_false_positives(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-test-dfs-store.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'main_rule_df')

        divide_cases.initialize_dataframe_rows(dataframe)
        divide_cases.get_possible_false_positives(dataframe)

        assert dataframe["match_class"].value_counts()[5] == 21
        expected_false_positives = ['\tUpdate to GPLv3.',
                                    '\tUpdate to GPLv3.',
                                    '2?ZpL',
                                    ' * Licensed under LGPL2',
                                    'License: LGPLv2 with exceptions',
                                    'LGPL2 / GPL2 at your choice.',
                                    'LGPL2 / GPL2 at your choice.',
                                    '\t(C) Copyright 2010-2011 Andy Green <andy@warmcat.com> licensed under LGPL2.1',
                                    '\t(C) Copyright 2010-2011 Andy Green <andy@warmcat.com> licensed under LGPL2.1',
                                    '\tlwsl_notice("lwsws libwebsockets web server - license CC0 + LGPL2.1 ");',
                                    ' * of libwebsockets; this version is under LGPL2.1 + SLE like the rest of lws',
                                    ' * Licensed under LGPL2',
                                    ' * This version is LGPL2.1+SLE like the rest of libwebsockets and is',
                                    '\t\t\t.base\t= S5PC100_GPL1(0),',
                                    '\t\t\t.label\t= "GPL1",',
                                    '\t\t\t.base\t= S5PC100_GPL2(0),',
                                    '\t\t\t.label\t= "GPL2",',
                                    '\t\t\t.base\t= S5PC100_GPL3(0),',
                                    '\t\t\t.label\t= "GPL3",',
                                    "M5<E*)29-'F/GPL3^I2>(CAQ&G**)ZG?>_-UPRHTQ#/'F44=0N5S,^<VE((]S",
                                    '* Changed the license to GPLv3.']

        assert expected_false_positives == list(dataframe.query("match_class == 5")["matched_text"].values)

    def test_get_incorrect_scan_cases(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'dataframe')

        divide_cases.get_incorrect_scan_cases(dataframe)

        expected_case_counts = [6712, 2747, 336]

        assert expected_case_counts == list(dataframe["score_coverage_based_groups"].value_counts().values)

    def test_set_unique_cases_files(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-score-based-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'dataframe')

        divide_cases.set_unique_cases_files(dataframe)

        expected_unique_counts = [8642, 1153]

        assert expected_unique_counts == list(dataframe["mask_unique"].value_counts().values)

    def test_group_matches_by_location_and_class(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-score-based-unique-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'dataframe')

        divide_cases.group_matches_by_location_and_class(dataframe)

        expected_location_group_numbers = [8698, 1023, 39, 15, 8, 5, 4, 2, 1]
        expected_match_class_numbers = [8684, 648, 227, 208, 14, 14]

        assert expected_location_group_numbers == list(dataframe["match_group_number"].value_counts().values)
        assert expected_match_class_numbers == list(dataframe["match_class"].value_counts().values)

    def test_get_unique_cases_mask(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-select-unique-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rule_df')

        expected_mask = [True, True, False, False, True, True, True, False, False, False, False, False, False, False,
                         False, False, False, False, False, False, False, False, False, False, False, False, False,
                         False, False]

        id_coverage_df = dataframe.loc[:, ["identifier", "match_coverage"]]
        mask = divide_cases.get_unique_cases_mask(id_coverage_df)

        assert expected_mask == list(mask.values[:, 1])

    def test_get_id_match_cov_tuples_apply(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-select-unique-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rule_df')

        id_coverage_df = dataframe.loc[:, ["identifier", "match_coverage"]]
        file_level_id_match_cov = id_coverage_df.groupby(level="file_sha1").apply(divide_cases.get_id_match_cov_tuples)

        assert file_level_id_match_cov[0] == file_level_id_match_cov[1]
        assert file_level_id_match_cov[0] != file_level_id_match_cov[2]
        assert file_level_id_match_cov.index.name == 'file_sha1'

    def test_get_id_match_cov_tuples(self):
        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-select-unique-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rule_df')

        id_coverage_df = dataframe.loc[dataframe.index[0:2], ["identifier", "match_coverage"]]

        file_tuple = divide_cases.get_id_match_cov_tuples(id_coverage_df)
        assert isinstance(file_tuple, tuple)

    def test_group_by_location(self):

        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-test-dfs-store.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rules_df')

        divide_cases.divide_cases_in_groups(dataframe)

        test_group_location_example_files = ("Issues/1918-ntp-4.2.6/genshell.c",
                                             "Issues/1910-cmake-3.4.1/cmCommandArgumentParser.cxx")
        test_group_location_columns = ["path", "start_line", "end_line", "match_group_number"]

        test_group_location = dataframe.loc[dataframe["path"].str.startswith(test_group_location_example_files),
                                            test_group_location_columns]

        expected_group_locations = [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 2, 3, 3, 3, 3]

        assert expected_group_locations == list(test_group_location["match_group_number"].values)

    def test_group_by_license_class(self):

        divide_cases = DivideCases()
        test_file = self.get_test_loc('divide-cases/cases-test-dfs-store.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rules_df')

        divide_cases.divide_cases_in_groups(dataframe)

        license_class_grouping_example_files = ("Issues/1927-u-boot-2010.06-4xx_pci.c",
                                                "Issues/1930-which-2.20-getopt.c", "Issues/1912-libtool-2.2.10-argz.c",
                                                "Issues/1920-socat-2.0.0/hostan.c")

        license_class_grouping_columns = ["path", "matched_text", "match_group_number", "is_license_text_lic",
                                          "is_license_notice", "is_license_tag", "is_license_reference",
                                          "match_group_number", "score", "match_class"]

        license_class_example_dataframe = dataframe.loc[
                                          dataframe["path"].str.startswith(license_class_grouping_example_files),
                                          license_class_grouping_columns]

        expected_license_class_values = [2.0, 2.0, 4.0, 4.0, 4.0, 4.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0,
                                         1.0, 1.0]

        assert expected_license_class_values == list(license_class_example_dataframe["match_class"].values)


class TestCraftRules(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/')

    def test_get_rules_by_group(self):

        craft_rules = CraftRules()

        test_file = self.get_test_loc('craft-rules/cases-grouped-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rule_df')

        test_file = self.get_test_loc('craft-rules/rules-generated.txt')
        list_strings = TestDataIO.load_list_from_txt(test_file)

        test_craft_rule_files = ("Issues/1918-ntp-4.2.6/genshell.c",)

        test_craft_rule_dataframe = dataframe.loc[dataframe["path"].str.startswith(test_craft_rule_files), :]

        crafted_rules_single_file = craft_rules.get_rules_by_group(test_craft_rule_dataframe)

        assert list_strings == list(crafted_rules_single_file["rule_text"].values)

    def test_craft_rules_by_group(self):

        craft_rules = CraftRules()

        test_file = self.get_test_loc('divide-cases/cases-test-group-location-dataframe.h5')
        dataframe = TestDataIO.load_dataframe_from_hdf5(test_file, 'before_rule_df')

        test_file = self.get_test_loc('craft-rules/rules-generated-multiple-file.txt')
        list_strings = TestDataIO.load_list_from_txt(test_file)

        crafted_rules_multiple_files = craft_rules.craft_rules_by_group(dataframe)

        assert list_strings == list(crafted_rules_multiple_files["rule_text"].values)
