# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import subprocess


def _install_smspp():
    """
    Clone and install the smspp-project with the desired flags.
    Modify environment variables as needed for GitHub Actions.
    """
    # 1. Clone the repository
    subprocess.check_call(
        ["git", "clone", "-b", "develop", "https://gitlab.com/smspp/smspp-project.git"]
    )

    # 2. cd into it
    os.chdir("smspp-project")

    # 3. Make INSTALL.sh executable
    subprocess.check_call(["chmod", "+x", "./INSTALL.sh"])

    # 4. Run INSTALL.sh with the flags you desire
    subprocess.check_call(
        [
            "sudo",
            "./INSTALL.sh",
            "--without-scip",
            "--without-gurobi",
            "--without-cplex",
        ]
    )

    # 5. Update the current process's PATH
    #
    # Example: Prepend the SMSPP bin & test paths to the PATH.
    os.environ["PATH"] = (
        "/opt/smspp-project/bin:"
        "/opt/smspp-project/build/InvestmentBlock/test:" + os.environ["PATH"]
    )

    # 6. Update the current process's LD_LIBRARY_PATH
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if current_ld_path:
        os.environ["LD_LIBRARY_PATH"] = f"/opt/smspp-project/lib:{current_ld_path}"
    else:
        # if it was not set at all, just assign the path
        os.environ["LD_LIBRARY_PATH"] = "/opt/smspp-project/lib"

    # 7. cd back to the parent (doc source root, presumably)
    os.chdir("$HOME")


try:
    _install_smspp()
except Exception as e:
    print(f"WARNING: Failed to install smspp-project: {e}")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pySMSpp"
# copyright = '2025, '
author = "Davide Fioriti"


# version = 'v0.0.1'
# release = 'v0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_reredirects",
    "nbsphinx",
    "nbsphinx_link",
]

autodoc_default_flags = ["members"]
autosummary_generate = True

source_suffix = ".rst"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "sphinx_book_theme"
html_theme = "sphinx_rtd_theme"

# html_theme_options = {
#     # "repository_url": "https://github.com/SPSUnipi/pySMSpp",
#     # "use_repository_button": True,
#     # "show_navbar_depth": 1,
#     # "show_toc_level": 2,
# }

html_static_path = ["_static"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

nbsphinx_allow_errors = True
