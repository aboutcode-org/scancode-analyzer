JSON Output Format
==================

`scancode-results-analyzer` is meant to be used as a post-scan Plugin for Scancode, where after
running a scan, the scan results are then analyzed for scan errors, and that information is
added to the scancode JSON results.

Command Line Argument to use ``scancode-results-analyzer``: ``--analyze-results``

Here's how example result-JSONs from `scancode-results-analyzer` could look like.

.. _license_detection_issues_result_json:

Structure and Location in Scancode JSON
---------------------------------------

The scancode JSON format has a list of files/directories (resources), and for each of those
resources there is a list of license matches as dictionaries, with each license match in a
dictionary, with relevant attributes and corresponding values.

Now similarly the license detection analysis results will also be a resource-level list,
for each resource in the codebase this list of dictionary will be added, where each dictionary
is for each corresponding license match, having the results of the analysis for that match.

.. note::

    [WIP] Optionally,
    1. There would also be a codebase-level dictionary added, optionally, with statistics on the
    resource level information added, and some header information.
    2. Another list of dictionary will be added per-resource, with created rules for each
    file-region.

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
                "--analyze-results": true,
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
                "license_detection_errors": [
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
                "license_detection_errors": [
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

The attribute ``license_detection_errors`` is a list of dictionaries, each dictionary representing a
license match, in that file.

.. code-block:: json

    {
        "path": 'path/to/file',
        "licenses": [
            {
                "path": "file1.cpp",
            },
        ]
        "license_detection_errors": [
            {
                "location_region_number": 1,
                "license_scan_analysis_result": "imperfect_match_coverage",
                "region_license_error_case": "tag",
                "region_license_error_sub_case": "false-positive",
            }
        ]
    }

The attributes containing the analysis results are:

1. ``location_region_number``
   :ref:`location_region_number`
2. ``license_scan_analysis_result``
   :ref:`license_scan_analysis_result`
3. ``region_license_error_case``
   :ref:`dividing_into_more_cases`
4. ``region_license_error_sub_case``
   :ref:`cases_sub_cases_table`

.. _license_scan_issue_example:

Scan Errors per File
--------------------

This is a dict for every file, which has one or more matches in each file, which would be
grouped together by location.

Here only the matches with errors will be shown, by match, in lists.

.. code-block:: json

     {
        "files": [
        {
            "path": 'path/to/1914-gpiolib.c',
            "licenses": [],
            "licence_detection_errors": [
                {
                    "location_region_number": 1,
                    "license_scan_analysis_result": "false-positive",
                    "region_license_error_case": "tag",
                    "region_license_error_sub_case": "false-positive",
                }
            ]
        },
        {
            "path": 'path/to/Issues/1912-libtool-2.2.10-argz.c',
            "licenses": [],
            "lic-detection-errors": [
                {
                    "location_region_number": 1,
                    "license_scan_analysis_result": "imperfect_match_coverage",
                    "region_license_error_case": "notice",
                    "region_license_error_sub_case": "single-key-notice",
                },
                {
                    "location_region_number": 1,
                    "license_scan_analysis_result": "imperfect_match_coverage",
                    "region_license_error_case": "notice",
                    "region_license_error_sub_case": "single-key-notice",
                },
                {
                    "location_region_number": 2,
                    "license_scan_analysis_result": "imperfect_match_coverage"
                    "region_license_error_case": "reference",
                    "region_license_error_sub_case": "reference-low-score",
                },
                {
                    "location_region_number": 2,
                    "license_scan_analysis_result": "imperfect_match_coverage"
                    "region_license_error_case": "reference",
                    "region_license_error_sub_case": "reference-low-score",
                },
            ]
        }
    }

.. _generated_rules_json_format:

Generated Rules
---------------

This is a list of files, as there could be more than one generated rule per file, as there might
be multiple areas of interest, grouped by location, and one generated rule per area.

Contains rule text, as well as rule attributes, along with identifiers to link with scan results.

This would be a separate plugin: ``--generate-rules``, and would have ``--analyze-results`` as a
pre-requisite.

.. code-block:: json

     {
        "files": [
        {
            "path": Issues/1918-ntp-4.2.6/genshell.c,
            "has_license_detection_errors": True,
            "license_detection_errors": [
                    {
                        ...
                    },
            ],
            "generated_rules": [
                {
                    "rule-text": "* licensed under the terms of the LGPL. The redistributable library\n * (``libopts'') is licensed under the terms of either the LGPL or, at the\n * users discretion, the BSD license. See the AutoOpts and/or libopts sources\n * for details.\n *\n * This source file is copyrighted and licensed under the following terms:\n *\n * genshellopt copyright (c) 1999-2009 Bruce Korb - all rights reserved\n *\n * genshellopt is free software: you can redistribute it and/or modify it\n * under the terms of the GNU General Public License as published by the\n * Free Software Foundation, either version 3 of the License, or\n * (at your option) any later version.\n * \n * genshellopt is distributed in the hope that it will be useful, but\n * WITHOUT ANY WARRANTY; without even the implied warranty of\n * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n * See the GNU General Public License for more details.\n * \n * You should have received a copy of the GNU General Public License along\n * with this program. If not, see <http://www.gnu.org/licenses/>.",
                    "is-negative": false,
                    "key-id": 52,
                    "key": lgpl,
                    "rule_class": notice,
                    "start_line": 14,
                    "end_line": 34,
                    "rule-confidence": high,
                },
                {
                    "rule-text": "\t\t\t.base\t= S5PC100_GPL1(0)",
                    "is-negative": true,
                    "rule-confidence": high,
                },
            ],
        },
        ],
    }

.. _json_package_level_stats:

Basic Statistics
----------------

These are some basic statistics on the scan license info in files, and their errors detected for
quick glances into as a summary. This is also a codebase-level optional dict, that could be added.

This would be a separate ``summary`` plugin: ``--results-analyzer-summary``.

.. code-block:: json

    {
        "basic_stats": {
            "total-files-scanned": 9795,
            "total-scan-errors": 7048,
            "total-scan-errors-unique": 1067,
            "total-scan-errors-unique-by-location": 345,
            "errors-by-license-classes": {
                "license-text": 3,
                "license-notice": 45,
                "license-tag": 6,
                "license-reference": 37,
                "tag-false-positives": 8,
            },
            "scan-errors-by-score-classes": {
                "extra-words": 4,
                "low-score": 34,
                "high-but-imperfect-score": ,
                "false-pos-perfect-score": 8,
            },
            "rules-generated": 34,
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
                        "License Referance": 4
                    ],
                },
                {
                    "name": false-positives-scancode-bert-base-uncased-L8-1,
                    "type": sentence-classifier-bert,
                    "link": https://huggingface.co/ayansinha/false-positives-scancode-bert-base-uncased-L8-1,
                    "model": BertBaseUnased,
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

