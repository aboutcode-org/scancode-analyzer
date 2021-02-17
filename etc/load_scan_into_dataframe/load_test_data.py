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

import os
import pandas as pd

from results_analyze.df_file_io import DataFrameFileIO


class TestData:

    def __init__(self):

        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.test_data_json_dir = os.path.join(os.path.dirname(__file__), 'data/results-test')
        self.mock_metadata_filename = 'sample_metadata.json'
        self.mock_metadata_filepath = os.path.join(self.test_data_dir, self.mock_metadata_filename)
        self.json_dict_metadata = DataFrameFileIO.import_data_from_json(self.mock_metadata_filepath)

        self.rule_scans = self.get_scans_from_folder("rule")
        self.lic_scans = self.get_scans_from_folder("lic")

    def get_scans_from_folder(self, folder_name):

        data_path = os.path.join(self.test_data_json_dir, folder_name)

        files_all = []

        for (dirpath, dirnames, filenames) in os.walk(data_path):
            filenames.sort()
            files_all.extend(filenames)

        json_dict_metadata = DataFrameFileIO.import_data_from_json(self.mock_metadata_filepath)
        mock_path = pd.Series(["mock/data/-/multiple-packages/random/1.0.0/tool/scancode/3.2.2.json"])

        packages_all = []

        for file in files_all:
            json_filepath = os.path.join(data_path, file)
            json_dict_content = DataFrameFileIO.import_data_from_json(json_filepath)

            json_dict = pd.Series([{"_metadata": json_dict_metadata, "content": json_dict_content}])
            json_df = pd.DataFrame({"path": mock_path, "json_content": json_dict})

            packages_all.append(json_df)

        pkg_dataframe = pd.concat(packages_all)

        return pkg_dataframe


class DataFrameFileIO:

    def __init__(self):

        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

        self.metadata_filename = 'projects_metadata.h5'
        self.mock_metadata_filename = 'sample_metadata.json'

        self.hdf_dir = os.path.join(os.path.dirname(__file__), 'data/hdf5/')
        self.json_input_dir = os.path.join(os.path.dirname(__file__), 'data/json-scan-results/')
        self.from_scancode_dir = os.path.join(os.path.dirname(__file__), 'data/from-scancode/')
        self.path_scancode_folders_json = os.path.join(os.path.dirname(__file__), 'data/rule_lic_folder_paths.json')

    @staticmethod
    def import_data_from_json(file_path):
        """
        Fetch postgres Database credentials.

        :returns credentials: JSON dict with credentials
        """

        with open(file_path) as f:
            json_dict = json.load(f)

        return json_dict

    def load_folder_names(self):

        files = self.import_data_from_json(self.path_scancode_folders_json)
        lic_folder_path = os.path.join(files["lic_folder"])
        rule_folder_path = os.path.join(files["rule_folder"])

        return lic_folder_path, rule_folder_path

    @staticmethod
    def get_hdf5_file_path(hdf_dir, filename):
        """
        Gets filepath.

        :param hdf_dir : string
        :param filename : string

        :returns filepath : os.Path
        """
        file_path = os.path.join(hdf_dir, filename)
        return file_path

    # ToDo: Support Selective Query/Search
    @staticmethod
    def load_dataframe_from_hdf5(file_path, df_key):
        """
        Loads data from the hdf5 to a Pandas Dataframe.

        :param file_path : string
        :param df_key : string

        :returns filepath : pd.DataFrame object containing the Data read from the hdf5 file.
        """

        dataframe = pd.read_hdf(path_or_buf=file_path, key=df_key)

        return dataframe

    @staticmethod
    def store_dataframe_to_hdf5(dataframe, file_path, df_key, h5_format=HDF5_STORE_FORMAT, is_append=False):
        """
        Stores data from the a Pandas Dataframe to hdf5.

        :param dataframe : pd.Dataframe
            The DataFrame which has to be stored
        :param file_path : string
        :param df_key: string
            Table name inside the h5 file for this dataframe.
        :param h5_format : string
            PyTables storage format
        :param is_append : bool
        """

        if is_append:
            # File has to exist
            dataframe.to_hdf(path_or_buf=file_path, key=df_key, mode='r+', format=h5_format)
        else:
            dataframe.to_hdf(path_or_buf=file_path, key=df_key, mode='w', format=h5_format)

    @staticmethod
    def df_to_inv_dict(df):
        """
        Converts a DataFrame to a String -> Integer Mapping Dictionary.

        :param df: pd.DataFrame
            The DataFrame with one column and Numerical Index
        :return inv_dict: dict
            String -> Integer Dictionary for the DataFrame
        """

        # Creates Integer -> String Dictionary
        df_dict = df.to_dict()

        # Inverse Dictionary
        inv_dict = {v: k for k, v in df_dict.items()}

        return inv_dict

    def get_prog_lang_dict(self):
        """
        Gets all Programming Languages detected by scancode from a text file
        (collected from scancode.typecode.prog_lexers.py)
        Converts them to a String -> Integer Mapping Dictionary for Compression Purposes.

        :return inv_prog_map: dict
            String -> Integer Dictionary for all the Programming Languages
        """
        prog_lang_file_path = os.path.join(self.from_scancode_dir, "languages.txt")

        prog_languages = []
        with open(prog_lang_file_path, "r") as file:
            for line in file:
                prog_languages.append(line.strip())

        lang_df = pd.DataFrame(prog_languages, columns=["prog_lang"],
                               index=pd.RangeIndex(start=1, stop=len(prog_languages) + 1))

        inv_prog_map = self.df_to_inv_dict(lang_df["prog_lang"])

        return inv_prog_map

    def mock_db_data_from_json(self, json_filename):
        """
        Takes Input from a File containing Scancode Scan Results, and returns a DataFrame is the same
        format as that of the DataBase Data.

        :param json_filename: String

        :return json_df: pd.Dataframe
            Returns a DataFrame with two columns "path" and "json_content". And one row of Data.
        """

        json_filepath = os.path.join(self.json_input_dir, json_filename)
        mock_metadata_filepath = os.path.join(self.json_input_dir, self.mock_metadata_filename)

        json_dict_content = self.import_data_from_json(json_filepath)
        json_dict_metadata = self.import_data_from_json(mock_metadata_filepath)

        json_dict = pd.Series([{"_metadata": json_dict_metadata, "content": json_dict_content}])
        mock_path = pd.Series(["mock/data/-/multiple-packages/random/1.0.0/tool/scancode/3.2.2.json"])

        json_df = pd.DataFrame({"path": mock_path, "json_content": json_dict})

        return json_df
