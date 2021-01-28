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
    There would also be a codebase-level dictionary added,
    1. With statistics on the license_detection issues.
    2. All the unique license detection issues and their occurrences.
    3. Header information.

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
            "--analyze-license-results": true
          }
        }
      ],
      "files": [
          {
              "path": "path/to/file",
              "licenses": [
                  {
                      "path": "file1.cpp"
                  }
              ],
              "license_detection_issues": [
                  {
                    "issue_id": "correct-detection"
                  }
              ]
          },
          {
              "path": "path/to/file2",
              "licenses": [
                  {
                      "path": "file2.cpp"
                  }
              ],
              "license_detection_issues": [
                  {
                      "issue_id": "false-positive"
                  }
              ]
          }
      ]
    }

.. _license_scan_issues:

Scan errors
-----------

The attribute ``license_detection_issues`` is a list of dictionaries, each dictionary representing
a file-region, and containing analysis results for all the license matches in a file-region.

.. code-block:: json

    {
        "path": "path/to/file",
        "licenses": [
            {
                "path": "file1.cpp"
            }
        ],
        "license_detection_issues": [
            {
                "start_line": 3,
                "end_line": 3,
                "issue_id": "imperfect-match-coverage",
                "issue_description": "The license detection is incorrect, a large variation is present from the matched rule(s) and is matched to only one part of the whole text",
                "issue_type": {
                    "classification_id": "notice-single-key-notice",
                    "classification_description":  "a notice that notifies a single license",
                    "is_license_text": false,
                    "is_license_notice": true,
                    "is_license_tag": false,
                    "is_license_reference": false,
                    "analysis_confidence": "high",
                    "is_suggested_matched_text_complete": true
                },
                "suggested_license": {
                    "license_expression": "gpl-2.0",
                    "matched_text": "/* Published under the GNU General Public License V.2, see file COPYING */"
                },
                "original_licenses": [
                    {
                        "key": "mit"
                    }
                ]
            }
        ]
    }

The attributes containing the analysis results are:

These 3 attributes in the analysis results has information on which file-region the matches are in.

    1. ``start_line`` and ``end_line`` marking the issue location in file
    2. ``issue_id`` and ``issue_description`` is what kind of issue it is and it's description.
    3. ``issue_type`` has further types of issues and their related attributes, listed below.
    4. ``original_license`` having the license matches with issues.

The issue type has these attributes:

    1. ``classification_id`` and ``classification_description``
    2. 4 boolean fields ``is_license_text``, ``is_license_notice``, ``is_license_tag``, and
       ``is_license_reference``.
    3. ``is_suggested_matched_text_complete`` and ``analysis_confidence``

.. _license_scan_issue_example:

Scan Errors per File-Region
---------------------------

This is a dict for every file-region, which has one or more matches in them, grouped together by
location.

.. code-block:: json

     {
        "files": [
            {
                "path": "scan-files/genshell.c",
                "licenses": [
                  {
                    "key": "lgpl-2.0"
                  }
                ],
                "licence_detection_analysis": [
                    {
                        "start_line": 14,
                        "end_line": 34,
                        "issue_id": "imperfect-match-coverage",
                        "issue_description": "The license detection is inconclusive with high confidence, because only a small part of the rule text is matched.",
                        "issue_type": {
                            "classification_id": "notice-has-unknown-match",
                            "classification_description": "License notices with unknown licenses detected.",
                            "is_license_text": false,
                            "is_license_notice": true,
                            "is_license_tag": false,
                            "is_license_reference": false,
                            "analysis_confidence": "medium",
                            "is_suggested_matched_text_complete": true
                        },
                        "suggested_license": {
                            "license_expression": "lgpl-2.0-plus",
                            "matched_text": " *  licensed under the terms of the LGPL.... "
                        }
                    },
                    {
                        "start_line": 54,
                        "end_line": 62,
                        "issue_id": "extra-words",
                        "issue_description": "The license detection is conclusive with high confidence because all the rule text is matched, but some unknown extra words have been inserted in the text.",
                        "issue_type": {
                            "classification_id": "notice-single-key-notice",
                            "classification_description":  "A notice with a single license.",
                            "is_license_text": false,
                            "is_license_notice": true,
                            "is_license_tag": false,
                            "is_license_reference": false,
                            "analysis_confidence": "high",
                            "is_suggested_matched_text_complete": true
                        },
                        "suggested_license": {
                            "license_expression": "gpl-3.0-plus",
                            "matched_text": "\"genshellopt is free software: you can redistribute it and/or modify it under \\\nthe terms of the GNU General Public License as published by the Free Software \\\nFoundation, either version 3 of the License, or (at your option) any later \\\nversion."
                        },
                        "original_licenses": []
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
    2. Incorrect Detection but only one match in a file-region. :ref:`incorrect-detection-one-match`
    3. Incorrect Detection but multiple matches in a file-region.
       :ref:`incorrect-detection-multiple-match-fragments`

.. _correct-detection-json-output:

1. Correct Detection
^^^^^^^^^^^^^^^^^^^^

In case of a correct license detection the issue has no corresponding dictionary
in `license_detection_issues`, and if all the licenses in a resource are correctly detected,
it is an empty list.

.. code-block:: json

    {
        "license_detection_issues": []
    }

.. _incorrect-detection-one-match:

2. Incorrect Detection (one match)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
        "license_detection_analysis": [
            {
                "start_line": 14,
                "end_line": 34,
                "issue_id": "imperfect-match-coverage",
                "issue_description": "The license detection is inconclusive with high confidence, because only a small part of the rule text is matched.",
                "issue_type": {
                    "classification_id": "notice-has-unknown-match",
                    "classification_description": "License notices with unknown licenses detected.",
                    "is_license_text": false,
                    "is_license_notice": true,
                    "is_license_tag": false,
                    "is_license_reference": false,
                    "analysis_confidence": "medium",
                    "is_suggested_matched_text_complete": true
                },
                "suggested_license": {
                    "license_expression": "lgpl-2.0-plus",
                    "matched_text": " *  licensed under the terms of the LGPL...."
                },
                "original_licenses": [
                    {
                        "key": "unknown"
                    },
                    {
                        "key": "lgpl-2.0-plus"
                    }
                ]
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
                "start_line": 14,
                "end_line": 34,
                "issue_id": "imperfect-match-coverage",
                "issue_description": "The license detection is inconclusive with high confidence, because only a small part of the rule text is matched.",
                "issue_type": {
                    "classification_id": "notice-has-unknown-match",
                    "classification_description": "License notices with unknown licenses detected.",
                    "is_license_text": false,
                    "is_license_notice": true,
                    "is_license_tag": false,
                    "is_license_reference": false,
                    "analysis_confidence": "medium",
                    "is_suggested_matched_text_complete": true
                },
                "suggested_license": {
                    "license_expression": "lgpl-2.0-plus",
                    "matched_text": " *  licensed under the terms of the LGPL. "
                }
            }
        ]
    }

.. _json_package_level_stats:

Basic Statistics
----------------

.. note::

    This is Work In Progress.

These are some basic statistics on the scan license info in files, and their errors detected for
quick glances into as a summary. This is also a codebase-level optional dict, that could be added.

This would be a separate ``summary`` plugin: ``--results-analyzer-summary``.

.. code-block:: json

    {
        "basic_stats": {
            "total_files_scanned": 9795,
            "total-scan_issues": 7048,
            "total_scan_issues_unique": {
                "file-regions": 345,
                "total-matches": 1067
            },
            "license_issue_types": {
                "correct-license-detection": 289,
                "extra-words": 4,
                "imperfect-match-coverage": 34,
                "near-perfect-match-coverage": 0,
                "false-positive": 8,
                "unknown-matched": 4
            },
            "unique_issues_by_license_classes": {
                "license-text": {
                    "total": 3,
                    "text-legal-lic-files": 0,
                    "text-non-legal-lic-files": 0,
                    "text-lic-text-fragments": 3
                },
                "license-notice": {
                    "total": 45,
                    "notice-and-or-except-notice": 6,
                    "notice-single-key-notice": 11,
                    "notice-has-unknown-match": 28,
                    "notice-false-positive": 0
                },
                "license-tag": {
                    "total": 14,
                    "tag-tag-coverage": 6,
                    "tag-other-tag-structures": 0,
                    "tag-false-positives": 8
                },
                "license-reference": {
                    "total": 37,
                    "reference-lead-in-or-unknown-refs": 7,
                    "reference-to-local-file": 21,
                    "reference-false-positive": 9
                }
            },
            "analysis_confidence": {
                "high": 18,
                "medium": 12,
                "low": 4
            },
            "is_suggested_matched_text_complete": {
                "True": 24,
                "False": 3
            },
            "all_unique_issues": [
                {
                    "suggested_licenses": {
                        "license_expression": "apache-2.0",
                        "matched_text": "This is licensed under the Apache 2.0 License."
                    },
                    "match_coverage_matched_rule": [23, "apache2_23.RULE"],
                    "all_occurrences": [
                        "path/to/analyzer.py",
                        "path/to/analyzer_plugin.py"
                    ],
                    "original_licenses": {
                        "score": 23,
                        "matched_text": "This is licensed under the Apache 2.0 License."
                    }
                }
            ]
        }
    }

.. _json_header_analyzer:

Header Text
-----------

This could be an optional, codebase-level header dict, which has details on the analyzer and
BERT model versions used.

.. note::

    This is Work In Progress.

.. code-block:: json

    {
        "header": {
            "tool_name": "scancode-results-analyzer",
            "version": 0.1,
            "cases_version": 0.1,
            "ml_models": [
                {
                    "name": "lic-class-scancode-bert-base-cased-L32-1",
                    "type": "sentence-classifier-bert",
                    "link": "https://huggingface.co/ayansinha/lic-class-scancode-bert-base-cased-L32-1",
                    "model": "BertBaseCased",
                    "Sentence Length": 32,
                    "Labels": 4,
                    "Label Names": {
                      "License Text": 1,
                      "License Notice": 2,
                      "License Tag": 3,
                      "License Reference": 4
                    }
                },
                {
                    "name": "false-positives-scancode-bert-base-uncased-L8-1",
                    "type": "sentence-classifier-bert",
                    "link": "https://huggingface.co/ayansinha/false-positives-scancode-bert-base-uncased-L8-1",
                    "model": "BertBaseUncased",
                    "Sentence Length": 8,
                    "Labels": 2,
                    "Label_Names": {
                      "License Tag": 1,
                      "False Positive": 2
                    }
                }
            ],
            "low_score_threshold": 95,
            "group_location_lines_threshold": 4
        }
    }

Related Issues
--------------

- `nexB/scancode-results-analyzer#22 <https://github.com/nexB/scancode-results-analyzer/issues/22>`_
- `nexB/scancode-results-analyzer#20 <https://github.com/nexB/scancode-results-analyzer/issues/20>`_
- `nexB/scancode-results-analyzer#21 <https://github.com/nexB/scancode-results-analyzer/issues/21>`_

