JSON Output Format
==================

`scancode-results-analyzer` is meant to be used as a post-scan Plugin for Scancode, where after
running a scan, the scan results are then analyzed for scan errors, and that information is
added to the scancode JSON results.

Command Line Argument to use ``scancode-results-analyzer``: ``--analyze-license-results``

Here's how example result-JSONs from `scancode-results-analyzer` could look like, post-analysis.

.. _license_detection_issues_result_json:

Structure and Location in Scancode JSON
---------------------------------------

The scancode JSON format has a list of files/directories (resources), and for each of those
resources there is a list of license matches as dictionaries, with each license match in a
dictionary, with relevant attributes and corresponding values.

Now similarly the license detection analysis results will also be a resource-level list,
for each resource in the codebase this list of dictionary will be added, where each dictionary
is for each corresponding file-region :ref:`file_region`, having the results of the analysis for all
the match(es) in that file-region.

.. note::

    [WIP]
    1. Optionally, There would also be a codebase-level dictionary added, optionally, with statistics on the
    resource level information added, and some header information.
    2. More Sub-cases of errors are being added.

.. code-block:: json

    {
        "headers": [
            {
            "tool_name": "scancode-toolkit",
            "tool_version": "3.1.1.post351.850399bc3",
            "options": {
                "input": [
                "/path_to/downloaded_licenses/"
                ],
                "--analyze-license-results": true,
            }
        ],
        "files": [
            {
                "path": 'path/to/file',
                "licenses": [
                    {
                        "path": "file1.cpp",
                    },
                ]
                "license_detection_analysis": [
                    {
                        ...
                    },
                ]
            }
            {
                "path": 'path/to/file2',
                "licenses": [
                    {
                        "path": "file2.cpp",
                    },
                ]
                "license_detection_analysis": [
                    {
                        ...
                    },
                ]
            },
        ]
    }

.. _license_scan_issues:

Scan errors
-----------

The attribute ``license_detection_analysis`` is a list of dictionaries, each dictionary representing a
file-region, and containing analysis results for all the license matches in a file-region.

.. code-block:: json

    {
        "path": 'path/to/file',
        "licenses": [
            {
                "path": "file1.cpp",
            },
        ]
        "license_detection_analysis": [
        {
          "start_line_region": 3,
          "end_line_region": 3,
          "license_matches": [
            ...
          ],
          "license_match_post_analysis": {
            "key": "gpl-2.0",
            "matched_text": "/* Published under the GNU General Public License V.2, see file COPYING */"
          },
          "license_scan_analysis_result": "imperfect-match-coverage",
          "license_scan_analysis_result_description": "The license detection is incorrect, a large variation is present from the matched rule(s) and is matched to only one part of the whole text",
          "region_license_error_case": "notice",
          "region_license_error_case_description": "A notice referencing the license name and some terms/implications are present in the matched text",
          "region_license_error_sub_case": "notice-single-key-notice",
          "region_license_error_sub_case_description":  "a notice that notifies a single license",
        }
    }

The attributes containing the analysis results are:

1.  `start_line_region`, `end_line_region` and `license_matches`
   :ref:`location_regions_division`
2. ``license_scan_analysis_result``
   :ref:`license_scan_analysis_result`
3. ``region_license_error_case``
   :ref:`dividing_into_more_cases`
4. ``region_license_error_sub_case``
   :ref:`cases_sub_cases_table`

.. _license_scan_issue_example:

Scan Errors per File-Region
---------------------------

This is a dict for every file-region, which has one or more matches in them, grouped together by location.

.. code-block:: json

     {
        "files": [
            {
                "scan-files/genshell.c",
                "licenses": [
                    ...
                ],
                "licence_detection_analysis": [
                    {
                        "start_line_region": 14,
                        "end_line_region": 34,
                        "license_matches": [
                            ...
                        ],
                        "license_match_post_analysis": {
                            "key": "agpl-3.0-plus",
                            "rule_text": " *  licensed under the terms of the LGPL.  The redistributable library\n *  (``libopts'') is licensed under the terms of either the LGPL or, at the\n *  users discretion, the BSD license.
                        },
                        "license_scan_analysis_result": "imperfect-match-coverage",
                        "license_scan_analysis_result_description": "The license detection is incorrect, a large variation is present from the matched rule(s) and is matched to only one part of the whole text",
                        "region_license_error_case": "notice",
                        "region_license_error_case_description": "A notice referencing the license name and some terms/implications are present in the matched text",
                        "region_license_error_sub_case": null,
                        "region_license_error_sub_case_description": null
                    },
                    {
                        "start_line_region": 54,
                        "end_line_region": 62,
                        "license_matches": [
                            ...
                        ],
                        "license_match_post_analysis": {
                            "key": "gpl-3.0-plus",
                            "matched_text": "\"genshellopt is free software: you can redistribute it and/or modify it under \\\nthe terms of the GNU General Public License as published by the Free Software \\\nFoundation, either version 3 of the License, or (at your option) any later \\\nversion."
                        },
                        "license_scan_analysis_result": "extra-words",
                        "license_scan_analysis_result_description": "A license rule from the scancode rules matches completely with a part of the text, but there's some extra words which aren't there in the rule",
                        "region_license_error_case": "notice",
                        "region_license_error_case_description": "A notice referencing the license name and some terms/implications are present in the matched text",
                        "region_license_error_sub_case": null,
                        "region_license_error_sub_case_description": null
                        }
                    }
                ]
            }
        ]
    }

.. _generated_rules_json_format:

Generated Rules
---------------

There are 3 cases of file-regions and corresponding different outputs for each:

    1. Correct Detection. :ref:`correct-detection-json-output`
    2. Incorrect Detection but only one match in a file-region. (or multiple joined by AND/OR/EXCEPT) :ref:`incorrect-detection-one-match`
    3. Incorrect Detection but multiple (often fragments) matches in a file-region. :ref:`incorrect-detection-multiple-match-fragments`

.. _correct-detection-json-output:

1. Correct Detection
^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
        "license_detection_analysis": [
        {
            "start_line_region": 9,
            "end_line_region": 22,
            "license_matches": [
                ...                 # The correctly detected license match would be here
            ],
            "license_match_post_analysis": null
            "license_scan_analysis_result": "correct-license-detection",
            "license_scan_analysis_result_description": "The license detection is correct",
            "region_license_error_case": null,
            "region_license_error_case_description": null,
            "region_license_error_sub_case": null,
            "region_license_error_sub_case_description": null
        ]
    }

.. _incorrect-detection-one-match:

2. Incorrect Detection (one match)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
        "license_detection_analysis": [
            {
                "start_line_region": 3,
                "end_line_region": 3,
                "license_matches": [
                ...                     # The wrongly detected license match would be here
                ],
                "license_match_post_analysis": {
                    "key": "gpl-2.0",
                    "matched_text": "/* Published under the GNU General Public License V.2, see file COPYING */"
                },
                "license_scan_analysis_result": "imperfect-match-coverage",
                "license_scan_analysis_result_description": "The license detection is incorrect, a large variation is present from the matched rule(s) and is matched to only one part of the whole text",
                "region_license_error_case": "notice",
                "region_license_error_case_description": "A notice referencing the license name and some terms/implications are present in the matched text",
                "region_license_error_sub_case": "notice-single-key-notice",
                "region_license_error_sub_case_description": "a notice that notifies a single license",
            }
        ]
    }

.. _incorrect-detection-multiple-match-fragments:

3. Incorrect Detection (multiple matches)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
        "license_detection_analysis": [
            {
                "start_line_region": 14,
                "end_line_region": 34,
                "license_matches": [
                    ...                       # The wrongly detected license matches would be here
                ],
                "license_match_post_analysis": {
                    "key": "agpl-3.0-plus",
                    "rule_text": " *  licensed under the terms of the LGPL.  The redistributable library\n *  (``libopts'') is licensed under the terms of either the LGPL or, at the\n *  users discretion, the BSD license.
                },
                "license_scan_analysis_result": "imperfect-match-coverage",
                "license_scan_analysis_result_description": "The license detection is incorrect, a large variation is present from the matched rule(s) and is matched to only one part of the whole text",
                "region_license_error_case": "notice",
                "region_license_error_case_description": "A notice referencing the license name and some terms/implications are present in the matched text",
                "region_license_error_sub_case": "notice-single-key-notice",
                "region_license_error_sub_case_description": "a notice that notifies a single license",
            }
        ]
    }

.. _json_package_level_stats:

Basic Statistics [WIP]
----------------------

These are some basic statistics on the scan license info in files, and their errors detected for
quick glances into as a summary. This is also a codebase-level optional dict, that could be added.

This would be a separate ``summary`` plugin: ``--results-analyzer-summary``.

.. code-block:: json

    {
        "basic_stats": {
            "total-files-scanned": 9795,
            "total-scan-errors": 7048,
            "total-scan-errors-unique": {
                "file-regions": 345,
                "total-matches": 1067,
            },
            "scan-errors-by-main-score-classes": {
                "correct-detection": 289,
                "extra-words": 4,
                "low-score": 34,
                "high-but-imperfect-score": 0,
                "false-pos-perfect-score": 8,
            },
            "errors-by-license-classes": {
                "license-text": {
                    "total": 3,
                    "text-legal-lic-files": 0,
                    "text-non-legal-lic-files": 0,
                    "text-lic-text-fragments": 3,
                },
                "license-notice": {
                    "total": 45,
                    "notice-and-or-except-notice": ,
                    "notice-single-key-notice": "a notice that notifies a single license",
                },
                "license-tag": {
                    "total": 14,
                    "tag-tag-coverage": 6,
                    "tag-other-tag-structures": 0,
                    "tag-false-positives": 8,
                },
                "license-reference": {
                    "total": 37,
                    "reference-lead-in-refs": 7,
                    "reference-low-coverage-refs": 21,
                    "reference-unknown-refs": 9,
                }
            },
            "rules-by-confidence": {
                "high-confidence": 18,
                "review-needed": 12,
                "review-needed-with-scanned-file": 4,
            }
        },
    }

.. _json_header_analyzer:

Header Text
-----------

This could be an optional, codebase-level header dict, which has details on the analyzer and
BERT model versions used.

.. code-block:: json

    {
        "header": {
            "tool_name": scancode-results-analyzer,
            "version": 0.1,
            "cases_version": 0.1,
            "ml_models": [
                {
                    "name": lic-class-scancode-bert-base-cased-L32-1,
                    "type": sentence-classifier-bert,
                    "link": https://huggingface.co/ayansinha/lic-class-scancode-bert-base-cased-L32-1,
                    "model": BertBaseCased,
                    "Sentence Length": 32,
                    "Labels": 4,
                    "Label Names": [
                        "License Text": 1,
                        "License Notice": 2,
                        "License Tag": 3,
                        "License Reference": 4
                    ],
                },
                {
                    "name": false-positives-scancode-bert-base-uncased-L8-1,
                    "type": sentence-classifier-bert,
                    "link": https://huggingface.co/ayansinha/false-positives-scancode-bert-base-uncased-L8-1,
                    "model": BertBaseUncased,
                    "Sentence Length": 8,
                    "Labels": 2,
                    "Label_Names": [
                        "License Tag": 1,
                        "False Positive": 2
                    ],
                },
            ],
            "low_score_threshold": 95,
            "group_location_lines_threshold": 4,
        },
    }


Related Issues
--------------

- `nexB/scancode-results-analyzer#22 <https://github.com/nexB/scancode-results-analyzer/issues/22>`_
- `nexB/scancode-results-analyzer#20 <https://github.com/nexB/scancode-results-analyzer/issues/20>`_
- `nexB/scancode-results-analyzer#21 <https://github.com/nexB/scancode-results-analyzer/issues/21>`_

