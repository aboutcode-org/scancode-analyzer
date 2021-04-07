scancode-analyzer
=================

.. what-is-scancode-analyzer

What is Scancode-Analyzer
-------------------------

`ScanCode`_ detects licenses, copyrights, package manifests and direct dependencies and more both in
source code and binary files.

ScanCode license detection is using multiple techniques to accurately detect licenses based on
automatons, inverted indexes and multiple sequence alignments. As the detection supports approximate
matching, there's a lot of `unknown` detections, or multiple approximate matches.

The goal of this project is to improve the accuracy of license detection leveraging scancode scans,

It is a `ScanCode`_ ``post-scan`` plugin to use it in scans directly, and in future as
`scancode.io`_ pipelines, with better issue review and reporting features.

This project aims to:

- Write tools and create models to massively analyze the accuracy of license detection
- Detect areas where the accuracy could be improved.
- Add this as a `scancode`_ post-scan plugin
- Add to pipelines in `scancode.io`_
- Write reusable tools and models to assist in the semi-automated reviews of scan results.
- It will also suggest new license detection rules semi-automatically to fix the detected anomalies

.. _ScanCode: https://github.com/nexB/scancode-toolkit
.. _scancode.io: https://github.com/nexB/scancode.io

.. from-github-links

Getting Started
---------------

Refer to the installation instructions on `INSTALL.rst`_

Documentation
-------------

Documentation: https://scancode-analyzer.readthedocs.io/en/latest/

Project Board
-------------

`Project Board`_ for  ``scancode-analyzer`` : Analysing Scancode License Detection Results.

.. _INSTALL.rst: https://github.com/nexB/scancode-analyzer/tree/master/INSTALL.rst
.. _Project Board: https://github.com/nexB/scancode-analyzer/projects/1
