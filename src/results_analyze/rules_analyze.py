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

import yaml
import os
# import itertools
# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from results_analyze.df_file_io import DataFrameFileIO, TestDataIO

# Format in which the Information DataFrames will be stored in hdf5 files
HDF5_STORE_FORMAT = 'fixed'
# Threshold of Words which is used in `Rule.compute_relevance` in `scancode.licensedcode.models.py`
THRESHOLD_COMPUTE_RELEVANCE = 18.0


class LicenseRulesInfo:
    def __init__(self, has_loaded=False):

        self.df_io = DataFrameFileIO()

        self.hdf5_info_dfs = os.path.join(os.path.dirname(__file__), 'data/lic-rule-info/info_dfs.hdf5')

        self.rule_df = None
        self.lic_df = None

        self.key_dict = None
        self.identifier_dict = None
        self.key_df = None
        self.identifier_df = None

        self.inv_identifier_dict = None
        self.inv_key_dict = None

        self.rule_bool_cols = ["is_license_reference", "is_license_text", "is_license_notice", "is_license_tag",
                               "only_known_words", "is_false_positive", "is_negative"]

        if has_loaded:
            self.load_info_from_file()
        else:
            self.lic_folder_path, self.rule_folder_path = self.df_io.load_folder_names()
            self.load_info_from_scancode()

    def load_info_from_file(self):
        """
        Load License and Rule DataFrames and Conversion Dictionary DataFrames from hdf5 files.
        """

        self.rule_df = TestDataIO.load_dataframe_from_hdf5(self.hdf5_info_dfs, "rule_df")
        self.lic_df = TestDataIO.load_dataframe_from_hdf5(self.hdf5_info_dfs, "lic_df")
        self.identifier_df = TestDataIO.load_dataframe_from_hdf5(self.hdf5_info_dfs, "id_df")
        self.key_df = TestDataIO.load_dataframe_from_hdf5(self.hdf5_info_dfs, "key_df")

        self.identifier_dict = self.df_io.df_to_inv_dict(self.identifier_df)
        self.key_dict = self.df_io.df_to_inv_dict(self.key_df)

    def save_info_to_file(self):
        """
        Store License and Rule DataFrames and Conversion Dictionary DataFrames into hdf5 files.
        """

        self.df_io.store_dataframe_to_hdf5(self.rule_df, self.hdf5_info_dfs, "rule",
                                           h5_format=HDF5_STORE_FORMAT, is_append=False)
        self.df_io.store_dataframe_to_hdf5(self.lic_df, self.hdf5_info_dfs, "lic",
                                           h5_format=HDF5_STORE_FORMAT, is_append=False)
        self.df_io.store_dataframe_to_hdf5(self.identifier_df, self.hdf5_info_dfs, "id",
                                           h5_format=HDF5_STORE_FORMAT, is_append=False)
        self.df_io.store_dataframe_to_hdf5(self.key_df, self.hdf5_info_dfs, "key",
                                           h5_format=HDF5_STORE_FORMAT, is_append=False)

    def load_rule_info_from_scancode(self):
        """
        From the scancode Rule Files, at `scancode/src/licensedcode/data/rules/` load all Rule Text and .yml files
        into a DataFrame.

        :return appended_data: pd.DataFrames
            A DataFrame containing all the Scancode Rules Information.
        """

        rule_files_all = []

        for (dirpath, dirnames, filenames) in os.walk(self.rule_folder_path):
            filenames.sort()
            rule_files_all.extend(filenames)

        files_rule = []
        files_yml = []

        for file in rule_files_all:
            if file[-4:] == 'RULE':
                files_rule.append(file)
            elif file[-3:] == 'yml':
                files_yml.append(file)

        os.chdir(self.rule_folder_path)

        assert len(files_rule) == len(files_yml)

        appended_data = []

        for (rule_text, rule_yml) in zip(files_rule, files_yml):
            f_yml = open(rule_yml, 'r')
            f_rule_text = open(rule_text, 'r')

            df = pd.json_normalize(yaml.safe_load(f_yml))
            rule_text_string = f_rule_text.read()
            no_words = len(rule_text_string.split())
            df["Rule_text"] = rule_text_string
            df["num_words"] = no_words

            appended_data.append(df)

        appended_data = pd.concat(appended_data)

        appended_data["rule_name"] = pd.Series(files_rule, index=appended_data.index)
        appended_data.index = pd.RangeIndex(start=1, stop=appended_data.shape[0] + 1)

        return appended_data

    def load_lic_info_from_scancode(self):
        """
        From the scancode License Files, at `scancode/src/licensedcode/data/licenses/` load all License Text and .yml
        files into a DataFrame.

        :return appended_data: pd.DataFrames
            A DataFrame containing all the Scancode License Information.
        """

        lic_files_all = []

        for (dirpath, dirnames, filenames) in os.walk(self.lic_folder_path):
            filenames.sort()
            lic_files_all.extend(filenames)

        files_notice = []
        files_yml = []

        for file in lic_files_all:
            if file[-7:] == 'LICENSE':
                files_notice.append(file)
            elif file[-3:] == 'yml':
                files_yml.append(file)

        notice_set = set([file_name[:-8] for file_name in files_notice])
        yml_set = set([file_name[:-4] for file_name in files_yml])

        extra_yml_files = [name + '.yml' for name in list(yml_set - (notice_set & yml_set))]
        files_yml_new = [e for e in files_yml if e not in extra_yml_files]

        assert len(files_notice) == len(files_yml_new)

        os.chdir(self.lic_folder_path)

        appended_data_notice = []

        for (notice_text, notice_yml) in zip(files_notice, files_yml_new):
            f_yml = open(notice_yml, 'r')
            f_notice_text = open(notice_text, 'r')

            df = pd.json_normalize(yaml.safe_load(f_yml))
            notice_text_string = f_notice_text.read()
            no_words = len(notice_text_string.split())
            df["Notice_text"] = notice_text_string
            df["Notice_len"] = no_words

            appended_data_notice.append(df)

        appended_data_notice = pd.concat(appended_data_notice)

        appended_data_notice["license_name"] = pd.Series(files_notice, index=appended_data_notice.index)
        appended_data_notice.index = pd.RangeIndex(start=1, stop=appended_data_notice.shape[0] + 1)

        return appended_data_notice

    @staticmethod
    def rule_compute_relevance(rule_df, threshold=THRESHOLD_COMPUTE_RELEVANCE):
        """
        Compute all the Relevance Values of Rules where it isn't given explicitly.

        :param rule_df: pd.DataFrame
            DataFrame with all Rule Information.
        :param threshold: float
            The threshold value, above which rules have a relevance of 100
        """

        rule_df.loc[(rule_df["is_false_positive"] is True) | (rule_df["is_negative"] is True), "relevance"] = 100

        rule_df.loc[rule_df["num_words"] >= threshold, "relevance"] = 100

        relevance_of_one_word = round((1 / threshold) * 100, 2)
        rule_df.loc[rule_df["relevance"].isna(), "relevance"] = rule_df.loc[
                                                    rule_df["relevance"].isna(), "num_words"] * relevance_of_one_word

    @staticmethod
    def rule_compute_min_cov(rule_df):
        """
        Compute all the Minimum Coverage Values of Rules where it isn't given explicitly.

        :param rule_df: pd.DataFrame
            DataFrame with all Rule Information.
        """

        rule_df.loc[rule_df["minimum_coverage"].isna(), "minimum_coverage"] = 0

    @staticmethod
    def lic_compute_min_cov(lic_df):
        """
        Compute all the Minimum Coverage Values of Licenses where it isn't given explicitly.

        :param lic_df: pd.DataFrame
            DataFrame with all License Information.
        """
        lic_df.loc[lic_df["minimum_coverage"].isna(), "minimum_coverage"] = 0

    def modify_lic_rule_info(self, rule_df, lic_df):
        """
        Formats and Modifies Rule/License Information.

        :param rule_df: pd.DataFrame
            DataFrame with all Rules Information.
        :param lic_df: pd.DataFrame
            DataFrame with all License Information.
        """
        # Convert NaN Values in Boolean Columns to False, making it a boolean column, not object
        rule_df.fillna({x: False for x in self.rule_bool_cols}, inplace=True)

        # self.rule_compute_relevance(rule_df)
        # self.rule_compute_min_cov(rule_df)
        # self.lic_compute_min_cov(lic_df)

        self.rule_df = rule_df
        self.lic_df = lic_df

    def construct_identifier_dict(self):
        """
        Construct a String -> Dictionary from Rule and License Information, for Identifiers.
        "identifier" - License or License Rule that is used to detect the license (i.e. "mit_456.RULE"/"mit.LICENSE")
        """

        rule_name_df = self.rule_df["rule_name"]
        lic_name_df = self.lic_df["license_name"]

        identifier_df = pd.concat([lic_name_df, rule_name_df])
        identifier_df.index = pd.RangeIndex(start=1, stop=identifier_df.shape[0] + 1)

        self.identifier_df = identifier_df
        self.identifier_dict = self.df_io.df_to_inv_dict(identifier_df)

        self.inv_identifier_dict = identifier_df.to_dict()

    def construct_key_dict(self):
        """
        Construct a String -> Dictionary from Rule and License Information, for Keys.
        "key" - License Key That is Detected (like - "mit")
        """

        lic_key_df = self.lic_df["key"]
        lic_key_df.index = pd.RangeIndex(start=1, stop=lic_key_df.shape[0] + 1)

        self.key_df = lic_key_df
        self.key_dict = self.df_io.df_to_inv_dict(lic_key_df)

        self.inv_key_dict = lic_key_df.to_dict()

    def load_info_from_scancode(self, save_info=True):
        """
        Loads License/Rule info from Scancode Files.
        Modifies and Constructs DataFrames and Dictionaries.
        Saves to File, optionally.

        :param save_info: bool
            Whether to save information to File.
        """

        rule_df = self.load_rule_info_from_scancode()
        lic_df = self.load_lic_info_from_scancode()

        self.modify_lic_rule_info(rule_df, lic_df)

        self.construct_identifier_dict()
        self.construct_key_dict()

        if save_info:
            self.save_info_to_file()


class VisualizeLicRuleInfo:

    def __init__(self):

        self.plt_figsize = (32, 16)
        self.wcloud_w = 2000
        self.wcloud_h = 1600

    @staticmethod
    def show_wordcloud(self, dataframe, text_column):

        wordcloud = WordCloud(width=self.wcloud_w, height=self.wcloud_h).generate(' '.join(dataframe[text_column]))
        plt.figure(figsize=(32, 16))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
