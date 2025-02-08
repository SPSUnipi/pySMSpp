# SMSpy

[![Tests](https://github.com/SPSUnipi/SMSpy/actions/workflows/test.yml/badge.svg)](https://github.com/SPSUnipi/SMSpy/actions/workflows/test.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SPSUnipi/SMSpy/main.svg)](https://results.pre-commit.ci/latest/github/SPSUnipi/SMSpy/main)

This package aims at providing a python interface to create [SMS++](https://gitlab.com/smspp/smspp-project) models using a simple python interface.
The package aims to support:
- Read/write operations of SMS++ models from/to netCDF4 files
- Add/remove/edit operations model components
- Execution of SMS++ models
- Reading SMS++ results as netCDF4 files


## How to develop

1. First, clone the repository using git:

    ```bash
        git clone https://github.com/SPSUnipi/SMSpy
    ```

2. Create a virtual environment using venv or conda. For exaample, using venv:

    ```bash
        python -m venv .venv
        source .venv/bin/activate
    ```

3. Install the required packages and pre-commit hooks:

    ```bash
        pip install -e .[dev]
        pre-commit install
    ```

4. Develop and test the code. For testing, please run:

    ```bash
        pytest
    ```
