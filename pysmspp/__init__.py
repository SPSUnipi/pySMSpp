"""pySMSpp: Python interface for SMS++ modeling and optimization.

pySMSpp provides a Python interface to create, manipulate, and solve SMS++ 
(Structured Modeling System) models. SMS++ is a framework for structured 
mathematical optimization problems.

Main Features
-------------
- **Model I/O**: Read and write SMS++ models from/to netCDF4 files
- **Model Construction**: Build hierarchical models with blocks, variables, and attributes
- **Model Editing**: Add, remove, or modify model components
- **Solver Integration**: Execute SMS++ solvers and read optimization results
- **Configuration Management**: Create and manage SMS++ solver configurations

Key Classes
-----------
SMSNetwork : Main container for SMS++ optimization models
Block : Hierarchical container for model components (attributes, dimensions, variables)
SMSConfig : Configuration manager for SMS++ solver settings
Variable : Represents model variables with dimensions and data
SMSPPSolverTool : Base class for SMS++ solver integrations

Quick Start
-----------
>>> from pysmspp import SMSNetwork, Block
>>> # Create a new SMS++ model
>>> network = SMSNetwork()
>>> # Add blocks and variables
>>> block = Block(name="my_block")
>>> network.add(block)
>>> # Save to netCDF
>>> network.to_netcdf("model.nc")

See Also
--------
Official SMS++ project: https://gitlab.com/smspp/smspp-project
Documentation: https://pysmspp.readthedocs.io
"""

from pysmspp.block import (
    SMSNetwork as SMSNetwork,
    SMSConfig as SMSConfig,
    Block as Block,
    SMSFileType as SMSFileType,
    Variable as Variable,
    components as components,
    blocks as blocks,
)
from pysmspp.smspp_tools import (
    SMSPPSolverTool as SMSPPSolverTool,
    UCBlockSolver as UCBlockSolver,
    InvestmentBlockTestSolver as InvestmentBlockTestSolver,
    is_smspp_installed as is_smspp_installed,
)
