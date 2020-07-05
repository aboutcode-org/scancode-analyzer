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

import gzip
import json
import pandas as pd
import numpy as np

from results_analyze.postgres import PostgresFetch
from results_analyze.load_results_file import ResultsDataFrameFile

# How many rows of Database to Fetch at once
# ToDo: Calculation Function based on memory usage stats and RAM/SWAP Available
NUM_ROWS_TO_FETCH = 20

# 'table' (A bit slower, On-Disk Search/Query Enabled) or 'fixed' (Fast, No On-Disk Search/Query)
HDF5_STORE_FORMAT = 'table'


class ResultsDataFramePackage:

    def __init__(self, has_database=True):
        """
        Constructor for ResultsDataFramePackage, initialized PostgresFetch and ResultsDataFrameFile objects,
        and data paths and filenames used.
        """

        if has_database:
            self.postgres = PostgresFetch()

        self.results_file = ResultsDataFrameFile()
        self.metadata_filename = 'projects_metadata.h5'
        self.hdf_dir = os.path.join(os.path.dirname(__file__), 'data/hdf5/')
        self.json_input_dir = os.path.join(os.path.dirname(__file__), 'data/json-scan-results/')
        self.mock_metadata_filename = 'sample_metadata.json'

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

    def append_metadata_dataframe(self, metadata_dataframe):
        """
        Stores data from the a Pandas Dataframe, containing metadata to hdf5. Creates file if file doesn't exist.

        :param metadata_dataframe : pd.Dataframe
            The metadata DataFrame which has to be appended
        """

        if not os.path.exists(self.hdf_dir):
            os.makedirs(self.hdf_dir)

        file_path = os.path.join(self.get_hdf5_file_path(self.hdf_dir, self.metadata_filename))

        if not os.path.isfile(self.get_hdf5_file_path(self.hdf_dir, filename=self.metadata_filename)):
            self.store_dataframe_to_hdf5(metadata_dataframe, file_path, df_key='metadata',
                                         h5_format='Table', is_append=False)
        else:
            self.store_dataframe_to_hdf5(metadata_dataframe, file_path, df_key='metadata',
                                         h5_format='Table', is_append=True)

    @staticmethod
    def mock_db_data_from_json(json_filepath, metadata_filepath):
        """
        Takes Input from a File containing Scancode Scan Results, and returns a DataFrame is the same
        format as that of the DataBase Data.

        :param json_filepath: String
        :param metadata_filepath: String

        :return json_df: pd.Dataframe
            Returns a DataFrame with two columns "path" and "json_content". And one row of Data.
        """

        json_dict_content = PostgresFetch.import_data_from_json(json_filepath)
        json_dict_metadata = PostgresFetch.import_data_from_json(metadata_filepath)

        json_dict = pd.Series([{"_metadata": json_dict_metadata, "content": json_dict_content}])
        mock_path = pd.Series(["mock/data/-/multiple-packages/random/1.0.0/tool/scancode/3.2.2.json"])

        json_df = pd.DataFrame({"path": mock_path, "json_content": json_dict})

        return json_df

    @staticmethod
    def decompress_dataframe(compressed_dataframe):
        """
        This function is applied to one column of a Dataframe containing memoryview objects, at once,
        using the DataFrame.apply() method, to perform vectorized decompression. Returns a Pandas Series object
         each row having the corresponding JSON dict.

        :param compressed_dataframe : pd.Series
            One column of a DataFrame, containing Compressed memoryview objects.

        :returns decompressed_dataframe : pd.Series
            One column of a DataFrame, containing JSON dicts of Scan Results.
        """
        string_json = gzip.decompress(compressed_dataframe).decode('utf-8')
        decompressed_dataframe = json.loads(string_json)

        return decompressed_dataframe

    def convert_records_to_json(self, num_rows_to_fetch=NUM_ROWS_TO_FETCH):
        """
        Fetch scan_results from Postgres Database, Load into Pandas Dataframes, and Decompress into JSON dicts.

        :param num_rows_to_fetch : int
            Number of Rows to Fetch from the Postgres Database, which is essentially the number of packages scanned.

        :returns dataframe_memoryview : pd.DataFrame
            DataFrame containing two Columns 'path' and 'json_content'.
        """
        # Fetch A specified rows of Data From postgres Database, and load into a DataFrame
        data_memoryview = self.postgres.fetch_data(num_rows_to_fetch)
        dataframe_memoryview = pd.DataFrame(data_memoryview, columns=['path', 'memoryview'])

        # Decompress entire `memoryview` column, add decompressed JSON dicts at `json_content`, then drop former.
        dataframe_memoryview['json_content'] = dataframe_memoryview.memoryview.apply(self.decompress_dataframe)
        dataframe_memoryview.drop(columns=['memoryview'], inplace=True)

        return dataframe_memoryview

    @staticmethod
    def dict_to_rows_in_dataframes(dataframe, key_1, key_2):
        """
        This function is applied to one column of a Dataframe containing json dicts, at once,
        using the DataFrame.apply() method, to perform vectorized data retrieval.

        :param dataframe : pd.Series
            One column of a DataFrame, containing json dicts.
        :param key_1 : string
        :param key_2 : string

        :returns row_data : pd.Series
            One column of a DataFrame, containing values/dicts/lists that were inside those JSON dicts.
        """
        row_data = dataframe[key_1][key_2]

        return row_data

    def dict_to_rows_in_dataframes_apply(self, dataframe, key_1, key_2):
        """
        This function is applied to one column of a Dataframe containing json dicts, at once, to perform
        vectorized data retrieval. Then convert the column of dicts to a list of dicts, to create dataframes from them.
        The DataFrames columns are those dict keys.

        :param dataframe : pd.DataFrame
            DataFrame, containing json dicts in a column.
        :param key_1 : string
        :param key_2 : string

        :returns dataframe : pd.DataFrame
            DataFrame, containing new columns for each dict keys, from the dict inside the JSON dict.
        """
        dataframe_dicts = dataframe.json_content.apply(self.dict_to_rows_in_dataframes, args=(key_1, key_2))
        new_df = pd.DataFrame(list(dataframe_dicts))

        # Merge By Index, which basically Appends Column-Wise
        dataframe = dataframe.join(new_df)

        return dataframe

    def value_to_rows_in_dataframes_apply(self, dataframe, key_1, key_2, name_value):
        """
        This function is applied to one column of a Dataframe containing json dicts, at once, to perform
        vectorized data retrieval. Then convert this row of values/lists to dataframes.
        The DataFrames column name is the `name_value`.

        :param dataframe : pd.DataFrame
            One column of a DataFrame, containing json dicts.
        :param key_1 : string
        :param key_2 : string
        :param name_value : string

        :return dataframe : pd.DataFrame
            DataFrame, containing a new column for the value/list, from inside the JSON dict.
        """
        dataframe_dicts = dataframe.json_content.apply(self.dict_to_rows_in_dataframes, args=(key_1, key_2))
        new_df = pd.DataFrame({name_value: dataframe_dicts})

        # Merge By Index, which basically Appends Column-Wise
        dataframe = dataframe.join(new_df)

        return dataframe

    @staticmethod
    def convert_string_to_datetime(dataframe, old_col, new_col):
        """
        This function takes a column of string datetime, and converts it into Pandas DatetimeIndex objects.

        :param dataframe : pd.DatFrame
        :param old_col : string : Name of Old Column
        :param new_col : string : Name of New Column
        """
        # Add Pandas DateTime Column
        dataframe[new_col] = pd.to_datetime(dataframe[old_col].tolist(), format='%Y-%m-%d')

        # Drop String DateTime Column
        dataframe.drop(columns=[old_col], inplace=True)

    def save_schema_num(self, schema_series):
        """
        This function takes a Series containing schema counts, and appends it to schema DataFrame and saves on disk.

        :param schema_series : pd.Series
        """
        schema_df = pd.DataFrame(schema_series)

        file_path = os.path.join(self.get_hdf5_file_path(self.hdf_dir, self.metadata_filename))
        self.store_dataframe_to_hdf5(schema_df, file_path, df_key='schema', h5_format='table', is_append=True)

    def assert_dataframe_schema(self, path_json_dataframe):
        """
        This function takes a DataFrame containing columns 'path' and 'json_content', extracts info from path.
        uses schema info to only keep schemaVersion 3.2.2, and saves the schema count which are deleted.

        :param path_json_dataframe : pd.DatFrame
        """

        # Splits the contents of 'path' column and adds another column 'list_split' containing lists
        path_json_dataframe['list_split'] = path_json_dataframe['path'].str.split(pat="/")

        # Convert these lists (each having 9 values) into DataFrame Columns named 0-8
        split_df = pd.DataFrame.from_dict(
            dict(zip(path_json_dataframe['list_split'].index, path_json_dataframe['list_split'].values))).T

        # Give the path-split columns appropriate names
        split_df.columns = pd.Index(['pkg_source_1', 'pkg_source_2', 'pkg_owner', 'pkg_name', 'revision',
                                    'pkg_version', 'tool', 'scancode', 'schema_ver'])

        # Save the Schema Version Counts
        self.save_schema_num(split_df.groupby(split_df['schema_ver'])['revision'].count())

        # Merge these split path DataFrame with the Main DataFrame (appends columns)
        merged_df = path_json_dataframe.join(split_df)

        # Only keep Scancode scans of schemaVersion 3.2.2
        merged_df.drop(merged_df[~ (merged_df['schema_ver'] == "3.2.2.json")].index, inplace=True)

        # Columns 'revision', 'tool', 'scancode' has same entries, and info from "path", "list_split" is extracted
        # Delete these unnecessary columns
        merged_df.drop(columns=["path", "list_split", 'revision', 'tool', 'scancode', 'schema_ver'], inplace=True)

        # Replace "-" entries in column "pkg_owner" with np.nan
        merged_df.loc[merged_df["pkg_owner"] == '-', "pkg_owner"] = np.nan

        return merged_df

    def modify_package_level_dataframe(self, metadata_dataframe):
        """
        This function is applied to one column of a Dataframe containing json dicts, at once, to perform
        vectorized data retrieval. Then convert this row of values/lists to dataframes.
        The DataFrames column name is the `name_value`.

        :param metadata_dataframe : pd.DataFrame

        :returns files_dataframe : pd.DataFrame
            DataFrame, containing a two columns, which has the path_string in one, and has a list of dicts in each row
            of the other column, which is list of file-level dicts.
        :returns metadata_dataframe : pd.DataFrame
            DataFrame, containing a new column for the value/list, from inside the JSON dict.
        """
        metadata_dataframe = self.dict_to_rows_in_dataframes_apply(metadata_dataframe, key_1='content',
                                                                   key_2='license_clarity_score')
        metadata_dataframe = self.value_to_rows_in_dataframes_apply(metadata_dataframe, key_1='_metadata',
                                                                    key_2='processedAt', name_value='TimeProcess')
        metadata_dataframe = self.value_to_rows_in_dataframes_apply(metadata_dataframe, key_1='content', key_2='files',
                                                                    name_value='Files')
        metadata_dataframe.drop(columns=['json_content'], inplace=True)

        # Convert TimeProcess to TimeIndex
        self.convert_string_to_datetime(metadata_dataframe, old_col='TimeProcess', new_col='TimeIndex')

        files_dataframe = metadata_dataframe[['TimeIndex', 'Files']].copy(deep=True)
        metadata_dataframe.drop(columns=['Files'], inplace=True)

        return files_dataframe, metadata_dataframe

    def create_package_level_dataframe(self, json_filename=None):
        """
        Creates a Package Level DataFrame, with File/License Information Levels.

        :param json_filename : String
            Optional Parameter, if Passed, Takes input from a JSON File instead of a Postgres Database

        :returns main_dataframe : df.DataFrame object
            Main Storage DataFrame
            Has Project, File and License level information organized via pd.MultiIndex.
        """
        # Loads Dataframes
        if json_filename:
            json_filepath = os.path.join(self.json_input_dir, json_filename)
            mock_metadata_filepath = os.path.join(self.json_input_dir, self.mock_metadata_filename)
            path_json_dataframe = self.mock_db_data_from_json(json_filepath, mock_metadata_filepath)
        else:
            path_json_dataframe = self.convert_records_to_json()

        # Asserts if Scancode SchemaVersion is desired value, from path
        path_json_dataframe = self.assert_dataframe_schema(path_json_dataframe)

        # Converts information multiple levels inside dicts into columns
        # Package Level Data, TimeStamp, 'license_clarity_score' values,'files' list -> `New Columns`.
        files_dataframe, metadata_dataframe = self.modify_package_level_dataframe(path_json_dataframe)

        # Append metadata level information to a MetaData File
        self.append_metadata_dataframe(metadata_dataframe)

        # ToDo: Parallelize the `results_file.create_file_level_dataframe` func call 
        # Iterate through all rows, (i.e. package scans), and calls file level function for each
        # Appends the File and License Level DataFrame returned to a List.
        file_level_dataframes_list = []
        drop_files_index_list = []
        for package_scan_result in files_dataframe.itertuples():
            has_data, file_level_dataframe = self.results_file.create_file_level_dataframe(package_scan_result[2])
            if has_data:
                file_level_dataframes_list.append(file_level_dataframe)
            else:
                drop_files_index_list.append(package_scan_result[0])

        # Drops the Files which has no License Information
        files_dataframe.drop(drop_files_index_list, inplace=True)

        # Creates File level keys, which are used to create package level keys in the MultiIndex
        list_file_level_keys = list(files_dataframe['TimeIndex'])

        # Concatenate File Level Dataframes from the list, and their corresponding keys
        #  into One Package Level Dataframe, using MultiIndex. Rename Primary Key column names.
        main_dataframe = pd.concat(file_level_dataframes_list,
                                   keys=list_file_level_keys)
        main_dataframe.index.names = ['pkg_scan_time', 'file_sha1', 'lic_det_num']

        return main_dataframe