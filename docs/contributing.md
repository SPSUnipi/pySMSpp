# Contributing to Documentation

This guide explains how to contribute to the pySMSpp documentation.

## Setup

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

## Building Documentation Locally

To build the documentation locally:

```bash
mkdocs serve
```

Then open your browser at `http://127.0.0.1:8000`.

## Adding New Pages

1. Create a new Markdown file in the appropriate `docs/` subdirectory.
2. Add the page to the `nav` section of `mkdocs.yml`.

## Writing Docstrings

Python docstrings are automatically included in the API reference using `mkdocstrings`. Follow the NumPy docstring format.

## Adding Notebooks

Place Jupyter notebooks in `examples/notebooks/` and add them to the `nav` section in `mkdocs.yml` under Examples.
