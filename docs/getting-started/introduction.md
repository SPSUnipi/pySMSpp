# Introduction

## What is pySMSpp?

pySMSpp is a Python package to interface [Structured Modeling System for mathematical models (SMS++)](https://smspp.gitlab.io/smspp-project/) with Python. It provides a basic interface to interact with SMS++ and to perform simulations using SMS++.

The package is under active development and the current documentation aims to facilitate the development of the package. Currently, there is not yet a stable release of the package on PyPI or Conda, so the installation can be performed by cloning the repository and installing the package locally.

## What is SMS++?

SMS++ is a software tool for advanced optimization of mathematical models by adopting advanced decomposition tools.
It is a collection of C++ classes for modeling complex, block-structured mathematical models and solving them via sophisticated, structure-exploiting algorithms such as decomposition methods and specialized Interior-Point approaches.

SMS++ preserves the block-structure of the model and allows the user to define the model in terms of blocks, which can be solved by different solvers. Each block may describe a specific physical system to model (e.g. a generator of a power system) or a specific mathematical structure (e.g. to allow Lagrangian relaxation). Each block may be characterized by a set of variables, constraints, and objectives, and may be solved by highly specialized solvers and decomposition techniques. As each block is solved by a specialized solver, the overall solution process is highly efficient and can exploit the structure of the model.

SMS++ supports a hierarchical model structure, where blocks may contain other blocks. This allows the user to define complex models in a modular way, where each block can be solved by a specialized solver. The nested structure combined with the specialized solvers allows the user to exploit the structure of the model and aims to break down computational resources to solve large-scale models.

For more information about SMS++, please refer to the [SMS++ website](https://smspp.gitlab.io/smspp-project/).

## Why pySMSpp?

As mentioned above SMS++ is a powerful tool for solving complex mathematical models. To facilitate user interaction with SMS++, we developed pySMSpp, a Python package that provides a basic interface to interact with SMS++ and to perform simulations using SMS++.

pySMSpp relies on the input/output modelling interface of SMS++ using [netCDF4 data format](https://unidata.github.io/netcdf4-python/). The netCDF4 data format allows to preserve the hierarchical block structure of the model and to store the model data in a structured way. pySMSpp provides a set of classes and functions to define the model in Python, alongside interfaces to write, read and optimize SMS++ models.
