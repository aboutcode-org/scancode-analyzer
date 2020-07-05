# scancode-results-analyzer

## What is Scancode-Results-Analyzer

[Scancode Toolkit](https://github.com/nexB/scancode-toolkit) ScanCode detects licenses, copyrights, package manifests 
and direct dependencies and more both in source code and binary files. 

ScanCode license detection is using multiple techniques to accurately detect licenses based on automatons, inverted 
indexes and multiple sequence alignments. The detection is not always accurate enough. The goal of this project is to 
improve the accuracy of license detection leveraging the ClearlyDefined data set, where ScanCode is used to massively
scan millions of packages.

This project aims to:

- write tools and create models to massively analyze the accuracy of license detection
- detect areas where the accuracy could be improved. 
- Write reusable tools and models to assist in the semi-automated reviews of scan results. 
- It will also create new license detection rules semi-automatically to fix the detected anomalies

## Quickstart - Local Machine

1. Download and Get Anaconda Installed.

    - [Linux Install Guide](https://docs.anaconda.com/anaconda/install/linux/)
    - [MacOS Install Guide](https://docs.anaconda.com/anaconda/install/mac-os/)
    - [Windows Install Guide](https://docs.anaconda.com/anaconda/install/windows/)

    [Verify your installation](https://docs.anaconda.com/anaconda/install/verify-install/)  

2. Navigate to the `scancode-results-analyzer` directory.

3. Create the Conda Environment

    Run `conda env create -f env_files/load_into_dataframes/environment.yml`
    
4. Activate the Conda Environment 

    Run `conda activate results-analyzer-load`
    
5. Open Jupyter Lab in this conda environment

    `jupyter lab`

6. Navigate to the `.ipynb` file you want to open on the left, and click to open.

7. Run the Cells using `Shift+Enter`. 

8. More Documentation

    - [Jupyter Basics Docs](https://realpython.com/jupyter-notebook-introduction/)
    - [Why Jupyter Lab](https://towardsdatascience.com/jupyter-lab-evolution-of-the-jupyter-notebook-5297cacde6b)

## Quickstart - Google Colab

1. Every Jupyter Notebook (i.e. `.ipynb` files) has a `Open In Colab` Badge like this - 
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nexB/scancode-results-analyzer/blob/master/src/notebooks/mock_db_data_from_json.ipynb)

2. Clicking that Opens the Jupyter Notebook in [Google Colab](https://colab.research.google.com/notebooks/intro.ipynb). 
Then Run the First Two Group of Cells that do the following tasks.

3. Cloning the [`scancode-results-analyzer` GitHub Repository](https://github.com/nexB/scancode-results-analyzer/) 
so that the Classes/Data can be loaded into the Jupyter Notebook Environment.

4. Installing conda and some additional requirements from the `environment.yml` File.

5. Everything is set up and the Code is Ready To Execute.

## GSoC Project Details

- Name: Improve ScanCode License detection accuracy, by leveraging the ClearlyDefined dataset of Scans
- Year: 2020
- [Link to Project in GSoC website](https://summerofcode.withgoogle.com/projects/#6265001049849856)
- [Link to Proposal](https://github.com/nexB/scancode-results-analyzer/blob/master/docs/gsoc-proposal.pdf)
- [Link to Project Kanban Board for GSoC Phase #1](https://github.com/nexB/scancode-toolkit/projects/7)
- Mentors and Reviewers:
    1. [@pombredanne](https://github.com/pombredanne)
    2. [@majurg](https://github.com/majurg)
    3. [@arnav-mandal1234](https://github.com/arnav-mandal1234)
    4. [@singh1114](https://github.com/singh1114)
- Author: [@AyanSinhaMahapatra](https://github.com/AyanSinhaMahapatra)
