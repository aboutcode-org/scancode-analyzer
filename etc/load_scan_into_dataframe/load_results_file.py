#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import numpy as np
import pandas as pd

from results_analyze.rules_analyze import LicenseRulesInfo


class ResultsDataFrameFile:
    def __init__(self):

        self.lic_rule_info = LicenseRulesInfo(has_loaded=False)

        # Which columns to drop from a File Level Dataframe.
        self.drop_columns_list_file_lev = ['type', 'name', 'base_name', 'extension', 'date', 'md5',
                                           'license_expressions', 'holders', 'copyrights', 'authors', 'packages',
                                           'emails', 'urls', 'files_count', 'dirs_count', 'size_count', 'scan_errors']
        # Which columns to drop from a License Level Dataframe.
        self.drop_columns_list_lic_lev = ['name', 'short_name', 'owner', 'homepage_url', 'text_url', 'reference_url',
                                          'spdx_license_key', 'spdx_url', 'license_expression', 'matched_rule',
                                          'licenses']

        # String to Integer Mappings for Compression
        self.category_dict = {'Copyleft Limited': 5, 'Copyleft': 6, 'Proprietary Free': 7,
                              'Permissive': 1,  'Public Domain': 2, 'Free Restricted': 3, 'Source-available': 4,
                              'Commercial': 8, 'Unstated License': 0, 'Patent License': 9}

        self.matcher_dict = {'1-hash': 1,
                             '2-aho': 2, '3-seq': 3, '4-spdx-id': 4}

    @staticmethod
    def dict_to_rows_matched_rule_dataframes_apply(dataframe):
        """
        Makes Dicts keys inside dict 'matched_rule' -> Columns of License level DataFrame.

        :param dataframe: pd.DataFrame
        """
        new_df = pd.DataFrame(list(dataframe['matched_rule']))

        # Merge By Index, which basically Appends Column-Wise
        dataframe = dataframe.join(new_df)

        return dataframe

    def modify_lic_level_dataframe(self, dataframe_lic):
        """
        Modifies License level DataFrame, from 'matched_rule' dicts, bring information to columns.
        Maps Rule Names and other strings to integer values to compress.

        :param dataframe_lic: pd.DataFrame
        :return dataframe_lic: pd.DataFrame
        """
        # From dict 'matched_rule' expand keys to DataFrame Columns
        dataframe_lic_rule = self.dict_to_rows_matched_rule_dataframes_apply(
            dataframe_lic)

        # Drops Unnecessary Columns
        dataframe_lic_rule.drop(
            columns=self.drop_columns_list_lic_lev, inplace=True)

        return dataframe_lic_rule

    def compress_lic_level_df(self, dataframe_lic):
        """
        The following are converted from Dictionary Mappings loaded with constructor (Short dicts)
         - "category" (Category of License, i.e. Permissive, Copyleft)
         - "matcher" (type of matcher used i.e. 2-aho)

        The following are converted from Dictionary Mappings loaded from LicenseRulesInfo (much longer dicts)
         - "key" - License Key That is Detected (like - "mit")
         - "identifier" - License or License Rule that is used to detect the license (i.e. "mit_456.RULE"/"mit.LICENSE")

        :param dataframe_lic: pd.DataFrame
            License Level DataFrame
        """
        dataframe_lic["category"] = dataframe_lic["category"].map(
            self.category_dict).fillna(0).astype(np.uint8)
        dataframe_lic["matcher"] = dataframe_lic["matcher"].map(
            self.matcher_dict).fillna(0).astype(np.uint8)

        dataframe_lic["key"] = dataframe_lic["key"].map(
            self.lic_rule_info.key_dict).fillna(0).astype(np.uint16)
        dataframe_lic["identifier"] = dataframe_lic["identifier"].map(
            self.lic_rule_info.identifier_dict).fillna(0).astype(np.uint16)

    def create_lic_level_dataframe(self, file_level_dataframe):
        """
        Takes a File Level DataFrame, creates license level dataframes, modifies and cleans them up and
        appends columns to file level dataframes. Here, already existing file level info is also present at each
        license level rows.

        :param file_level_dataframe: pd.DataFrame
        :returns merged_df: pd.DataFrame
        """
        # For each file, add license level dict-keys to new columns, and multiple licenses per file into new rows
        # Introduces new column 'level_1'(renamed to 'lic_det_num'), which is the primary key for
        # each license detection inside one file.
        lic_level_dataframe = file_level_dataframe.groupby('sha1').licenses.apply(
            lambda x: pd.DataFrame(x.values[0])).reset_index()
        lic_level_dataframe.rename(
            columns={'level_1': 'lic_det_num'}, inplace=True)

        # Modifies license level information
        lic_level_dataframe = self.modify_lic_level_dataframe(
            lic_level_dataframe)

        # makes sha1 column as the file level Index [Primary Key].
        lic_level_dataframe.set_index('sha1', inplace=True)

        # Remove "licenses" column, as the data from it is already added
        file_level_dataframe.drop(columns=["licenses"], inplace=True)

        merged_df = file_level_dataframe.join(
            lic_level_dataframe, lsuffix='_file', rsuffix='_lic')
        merged_df.reset_index(inplace=True)

        self.compress_lic_level_df(merged_df)

        return merged_df

    def modify_file_level_dataframe(self, dataframe_files):
        """
        Takes a File Level DataFrame, drops unnecessary columns, drops all directory rows, drops same files,
        drop files with no license detections, and makes sha1 column as the file level Index [Primary Key].

        :param dataframe_files: pd.DataFrame
            File Level DataFrame

        :returns has_data: bool
            If A File Level DataFrame is non-empty
        """
        # Drops Unnecessary Columns
        dataframe_files.drop(
            columns=self.drop_columns_list_file_lev, inplace=True)

        # Drops all rows with file_type as directories, as they have `NaN` as their `sha1` values
        dataframe_files.dropna(subset=['sha1'], inplace=True)

        # Add a column number of license detections per file, and drop files with no license detections
        dataframe_files['license_detections_no'] = dataframe_files.licenses.apply(
            lambda x: np.shape(x)[0])
        dataframe_files.drop(dataframe_files[~ (
            dataframe_files['license_detections_no'] > 0)].index, inplace=True)

        if dataframe_files.shape[0] == 0:
            has_data = False
            return has_data
        else:
            has_data = True

        # Drops files that have the same sha1 hash, i.e. essentially similar files
        dataframe_files.drop_duplicates(
            subset='sha1', keep="last", inplace=True)

        # Makes SHA1 column the index (Slows down calculations)
        dataframe_files.set_index('sha1', inplace=True)

        return has_data

    def create_file_level_dataframe(self, package_files_list):
        """
        Creates a File and License Level DataFrame

        :param package_files_list: list of file level dicts

        :returns has_data: bool
            If A File Level DataFrame is non-empty
        :returns file_and_lic_level_dataframe: pd.DataFrame
            Has File and License level information organized via pd.MultiIndex.
        """
        # Initialize the file package level list into a DataFrame (Row - Files, Columns - Dict keys inside Files)
        file_level_dataframe = pd.DataFrame(package_files_list)

        # Clean Up and Modify the File Level DataFrame
        has_data = self.modify_file_level_dataframe(file_level_dataframe)

        # Checks if file_level_dataframe is Empty (i.e. if none of the files has any license information)
        # Exits if Yes with empty DataFrame which won't be added
        if not has_data:
            return has_data, file_level_dataframe

        # From column 'licenses', which is a list of dicts, create License Level DataFrames
        file_and_lic_level_dataframe = self.create_lic_level_dataframe(
            file_level_dataframe)

        # Sets 'sha1' and 'lic_det_num' columns as the Indexes (Primary Key Tuple)
        file_and_lic_level_dataframe.set_index(
            ['sha1', 'lic_det_num'], inplace=True)

        return has_data, file_and_lic_level_dataframe
