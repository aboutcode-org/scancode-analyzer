
import os

from results_analyze import load_scancode_data


class TestLoadScancodeData():
        
    def test_check_loaded_data(self):
        
        info = load_scancode_data.LicenseRulesInfo()
        expected_rule_attributes = [
            'license_expression', 'is_license_tag', 'relevance', 'rule_filename',
            'text', 'words_count', 'is_license_notice', 'ignorable_urls',
            'is_license_reference', 'referenced_filenames', 'minimum_coverage',
            'notes', 'is_license_text', 'ignorable_copyrights', 'ignorable_holders',
            'ignorable_authors', 'ignorable_emails', 'only_known_words',
            'is_false_positive', 'is_license_intro'
        ]
        expected_license_attributes = [
            'key', 'short_name', 'name', 'category', 'owner', 'homepage_url',
            'is_exception', 'spdx_license_key', 'text_urls', 'other_urls',
            'standard_notice', 'license_filename', 'text', 'words_count', 'notes',
            'faq_url', 'ignorable_authors', 'ignorable_copyrights',
            'ignorable_holders', 'ignorable_urls', 'ignorable_emails',
            'minimum_coverage', 'osi_license_key', 'osi_url',
            'other_spdx_license_keys', 'language'
        ]
        assert list(info.rule_df.columns) == expected_rule_attributes
        assert list(info.lic_df.columns) == expected_license_attributes