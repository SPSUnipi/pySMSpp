# Contributing

Thank you for your interest in contributing to pySMSpp! This guide covers how to contribute to the codebase as well as to the documentation.

## Contributing to the Code

### Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/SPSUnipi/pySMSpp
    cd pySMSpp
    ```

2. Create a virtual environment (using venv or conda):

    ```bash
    # Using venv
    python -m venv .venv
    source .venv/bin/activate

    # Or using conda
    conda create -n pysmspp python=3.12
    conda activate pysmspp
    ```

3. Install the package in editable mode with development dependencies and pre-commit hooks:

    ```bash
    pip install -e ".[dev]"
    pre-commit install
    ```

### Running Tests

Run the test suite with:

```bash
pytest
```

### Code Style

Code style is enforced automatically by [ruff](https://docs.astral.sh/ruff/) via pre-commit hooks. To run the hooks manually:

```bash
pre-commit run --all-files
```

### Submitting Changes

1. Create a new branch for your feature or fix.
2. Make your changes and add tests if applicable.
3. Ensure the tests and pre-commit hooks pass.
4. Open a pull request describing your changes.

## Contributing to the Documentation

### Setup

Install the documentation dependencies:

```bash
pip install -e ".[dev,docs]"
```

### Building Documentation Locally

To preview the documentation locally:

```bash
mkdocs serve
```

Then open your browser at `http://127.0.0.1:8000`.

To build the static site:

```bash
mkdocs build
```

### Adding New Pages

1. Create a new Markdown file in the appropriate `docs/` subdirectory.
2. Add the page to the `nav` section of `mkdocs.yml`.

### Writing Docstrings

Python docstrings are automatically included in the API reference using `mkdocstrings`. Follow the [NumPy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html). Example:

```python
def my_function(param1: int, param2: str) -> bool:
    """Short description of the function.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.

    Returns
    -------
    bool
        Description of the return value.
    """
```

### Adding Notebooks

Place Jupyter notebooks in `docs/examples/` and add them to the `nav` section in `mkdocs.yml` under Examples.
