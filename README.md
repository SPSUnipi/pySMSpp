# pySMSpp

[![Tests](https://github.com/SPSUnipi/pySMSpp/actions/workflows/test.yml/badge.svg)](https://github.com/SPSUnipi/pySMSpp/actions/workflows/test.yml)
[![Documentation Status](https://readthedocs.org/projects/pysmspp/badge/?version=latest)](https://pysmspp.readthedocs.io/en/latest/?badge=latest)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SPSUnipi/pySMSpp/main.svg)](https://results.pre-commit.ci/latest/github/SPSUnipi/pySMSpp/main)

This package aims at providing a python interface to create [SMS++](https://gitlab.com/smspp/smspp-project) models using a simple python interface.
The package aims to support:
- Read/write operations of SMS++ models from/to netCDF4 files
- Add/remove/edit operations model components
- Execution of SMS++ models
- Reading SMS++ results as netCDF4 files


## How to develop

1. First, clone the repository using git:

    ```bash
        git clone https://github.com/SPSUnipi/pySMSpp
    ```

2. Create a virtual environment using venv or conda.
    For exaample, using venv:

    ```bash
        python -m venv .venv
        source .venv/bin/activate
    ```
   
    Alternatively, using conda:

    ```bash
        conda create -n pysmspp python=3.10
        conda activate pysmspp
    ```

3. Install the required packages and pre-commit hooks:

    ```bash
        pip install -e .[dev]
        pre-commit install
    ```

    Note that the `-e` command line option installs the package in editable mode, so that changes to the source code are immediately available in the environment being used. The `[dev]` option installs the packages required for development. The `pre-commit install` command installs the pre-commit hooks, which are used to check the code before committing to ensure code quality standards.

4. Develop and test the code. For testing, please run:

    ```bash
        pytest
    ```
