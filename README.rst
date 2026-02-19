scancode-analyzer
=================

.. what-is-scancode-analyzer

What is ScanCode-Analyzer
-------------------------

`ScanCode`_ detects licenses, copyrights, package manifests, direct dependencies and more in
source code orbinary files.

ScanCode license detection uses multiple techniques to accurately detect licenses based on
automatons, inverted indexes and multiple sequence alignments. As the detection supports approximate
matching, there are many `unknown` detections, or multiple approximate matches.

The goal of this project is to improve the accuracy of license detection by leveraging ScanCode scan data.

It is a `ScanCode`_ ``post-scan`` plugin for direct use in scans. In future we plan to add
`scancode.io`_ pipelines, with better issue review and reporting features.

This project aims to:

- Write tools and create models to massively analyze the accuracy of license detection
- Detect areas where the accuracy could be improved.
- Add this as a `scancode`_ post-scan plugin
- Add this to pipelines in `scancode.io`_
- Write reusable tools and models to assist in the semi-automated reviews of scan results.
- Suggest new license detection rules semi-automatically to fix the detected anomalies

.. _ScanCode: https://github.com/aboutcode-org/scancode-toolkit
.. _scancode.io: https://github.com/aboutcode-org/scancode.io

.. from-github-links

Getting Started
---------------

Refer to the installation instructions on `INSTALL.rst`_

.. _INSTALL.rst: https://github.com/aboutcode-org/scancode-analyzer/blob/main/INSTALL.rst

Documentation
-------------

Documentation: https://scancode-analyzer.readthedocs.io/en/latest/
