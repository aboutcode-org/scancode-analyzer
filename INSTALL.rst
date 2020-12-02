Quickstart - Scancode Plugin
----------------------------

``scancode-results-analyzer`` can be installed as a scancode post-scan plugin, using ``pip``.
This is currently work-in-progress.

1. Ensure you have Virtualenv installed.

2. Clone the Repository and navigate to the ``scancode-results-analyzer`` directory.

3. Configure::

    ./configure

4. Activate the Virtual Environment Created

    source tmp/bin/activate

5. Install as a scancode-toolkit plugin::

    pip install -e .

6. Run scancode for the first time for setup::

    scancode -h

7. Run a scan using the ``--analyze-results`` command line options::

    scancode -l --json-pp output.json /path/to/scan_files/ --license-text --analyze-results

8. OR, import a JSON scan result and run the plugin on that scan::

    scancode --json-pp results.json --from-json tests/data/results-test/selective-before-rules-added/only_errors.json --analyze-results


Quickstart - Conda
------------------

Different modules of ``scancode-results-analyzer`` can be imported as python modules, to test their functionality
on scancode JSON scans. They need to be imported by using jupyter-notebooks in a ``conda`` environment.

1. Download and Get Anaconda Installed.

    - `Linux Install Guide`_
    - `MacOS Install Guide`_
    - `Windows Install Guide`_

`Verify your installation`_

2. Navigate to the ``scancode-results-analyzer`` directory.

3. Create the Conda Environment

.. code-block:: bash

    conda env create -f env_files/results-analyzer/environment.yml

4. Activate the Conda Environment

.. code-block:: bash

    conda activate results-analyzer

5. Open Jupyter Lab in this conda environment

.. code-block:: bash

    jupyter lab &

6. Navigate to the ``.ipynb`` file you want to open on the left, and click to open.

7. Run the Cells using ``Shift+Enter``.

8. More Documentation

    - `Jupyter Basics Docs`_
    - `Why Jupyter Lab`_

.. _Linux Install Guide: https://docs.anaconda.com/anaconda/install/linux/
.. _MacOS Install Guide: https://docs.anaconda.com/anaconda/install/mac-os/
.. _Windows Install Guide: https://docs.anaconda.com/anaconda/install/windows/
.. _Verify your installation: https://docs.anaconda.com/anaconda/install/verify-install/
.. _Jupyter Basics Docs: https://realpython.com/jupyter-notebook-introduction/
.. _Why Jupyter Lab: https://towardsdatascience.com/jupyter-lab-evolution-of-the-jupyter-notebook-5297cacde6b
.. _More information on Python virtualenv: https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv
