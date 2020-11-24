JSON Output Format
==================

`scancode-results-analyzer` is meant to be used as a post-scan Plugin for Scancode, where after
running a scan, the scan results are then analyzed for scan errors, and that information is
added to the scancode results.

Command Line Argument to use ``scancode-results-analyzer``: ``--results-analyzer``

Here's how example result-JSONs from `scancode-results-analyzer` could look like.

Related Issues
--------------

- `nexB/scancode-results-analyzer#22 <https://github.com/nexB/scancode-results-analyzer/issues/22>`_
- `nexB/scancode-results-analyzer#20 <https://github.com/nexB/scancode-results-analyzer/issues/20>`_
- `nexB/scancode-results-analyzer#21 <https://github.com/nexB/scancode-results-analyzer/issues/21>`_

Structure and Location in Scancode JSON
---------------------------------------

The scancode JSON format has a list of files/directories (resources), where there is a list of
dictionaries, with each file in a dictionary, with relevant attributes and corresponding values.

Now each resource in the codebase will have a boolean flag, and a dictionary added in them, having
the results of the analyzer. These dictionaries would have the analyzer error result details.

They would be "file-level", in the sense, together with other scancode resource-level information.

There would also be a codebase-level dictionary added, optionally, with statistics on the
resource level information added, and some header information.

.. code-block:: json

    {
        "headers": [
            {
            "tool_name": "scancode-toolkit",
            "tool_version": "3.1.1.post351.850399bc3",
            "options": {
                "input": [
                "/home/ayan/Desktop/nexB/path_to/downloaded_licenses/"
                ],
                "--results-analyzer": true,
            }
        ],
        "summary": {},
        "license_clarity_score": {},
        "summary_of_key_files": {},
        "results-analyzer": {
            "header": {
                ...
            },
            "basic_stats": {
                ...
            }
        },
        "files": [
            {
                # File Level Attributes
                "path": 'path/to/file',
                ...
                "license_detection_errors": [
                    ...
                ]
            }
            {
                "path": 'path/to/file2',
                ...
                "license_detection_errors": [
                    ...
                ]
            },
        ]
    }


Scan errors
-----------

The attribute ``license_detection_errors`` is a list of dictionaries, each dictionary representing a 

.. code-block:: json

    {
        # File Level Attributes
        "path": 'path/to/file',
        ...
        "license_detection_errors": [
            {
                "license_scan_result": "imperfect_match_coverage",
                "error_class": {
                    "class_type": 'tag',
                }
                "location_group": 1,
                "location_group_class": "tag",
                "location_group_subclass": "false-positive",
            }
        ]
    }


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
            ...
            "licence_detection_errors": [
                {
                    # Num Index for matches
                    "lic_det_num": 1,

                    # Scancode Match Attributes
                    "matched_text": "\t\t\t.base\t= S5PC100_GPL1(0)",
                    "identifier": 7229,
                    "match_coverage": 100.0,
                    "score": 100.0,
                    "start_line": 266,
                    "end_line": 266,
                    "matched_length": 1,

                    # Analyzer Result Attributes
                    "license_scan_result": "false-positive",
                    "error_class": {
                        "class-type": tag,
                        "subclass": false-positive,
                        "error-id": tag-false-positive,
                        "error-name": 31,
                    }
                    "location-group": 1,
                    "location-group-class": "notice",
                }
            ]
        },
        {
            "path": 'path/to/Issues/1912-libtool-2.2.10-argz.c',
            ...
            "lic-detection-errors": [
                {
                    "license_detection_num": 1,
                    "matched_text": "Copyright (C) 2004, 2006, 2007, 2008 Free Software Foundation, Inc.\n Written by Gary V. Vaughan, 2004\n\n NOTE: The canonical source of this file is maintained with the\n GNU Libtool package. Report bugs to bug-libtool@gnu.org.\n\nGNU Libltdl is free software; you can redistribute it and/or\nmodify it under the terms of the GNU Lesser General Public\nLicense as published by the Free Software Foundation; either\nversion 2 of the License, or (at your option) any later version.\n\nAs a special exception to the GNU Lesser General Public License,",
                    "identifier": 7229,
                    "match_coverage": 40.62,
                    "score": 40.62,
                    "start_line": 3,
                    "end_line": 14,
                    "matched_length": 52,

                    "license_scan_result": "imperfect_match_coverage",
                    "error-class": {
                        "class-type": notice,
                        "subclass": low-score,
                        "error-id": notice-low-score,
                        "error-name": 21,
                    }
                    "location-group": 1,
                    "location-group-class": "notice",
                },
                {
                    "license_detection_num": 2,
                    "matched_text": "As a special exception to the GNU Lesser General Public License,",
                    "identifier": 7229,
                    "match_coverage": 100,
                    "score": 16,
                    "start_line": 14,
                    "end_line": 14,
                    "matched_length": 3,

                    "license_scan_result": "imperfect_match_coverage",
                    "error-class": {
                        "class-type": notice,
                        "subclass": low-score,
                        "error-id": notice-low-score,
                        "error-name": 21,
                    }
                    "location-group": 1,
                    "location-group-class": notice,
                },
                {
                    "license_detection_num": 3,
                    "matched_text": "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\nGNU Lesser General Public License for more details",
                    "identifier": 7229,
                    "match_coverage": 100.0,
                    "score": 33.0,
                    "start_line": 21,
                    "end_line": 22,
                    "matched_length": 6,

                    "license_scan_result": "imperfect_match_coverage",
                    "error-class": {
                        "class-type": referance,
                        "subclass": low-score,
                        "error-id": referance-low-score,
                        "error-name": 41,
                    }
                    "location-group": 2,
                    "location-group-class": referance,
                }
                {
                    "license_detection_num": 4,
                    "matched_text": "You should have received a copy of the GNU Lesser General Public\nLicense along with GNU Libltdl; see the file COPYING.LIB. If not, a",
                    "identifier": 7229,
                    "match_coverage": 100.0,
                    "score": 33.0,
                    "start_line": 24,
                    "end_line": 25,
                    "matched_length": 6,

                    "license_scan_result": "imperfect_match_coverage",
                    "error-class": {
                        "class-type": referance,
                        "subclass": low-score,
                        "error-id": referance-low-score,
                        "error-name": 41,
                    }
                    "location-group": 2,
                    "location-group-class": referance,
                }
            ]
        }
    }

Generated Rules
---------------

This is a list of files, as there could be more than one generated rule per file, as there might
be multiple areas of interest, grouped by location, and one generated rule per area.

Contains rule text, as well as rule attributes, along with identifiers to link with scan results.

.. code-block:: json

     {
        "files": [
        {
            "path": Issues/1918-ntp-4.2.6/genshell.c,
            "has_license_detection_errors": True,
            "license_detection_errors": [
                ...
            ],
            "generated_rules": [
                {
                    # Rule Info
                    "rule-text": "* licensed under the terms of the LGPL. The redistributable library\n * (``libopts'') is licensed under the terms of either the LGPL or, at the\n * users discretion, the BSD license. See the AutoOpts and/or libopts sources\n * for details.\n *\n * This source file is copyrighted and licensed under the following terms:\n *\n * genshellopt copyright (c) 1999-2009 Bruce Korb - all rights reserved\n *\n * genshellopt is free software: you can redistribute it and/or modify it\n * under the terms of the GNU General Public License as published by the\n * Free Software Foundation, either version 3 of the License, or\n * (at your option) any later version.\n * \n * genshellopt is distributed in the hope that it will be useful, but\n * WITHOUT ANY WARRANTY; without even the implied warranty of\n * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n * See the GNU General Public License for more details.\n * \n * You should have received a copy of the GNU General Public License along\n * with this program. If not, see <http://www.gnu.org/licenses/>.",
                    "is-negative": false,
                    "key-id": 52,
                    "key": lgpl,
                    "rule_class": notice,

                    # Debug Help Info
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

Header Text
-----------

This could be an optional, codebase-level header dict, which has details on the analyzer and
BERT model versions used.

This could even be a separate ``generate_rules`` plugin: ``--results-analyzer-generate-rules``.

.. code-block:: json

    {
        "header": {
            "tool_name": scancode-results-analyzer,
            "version": 0.1,
            "ml-models": [
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
                    ],,
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
            "low-score-threshold": 95,
            "group-location-lines-threshold": 4,
        },
    }


Basic Statistics
----------------

These are some basic statistics on the scan license info in files, and their errors detected for
quick glances into as a summary. This is also a codebase-level optional dict, that could be added.

This could even be a separate ``summary`` plugin: ``--results-analyzer-summary``.

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


