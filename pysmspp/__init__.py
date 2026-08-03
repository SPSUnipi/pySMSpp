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
Attribute : Represents model attributes with name and value
Dimension : Represents model dimensions with name and size
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
    Attribute as Attribute,
)
from pysmspp.block import (
    Block as Block,
)
from pysmspp.block import (
    Dimension as Dimension,
)
from pysmspp.block import (
    SMSConfig as SMSConfig,
)
from pysmspp.block import (
    SMSFileType as SMSFileType,
)
from pysmspp.block import (
    SMSNetwork as SMSNetwork,
)
from pysmspp.block import (
    Variable as Variable,
)
from pysmspp.block import (
    blocks as blocks,
)
from pysmspp.block import (
    components as components,
)
from pysmspp.smspp_tools import (
    InvestmentBlockSolver as InvestmentBlockSolver,
)
from pysmspp.smspp_tools import (
    InvestmentBlockTestSolver as InvestmentBlockTestSolver,
)
from pysmspp.smspp_tools import (
    SDDPSolver as SDDPSolver,
)
from pysmspp.smspp_tools import (
    SMSPPSolverTool as SMSPPSolverTool,
)
from pysmspp.smspp_tools import (
    TSSBSolver as TSSBSolver,
)
from pysmspp.smspp_tools import (
    UCBlockSolver as UCBlockSolver,
)
from pysmspp.smspp_tools import (
    is_smspp_installed as is_smspp_installed,
)
