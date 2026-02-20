# How to Contribute

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and you always earn credits.

You can contribute in many ways:

- Submit feedback or bug reports
- Add new features
- Fix bugs
- Write or improve documentation

## Code

### Linting and pre-commit

For every code contribution, the [pre-commit](https://pre-commit.com/index.html) utility should be executed.
This will lint, format and check your code contributions against our guidelines to ensure code quality and consistency:

1. Installation: `pip install pre-commit`
2. Activate on every `git commit`: `pre-commit install`
3. Run manually: `pre-commit run --all`

## Documentation

### How to document?

We add documentation continuously while the project grows, which makes it easier to understand and maintain.
We rely on [MkDocs](https://www.mkdocs.org/) and the [mkdocstrings](https://mkdocstrings.github.io/) plugin to document the package and generate the documentation website.

Feel free to check it yourself by starting to contribute. Every typo fix counts!

### Structure and syntax

The documentation lives in the `docs/` folder. Most files are written in Markdown (`.md`).

There are two types of documentation elements:

1. **Narrative documentation** — Plain Markdown text that explains concepts, installation steps, examples etc.
   Uses standard [Markdown syntax](https://www.markdownguide.org/cheat-sheet/).

2. **Automated API documentation** via `mkdocstrings` — Links Python docstrings directly to the docs pages.
   A minimal example (from `docs/api_reference/block.md`):

   ```markdown
   ## SMSNetwork

   ::: pysmspp.block.SMSNetwork
   ```

   This renders the full docstring of `pysmspp.block.SMSNetwork` automatically.

### Writing docstrings

pySMSpp uses [NumPy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html). Example:

```python
def my_function(param1: int, param2: str = "default") -> bool:
    """
    Short summary of what the function does.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str, optional
        Description of param2. Default is "default".

    Returns
    -------
    bool
        Description of the return value.

    Examples
    --------
    >>> my_function(1, "hello")
    True
    """
    ...
```

### How to build docs locally

To build the documentation locally, you need [MkDocs](https://www.mkdocs.org/) and its plugins.

1. Create and activate a fresh environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

2. Install the documentation requirements:

    ```bash
    pip install -r docs/requirements.txt
    pip install -e .
    ```

3. Build and serve the documentation:

    ```bash
    mkdocs serve
    ```

    This starts a local server at <http://127.0.0.1:8000/> with live reload.

4. To build a static site:

    ```bash
    mkdocs build
    ```

    The output is placed in the `site/` directory.

The documentation is built automatically by [ReadTheDocs](https://pysmspp.readthedocs.io) for every pull request.
