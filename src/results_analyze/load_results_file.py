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


class ResultsDataFrameFile:
    def __init__(self):
        # Which columns to drop from a File Level Dataframe.
        self.drop_columns_list_file_lev = ['type', 'name', 'base_name', 'extension', 'date', 'md5',
                                           'license_expressions', 'holders', 'copyrights', 'authors', 'packages',
                                           'emails', 'urls', 'files_count', 'dirs_count', 'size_count', 'scan_errors']
        # Which columns to drop from a License Level Dataframe.
        self.drop_columns_list_lic_lev = ['name', 'short_name', 'owner', 'homepage_url', 'text_url', 'reference_url',
                                          'spdx_license_key', 'spdx_url', 'license_expression', 'matched_rule',
                                          'licenses']

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
        dataframe_lic_rule = self.dict_to_rows_matched_rule_dataframes_apply(dataframe_lic)

        # Drops Unnecessary Columns
        dataframe_lic_rule.drop(columns=self.drop_columns_list_lic_lev, inplace=True)

        # ToDo: Map Strings to Int Values

        return dataframe_lic_rule

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
        lic_level_dataframe.rename(columns={'level_1': 'lic_det_num'}, inplace=True)

        # Modifies license level information
        lic_level_dataframe = self.modify_lic_level_dataframe(lic_level_dataframe)

        # makes sha1 column as the file level Index [Primary Key].
        lic_level_dataframe.set_index('sha1', inplace=True)

        merged_df = file_level_dataframe.join(lic_level_dataframe, lsuffix='_file', rsuffix='_lic')
        merged_df.reset_index(inplace=True)

        return merged_df

    def modify_file_level_dataframe(self, dataframe_files):
        """
        Takes a File Level DataFrame, drops unnecessary columns, drops all directory rows, drops same files,
        drop files with no license detections, and makes sha1 column as the file level Index [Primary Key].

        :param dataframe_files: pd.DataFrame
            File Level DataFrames
        """
        # Drops Unnecessary Columns
        dataframe_files.drop(columns=self.drop_columns_list_file_lev, inplace=True)

        # Drops all rows with file_type as directories, as they have `NaN` as their `sha1` values
        dataframe_files.dropna(subset=['sha1'], inplace=True)

        # Add a column number of license detections per file, and drop files with no license detections
        dataframe_files['license_detections_no'] = dataframe_files.licenses.apply(lambda x: np.shape(x)[0])
        dataframe_files.drop(dataframe_files[~ (dataframe_files['license_detections_no'] > 0)].index, inplace=True)

        # Drops files that have the same sha1 hash, i.e. essentially similar files
        dataframe_files.drop_duplicates(subset='sha1', keep="last", inplace=True)

        # Makes SHA1 column the index (Slows down calculations)
        dataframe_files.set_index('sha1', inplace=True)

        return

    def create_file_level_dataframe(self, package_files_list):
        """
        Creates a File and License Level DataFrame

        :param package_files_list: list of file level dicts
        :returns file_and_lic_level_dataframe: pd.DataFrame
            Has File and License level information organized via pd.MultiIndex.
        """
        # Initialize the file package level list into a DataFrame (Row - Files, Columns - Dict keys inside Files)
        file_level_dataframe = pd.DataFrame(package_files_list)

        # Clean Up and Modify the File Level DataFrame
        self.modify_file_level_dataframe(file_level_dataframe)

        # From column 'licenses', which is a list of dicts, create License Level DataFrames
        file_and_lic_level_dataframe = self.create_lic_level_dataframe(file_level_dataframe)

        # Sets 'sha1' and 'lic_det_num' columns as the Indexes (Primary Key Tuple)
        file_and_lic_level_dataframe.set_index(['sha1', 'lic_det_num'], inplace=True)

        return file_and_lic_level_dataframe
