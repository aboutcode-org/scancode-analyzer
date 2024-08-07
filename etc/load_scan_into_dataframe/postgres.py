#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import psycopg2
import json

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

    @staticmethod
    def import_data_from_json(file_path):
        """
        Fetch postgres Database credentials.

        :returns credentials: JSON dict with credentials
        """

        with open(file_path) as f:
            credentials = json.load(f)

        return credentials

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
        credentials = self.import_data_from_json(file_path)

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
