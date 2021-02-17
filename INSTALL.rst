Quickstart - Scancode Plugin
----------------------------

``scancode-results-analyzer`` can be installed as a scancode post-scan plugin,
using ``pip``.

1. Clone the Repository and navigate to the ``scancode-results-analyzer`` directory.

2. Configure::

    ./configure

3. Activate the Virtual Environment Created

    source tmp/bin/activate

4. Run scancode for the first time for setup::

    scancode -h

5. Run a scan using the ``--analyze-license-results`` command line options::

    scancode -l --json-pp output.json /path/to/scan_files/ --license-text --is-license-text --classify --analyze-license-results

6. OR, import a JSON scan result and run the plugin on that scan::

    scancode --json-pp results.json --from-json tests/data/results-test/selective-before-rules-added/only_errors.json --analyze-license-results

.. note::

    `scancode-results-analyzer` has required CLI options, as these produce attributes
    essential to the analysis process. These are:
    `--license --info --license-text --is-license-text --classify`
    Even when loading from json, the scan generating these json files should have
    been run with this options for the analysis plugin to work.

