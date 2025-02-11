################
 Installation
################

.. note::
    pySMSpp is a Python package under active development and current documentation aims to facilitate development of the package. Currently, there is not yet a stable release of the package on PyPI or Conda, so the installation can be performed by cloning the repository and installing the package locally.

Python
======

To use pySMSpp we highly recommend to use a package manager such as `conda
<https://docs.conda.io/en/latest/miniconda.html>`_, `mamba
<https://github.com/mamba-org/mamba>`_ or `pip
<https://pip.pypa.io/en/stable/>`_ as easy-to-use package managers, available for Windows, Mac OS X and GNU/Linux.

As common practice, it is highly recommend to use dedicated `conda/mamba environments <https://mamba.readthedocs.io/en/latest/user_guide/mamba.html>`_ or `virtual environments
<https://pypi.python.org/pypi/virtualenv>`_ to ensure .


Adoption of conda environments
==============================

If you are using conda, you can create a new environment with::

    conda create -n pysmspp python=3.10 pip

This will create a new environment named ``pysmspp`` with Python 3.10 and pip package manager installed.

If you prefer mamba, please execute the same command with ``mamba`` instead of ``conda``. For alternative package managers, please refer to their respective documentation.


Clone the package
=================

To clone the package, you can use the following command::

    cd /path/to/your/folder
    git clone https://github.com/SPSUnipi/pySMSpp

This will create a new folder named ``pySMSpp`` in the directory ``/path/to/your/folder``

Installing with pip
===================

You can now install the package locally using pip::

    cd /path/to/your/folder/pySMSpp
    pip install .

If you aim to develop the package, we recommend to install the package in editable mode (option ``-e``) and install the development dependencies (option ``[dev]``)::

    pip install -e .[dev]


Getting SMS++
=============

To use pySMSpp, you need to have SMS++ installed on your system. You can install the latest version of SMS++ from the `official SMS++ website <https://gitlab.com/smspp/smspp-project>`_.

