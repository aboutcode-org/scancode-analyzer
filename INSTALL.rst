Installation
============

The installation methods install the `scancode-analyzer` post-scan plugin, installed
with `scancode`, extending it to have the `--analyze-license-results` option.

Install Plugin from Source
--------------------------

``scancode-analyzer`` can be installed as a scancode post-scan plugin.

1. Clone the Repository and navigate to the ``scancode-analyzer`` directory.

2. Configure (Installs the requirements, and scancode-toolkit with the plugin)::

    ./configure

3. Activate the Virtual Environment Created

    source tmp/bin/activate

4. Run scancode for the first time for setup::

    scancode -h

5. Run a scan using the ``--analyze-license-results`` command line options::

    scancode -il --json-pp output.json /path/to/scan_files/ --license-text --is-license-text --classify --analyze-license-results

6. OR, import a JSON scan result and run the plugin on that scan::

    scancode --json-pp results.json --from-json path/to/scan_result.json --analyze-license-results

.. note::

    `scancode-analyzer` has required CLI options, as these produce attributes
    essential to the analysis process. These are:
    `--license --info --license-text --is-license-text --classify`
    Even when loading from json, the scan generating these json files should have
    been run with this options for the analysis plugin to work.


Install plugin via `pip`
------------------------

1. Install all `scancode` `prerequisites`_ and create a `virtualenvironment`_.

2. Run `pip install scancode-analyzer` to install the latest version of Scancode Analyzer.


.. _virtualenvironment: https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-as-a-library-via-pip
.. _prerequisites: https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#prerequisites
