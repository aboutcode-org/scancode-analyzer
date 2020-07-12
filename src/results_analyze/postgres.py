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

import psycopg2
from results_analyze.df_file_io import DataFrameFileIO

# Global Variables
# To Format Query
DATABASE_NAME = "clearcode_cditem"
TOOL_NAME = "%/scancode/%"
COLUMNS_RETURN = 'path, content'
COLUMNS_SEARCH = "path"


class PostgresFetch:

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.cursor, self.connection = self.init_connection()
        self.offset = 0

    def get_credentials_filepath(self):
        """
        Get credentials file os.Path object.

        :returns file_path: os.Path object
        """
        file_path = os.path.join(self.data_dir, 'credentials.json')
        return file_path

    def format_query(self, num_rows):
        """
        Formats query string using credentials and offset/row information.

        :param num_rows: No of rows to Fetch from Postgres Database
        :returns query_string: PostgreSQL query string
        """
        query_string = "SELECT {columns_return} FROM {database} WHERE {columns_search} like '{tool_name}'" \
                       "OFFSET {offset} ROWS FETCH FIRST {num_rows} ROW ONLY;".format(
                        columns_return=COLUMNS_RETURN,
                        database=DATABASE_NAME,
                        columns_search=COLUMNS_SEARCH,
                        tool_name=TOOL_NAME,
                        offset=self.offset,
                        num_rows=num_rows
                        )

        return query_string

    def init_connection(self):
        """
        Initiate Connection, called with Class Constructor.

        :returns cursor: psycopg2.cursor Object
        :returns connection: psycopg2.connection Object
        """
        # Fetch credentials from data/credentials.json
        file_path = self.get_credentials_filepath()
        credentials = DataFrameFileIO.import_data_from_json(file_path)

        # Initialize Connection Object
        connection = psycopg2.connect(user=credentials['user'],
                                      password=credentials['password'],
                                      host=credentials['host'],
                                      port=credentials['port'],
                                      database=credentials['database'])

        # Connect to Database
        cursor = connection.cursor()

        return cursor, connection

    def fetch_data(self, num_rows_to_fetch):
        """
        Fetches `path` and `contents` from the Database, into list of Tuples. Example Tuple:
        ('composer/packagist/phpro/grumphp/revision/0.16.1/tool/scancode/3.2.2.json', <memory at 0x7f222d6ccf48>)

        :param num_rows_to_fetch: int
            Number of rows to fetch, i.e. each row is a package scan
        :returns records: list of tuples
        """
        # Fetch contents of rows where path has "/scancode/"

        query_string = self.format_query(num_rows_to_fetch)
        self.offset += num_rows_to_fetch
        self.cursor.execute(query_string)

        # Load all the data into record
        records = self.cursor.fetchall()

        return records

    def close_connection(self):
        """
        Closes Postgres connection.
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            # print("PostgreSQL connection is closed")
