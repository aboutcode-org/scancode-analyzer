#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/aboutcode-org/scancode-toolkit/
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
#  Visit https://github.com/aboutcode-org/scancode-toolkit/ for support and download.

import pandas as pd

from licensedcode import models

# Threshold of Words which is used in `Rule.compute_relevance` in `scancode.licensedcode.models.py`
THRESHOLD_COMPUTE_RELEVANCE = 18.0

# Different Rule Attribute Groups
boolean_rule_attributes = [
    "is_license_reference", "is_license_text", "is_license_notice",
    "is_license_tag", "is_license_intro", "only_known_words", "is_false_positive"
]

ignorables = [
    'ignorable_copyrights', 'ignorable_holders', 'ignorable_authors',
    'ignorable_emails', 'ignorable_urls'
]

other_optionals = ['referenced_filenames', 'notes']


class LicenseRulesInfo:
    """
    Contains all Licenses and License Rules related information, loaded from scancode.
    """

    def __init__(
        self,
        rules_folder=models.rules_data_dir,
        licenses_folder=models.licenses_data_dir
    ):
        self.rule_df = None
        self.lic_df = None

        self.load_scancode_rules(rules_folder)
        self.load_scancode_licenses(licenses_folder)
        self.modify_lic_rule_info()

    def load_scancode_rules(self, rules_folder):
        """
        Loads all scancode rules into a Dataframe.
        """
        rules = list(models.load_rules(rules_folder))
        rules_df = []

        for rule in rules:
            df = pd.DataFrame.from_dict(rule.to_dict(), orient='index').T
            rule_text = rule.text()
            df["rule_filename"] = rule.data_file.split("/")[-1][:-4]
            df["text"] = rule_text
            df["words_count"] = len(rule_text.split())
            rules_df.append(df)

        self.rule_df = pd.concat(rules_df)

    def load_scancode_licenses(self, licenses_folder):
        """
        Loads all scancode licenses into a Dataframe.
        """
        licenses = models.load_licenses(licenses_folder)
        licenses_df = []

        for license in licenses.values():

            df = pd.DataFrame.from_dict(license.to_dict(), orient='index').T
            license_text = license.text
            df["license_filename"] = license.data_file.split("/")[-1][:-4]
            df["text"] = license_text
            df["words_count"] = len(license_text.split())
            licenses_df.append(df)

        self.lic_df = pd.concat(licenses_df)

    @staticmethod
    def rules_compute_relevance(rule_df, threshold=THRESHOLD_COMPUTE_RELEVANCE):
        """
        Compute all the Relevance Values of Rules where it isn't given explicitly.

        :param rule_df: pd.DataFrame
            DataFrame with all Rule Information.
        :param threshold: float
            The threshold value, above which rules have a relevance of 100
        """

        rule_df.loc[rule_df["is_false_positive"] is True, "relevance"] = 100

        rule_df.loc[rule_df["words_count"] >= threshold, "relevance"] = 100

        relevance_of_one_word = round((1 / threshold) * 100, 2)
        rule_df.loc[
            rule_df["relevance"].isna(),
            "relevance"
        ] = rule_df.loc[
            rule_df["relevance"].isna(),
            "words_count"
        ] * relevance_of_one_word

    @staticmethod
    def rules_compute_min_cov(rule_df):
        """
        Compute all the Minimum Coverage Values of Rules where it isn't given explicitly.

        :param rule_df: pd.DataFrame
            DataFrame with all Rule Information.
        """

        rule_df.loc[rule_df["minimum_coverage"].isna(), "minimum_coverage"] = 0

    @staticmethod
    def licences_compute_min_cov(lic_df):
        """
        Compute all the Minimum Coverage Values of Licenses where it isn't given explicitly.

        :param lic_df: pd.DataFrame
            DataFrame with all License Information.
        """
        lic_df.loc[lic_df["minimum_coverage"].isna(), "minimum_coverage"] = 0

    def modify_lic_rule_info(self):
        """
        Formats and Modifies Rule/License Information.

        :param rule_df: pd.DataFrame
            DataFrame with all Rules Information.
        :param lic_df: pd.DataFrame
            DataFrame with all License Information.
        """
        # Convert NaN Values in Boolean Columns to False, making it a boolean column, not object
        self.rule_df.fillna(
            {x: False for x in boolean_rule_attributes},
            inplace=True
        )

        self.rules_compute_relevance(self.rule_df)
        self.rules_compute_min_cov(self.rule_df)
        self.licences_compute_min_cov(self.lic_df)
