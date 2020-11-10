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
import json
import pandas as pd

from results_analyze.df_file_io import DataFrameFileIO


class LoadScanDataJSON:

    def __init__(self):

        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.test_data_json_dir = os.path.join(os.path.dirname(__file__), 'data/results-test')
        self.mock_metadata_filename = 'sample_metadata.json'
        self.mock_metadata_filepath = os.path.join(self.test_data_dir, self.mock_metadata_filename)
        self.json_dict_metadata = DataFrameFileIO.import_data_from_json(self.mock_metadata_filepath)

        self.rule_scans = self.get_scans_from_folder("rule")
        self.lic_scans = self.get_scans_from_folder("lic")
        self.after_rules_added = self.get_scans_from_folder("selective-after-rules-added")
        self.before_rules_added = self.get_scans_from_folder("selective-before-rules-added")

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


class TestDataIO:

    @staticmethod
    def load_dataframe_from_hdf5(store_path, dataframe_name):

        read_from_h5 = pd.HDFStore(store_path)
        dataframe = read_from_h5[dataframe_name]
        read_from_h5.close()

        return dataframe

    @staticmethod
    def store_dataframe_to_hdf5(dataframe, store_path, dataframe_name):

        store_at_h5 = pd.HDFStore(store_path)
        store_at_h5[dataframe_name] = dataframe
        store_at_h5.close()

    @staticmethod
    def load_list_from_txt(path):

        with open(path, 'r') as filehandle:
            listdata = json.load(filehandle)

        return listdata

    @staticmethod
    def write_list_of_strings_to_txt(listdata, path):

        with open(path, 'w') as filehandle:
            json.dump(listdata, filehandle)
