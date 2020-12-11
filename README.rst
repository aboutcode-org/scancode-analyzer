scancode-results-analyzer
=========================

.. what-is-scancode-results-analyzer

What is Scancode-Results-Analyzer
---------------------------------

`ScanCode`_ detects licenses, copyrights, package manifests and direct dependencies and more both in source code and
binary files.

ScanCode license detection is using multiple techniques to accurately detect licenses based on automatons, inverted
indexes and multiple sequence alignments. The detection is not always accurate enough. The goal of this project is to
improve the accuracy of license detection leveraging the ClearlyDefined and other datasets, where ScanCode is used
to massively scan millions of packages. It would also be available as a `ScanCode`_ ``post-scan`` plugin to use it
in scans directly, or in `scancode.io`_ pipelines.

This project aims to:

- Write tools and create models to massively analyze the accuracy of license detection
- Detect areas where the accuracy could be improved.
- Add this as a `scancode`_ post-scan plugin
- Add to pipelines in `scancode.io`_
- Write reusable tools and models to assist in the semi-automated reviews of scan results.
- It will also create new license detection rules semi-automatically to fix the detected anomalies

.. _ScanCode: https://github.com/nexB/scancode-toolkit
.. _scancode.io: https://github.com/nexB/scancode.io

.. from-github-links

Getting Started
---------------

Refer to the installation instructions on `INSTALL.rst`_

Documentation
-------------

Documentation: https://scancode-results-analyzer.readthedocs.io/en/latest/ [WIP]

Project Board
-------------

`Project Board`_ for  ``scancode-results-analyzer`` : Analysing Scancode License Detection Results.

.. _INSTALL.rst: https://github.com/nexB/scancode-results-analyzer/tree/master/INSTALL.rst
.. _Project Board: https://github.com/nexB/scancode-results-analyzer/projects/1
