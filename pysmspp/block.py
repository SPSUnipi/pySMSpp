from pysmspp.components import Dict
from pysmspp.smspp_tools import (
    SMSPPSolverTool,
    UCBlockSolver,
    InvestmentBlockTestSolver,
    InvestmentBlockSolver,
)
from enum import IntEnum

import netCDF4 as nc
import numpy as np
import os
from pathlib import Path
import pandas as pd


NC_DOUBLE = "f8"
NP_DOUBLE = np.float64
NC_UINT = "u4"
NP_UINT = np.uint32

dir_name = os.path.dirname(__file__)
components = pd.read_csv(os.path.join(dir_name, "data", "components.csv"), index_col=0)

blocks = Dict()
for file_name in os.listdir(os.path.join(dir_name, "data", "blocks")):
    if file_name.endswith(".csv"):
        key = file_name.replace(".csv", "")
        file_path = os.path.join(dir_name, "data", "blocks", file_name)
        blk_conf = pd.read_csv(file_path).iloc[:, 1:]
        blk_conf["attribute"] = blk_conf["attribute"].str.replace("*", "")
        blocks[key] = blk_conf.set_index("attribute")


class SMSConfig:
    """
    Configuration manager for SMS++ solver settings.

    SMSConfig manages solver configuration files for SMS++ optimization. It can
    load configurations from file paths or use predefined templates stored in the
    package data directory.

    Configuration files specify solver parameters such as tolerances, iteration
    limits, decomposition strategies, and other optimization settings required by
    SMS++ solvers.

    Attributes
    ----------
    config : str
        The absolute path to the configuration file.

    Examples
    --------
    Load from a template:

    >>> config = SMSConfig(template="UCBlock/uc_solverconfig")

    Load from a file path:

    >>> config = SMSConfig(fp="/path/to/config.txt")

    Get available templates:

    >>> templates = SMSConfig.get_templates()

    See Also
    --------
    SMSNetwork.optimize : Uses SMSConfig for optimization
    """

    def __init__(self, fp: Path | str = None, template: str = None):
        """
        Initialize a SMSConfig object.
        If an existing fp is provided, it is used as the configuration file; an error is thrown if the file does not exist.
        If a template is provided, the configuration file is set to the template file in the data/configs directory.
        fp and template cannot be both None.

        Parameters
        ----------
        fp : Path | str (default: None)
            The path to the configuration file.
        template : str (default: None)
            The template name of the configuration file.
        """
        if fp is None and template is None:
            raise ValueError("Either fp or template must be provided.")
        if fp is not None and template is not None:
            raise ValueError("fp or template cannot be specified together.")

        if template is None:
            fp_p = Path(fp)
            if not fp_p.exists():
                raise FileNotFoundError(f"File {fp} not found.")
            else:
                self._config = str(fp_p.resolve())
        else:
            dirconfigs = Path(dir_name, "data", "configs")
            if not template.endswith(".txt"):
                template = template + ".txt"
            fp_config = Path(dirconfigs, template)
            if fp_config.exists():
                self._config = str(fp_config.resolve())
            else:
                raise FileNotFoundError(
                    f"Template {template} is not found. Supported templates are:\n"
                    + "\n".join(SMSConfig.get_templates())
                )

    def __repr__(self):
        """Return a string representation of the configuration object."""
        return f'Configuration path: "{self.config}"'

    def __str__(self):
        """Return the configuration path as a string."""
        return self.config

    @property
    def config(self):
        """Return the configuration path."""
        return self._config

    @staticmethod
    def get_templates():
        """
        Return the list of available configuration templates.

        Returns
        -------
        list of str
            List of template names available in the data/configs directory.
        """
        dirconfigs = Path(dir_name, "data", "configs")
        return [str(f.relative_to(dirconfigs)) for f in dirconfigs.glob("**/*.txt")]


def get_attr_field(block_type: str, attr_name: str, field: str = None):
    """
    Return the attribute value or field from block configuration.

    Parameters
    ----------
    block_type : str
        The type of the block.
    attr_name : str
        The name of the attribute.
    field : str, optional
        The specific field to retrieve. If None, returns the entire row.

    Returns
    -------
    str or pandas.Series
        The requested field value (str) or entire attribute row (pandas.Series).
    """
    block_attrs = blocks[block_type].query("smspp_object == 'Block'")
    simple_attrs = blocks[block_type].query("smspp_object != 'Block'")

    if attr_name in simple_attrs.index:
        attr = attr_name
    else:
        attr_sel = block_attrs.loc[
            block_attrs.index.to_series().map(lambda x: attr_name.startswith(x))
        ]
        if attr_sel.shape[0] == 1:
            attr = attr_sel.index[0]
        elif attr_sel.empty:
            raise ValueError(f"Attribute {attr_name} not found in block {block_type}.")
        else:
            raise ValueError(
                f"Ambiguous attribute {attr_name} in block {block_type}."
                + f"Possible types: {attr_sel.index.tolist()}."
            )

    if field is None:
        return blocks[block_type].loc[attr]
    else:
        return blocks[block_type].at[attr, field]


class SMSFileType(IntEnum):
    """
    Enumeration of SMS++ file types.

    Defines the different types of files that can be created and managed in SMS++
    systems. Each file type serves a specific purpose in the modeling and
    optimization workflow.

    Attributes
    ----------
    eProbFile : int
        Problem file (value 0): Contains both the model block structure and
        solver configuration. This is the complete specification needed to run
        an optimization.
    eBlockFile : int
        Block file (value 1): Contains only the model structure with blocks,
        variables, dimensions, and attributes. No solver configuration included.
    eConfigFile : int
        Configuration file (value 2): Contains only solver settings and
        parameters. No model structure included.
    eSolutionFile : int
        Solution file (value 3): Contains the optimization results including
        objective values, variable values, and solver status.

    Examples
    --------
    >>> network = SMSNetwork(file_type=SMSFileType.eBlockFile)
    >>> print(SMSFileType.eProbFile)  # Output: 0
    >>> file_type = SMSFileType(1)  # eBlockFile

    See Also
    --------
    SMSNetwork : Uses SMSFileType to specify file format
    """

    eProbFile = 0  # Problem file: Block and Configuration
    eBlockFile = 1  # Block file
    eConfigFile = 2  # Configuration file
    eSolutionFile = 3  # Solution file


class Attribute:
    """
    Represents an attribute in an SMS++ model.

    Attributes store metadata and configuration parameters for blocks in the
    SMS++ hierarchical structure. They can hold string, integer, or floating-point
    values.

    Attributes
    ----------
    name : str
        The name of the attribute.
    value : str | int | float
        The value of the attribute.

    Examples
    --------
    >>> attr = Attribute("block_type", "UCBlock")
    >>> attr = Attribute("TimeHorizon", 24)
    >>> attr = Attribute("LinearTerm", 0.3)
    """

    name: str
    value: str | int | float

    def __init__(self, name: str, value: str | int | float):
        """
        Initialize an Attribute object.

        Parameters
        ----------
        name : str
            The name of the attribute.
        value : str | int | float
            The value of the attribute.
        """
        self.name = name
        self.value = value

    def __str__(self) -> str:
        """Return string representation of the attribute value."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return detailed representation of the attribute."""
        return f"Attribute(name={self.name!r}, value={self.value!r})"

    def __eq__(self, other) -> bool:
        """Compare attribute with another value or Attribute object."""
        if isinstance(other, Attribute):
            return self.name == other.name and self.value == other.value
        return self.value == other


class Dimension:
    """
    Represents a dimension in an SMS++ model.

    Dimensions define the size of arrays and variables in the SMS++ model structure.
    They are used to specify the shape of multi-dimensional variables and data arrays.

    Attributes
    ----------
    name : str
        The name of the dimension.
    value : int
        The size of the dimension (number of elements).

    Examples
    --------
    >>> dim = Dimension("TimeHorizon", 24)
    >>> dim = Dimension("NumberNodes", 2)
    """

    name: str
    value: int

    def __init__(self, name: str, value: int):
        """
        Initialize a Dimension object.

        Parameters
        ----------
        name : str
            The name of the dimension.
        value : int
            The size of the dimension.
        """
        self.name = name
        self.value = value

    def __str__(self) -> str:
        """Return string representation of the dimension value."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return detailed representation of the dimension."""
        return f"Dimension(name={self.name!r}, value={self.value!r})"

    def __eq__(self, other) -> bool:
        """Compare dimension with another value or Dimension object."""
        if isinstance(other, Dimension):
            return self.name == other.name and self.value == other.value
        return self.value == other


class Variable:
    """
    Represents a variable in an SMS++ model.

    Variables hold the data arrays and parameters used in SMS++ optimization models.
    They have a specific type, dimensional structure, and associated data values.

    Attributes
    ----------
    name : str
        The name of the variable.
    var_type : str
        The data type of the variable (e.g., "float", "int", "double").
    dimensions : tuple
        The dimensions of the variable as a tuple of dimension names.
    data : float | list | np.ndarray
        The data values of the variable.

    Examples
    --------
    >>> var = Variable("MinPower", "float", (), 0.0)
    >>> var = Variable("ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), np.full((2, 24), 50.0))
    """

    name: str
    var_type: str
    dimensions: tuple
    data: float | list | np.ndarray

    def __init__(
        self,
        name: str,
        var_type: str,
        dimensions: tuple,
        data: float | list | np.ndarray,
    ):
        """
        Initialize a Variable object.

        Parameters
        ----------
        name : str
            The name of the variable.
        var_type : str
            The data type of the variable (e.g., "float", "int", "double").
        dimensions : tuple
            The dimensions of the variable. Use empty tuple () for scalar values.
        data : float | list | np.ndarray
            The data values of the variable.
        """
        if dimensions is None:
            dimensions = ()
        self.name = name
        self.var_type = var_type
        self.dimensions = dimensions
        self.data = data


class Block:
    """
    Hierarchical container for SMS++ model components.

    A Block is the fundamental building component of SMS++ models, providing a
    hierarchical structure to organize attributes, dimensions, variables, and
    sub-blocks. Blocks can be nested to create complex optimization models with
    multiple layers of structure.

    The Block class supports:
    - Reading from and writing to NetCDF4 files
    - Dynamic construction from attributes, dimensions, variables, and sub-blocks
    - Hierarchical nesting of blocks
    - Type-based component management

    Attributes
    ----------
    attributes : Dict
        Dictionary of Attribute objects containing metadata and parameters.
    dimensions : Dict
        Dictionary of Dimension objects defining array sizes.
    variables : Dict
        Dictionary of Variable objects containing data arrays.
    blocks : Dict
        Dictionary of nested Block objects forming the hierarchy.
    components : Dict
        Configuration dictionary for component types.

    Examples
    --------
    Create an empty block:

    >>> block = Block()

    Create a block from a NetCDF file:

    >>> block = Block(fp="model.nc")

    Create a block with attributes:

    >>> block = Block(attributes={"type": "UCBlock"})

    Create a block with variables using kwargs:

    >>> block = Block(MinPower=Variable("MinPower", "float", (), 0.0))

    See Also
    --------
    SMSNetwork : Network-level block for complete SMS++ models
    Attribute : Metadata storage
    Dimension : Array dimension definition
    Variable : Data array storage
    """

    # Class variables

    _attributes: Dict  # attributes of the block
    _dimensions: Dict  # dimensions of the block
    _variables: Dict  # variables of the block
    _blocks: Dict  # blocks beloning to the block

    components: Dict  # components of the block

    # Constructor

    def __init__(
        self,
        fp: Path | str = "",
        attributes: Dict = None,
        dimensions: Dict = None,
        variables: Dict = None,
        blocks: Dict = None,
        **kwargs,
    ):
        """
        Initialize a Block object.
        A block object can be created from a NetCDF file, or, alternatively, from the given attributes, dimensions, variables, and blocks.
        Moreover, optional additional arguments can be passed to the Block constructor to override the values loaded from files or from the arguments (attributes, dimensions, variables and blocks).

        Example of possible usage:
        >>> Block()
        >>> Block(fp="file.nc")
        >>> Block(attributes={"block_type": "UCBlock"})
        >>> Block(dimensions={"n": 10})
        >>> Block(variables={"var1": Variable("var1", "float", None, 0.0)})
        >>> Block(blocks={"Block_0": Block()})
        >>> Block(fp="file.nc", attributes={"block_type": "UCBlock"})
        >>> Block(MinPower=Variable("MinPower", "float", None, 0.0))

        Parameters
        ----------
        fp : Path | str (default: "")
            The path to the NetCDF file to read.
        attributes : Dict (default: None)
            The attributes of the block.
        dimensions : Dict (default: None)
            The dimensions of the block.
        variables : Dict (default: None)
            The variables of the block.
        blocks : Dict (default: None)
            The blocks of the block.
        kwargs : dict
            The arguments to pass to the Block constructor.
        """
        self.components = Dict(components.T.to_dict())
        if fp:
            obj = self.from_netcdf(fp)
            self._attributes = obj.attributes
            self._dimensions = obj.dimensions
            self._variables = obj.variables
            self._blocks = obj.blocks
        else:
            self._attributes = attributes if attributes else Dict()
            self._dimensions = dimensions if dimensions else Dict()
            self._variables = variables if variables else Dict()
            self._blocks = blocks if blocks else Dict()
        self.from_kwargs(**kwargs)

    def __repr__(self):
        """
        Return a string representation of the Block object.

        Returns
        -------
        str
            A formatted string showing the counts and names of attributes,
            dimensions, variables, and sub-blocks.
        """
        # Extract the keys of the dictionaries
        dim_str = ", ".join(self.dimensions.keys()) if self.dimensions else "None"
        var_str = ", ".join(self.variables.keys()) if self.variables else "None"
        attr_str = ", ".join(self.attributes.keys()) if self.attributes else "None"
        block_str = ", ".join(self.blocks.keys()) if self.blocks else "None"

        return (
            f"Block object\n"
            f"Attributes ({len(self.attributes)}): {attr_str}\n"
            f"Dimensions ({len(self.dimensions)}): {dim_str}\n"
            f"Variables ({len(self.variables)}): {var_str}\n"
            f"Blocks ({len(self.blocks)}): {block_str}"
        )

    # Properties
    @property
    def attributes(self) -> Dict:
        """Return the attributes of the block."""
        return self._attributes

    @property
    def dimensions(self) -> Dict:
        """Return the dimensions of the block."""
        return self._dimensions

    @property
    def variables(self) -> Dict:
        """Return the variables of the block."""
        return self._variables

    @property
    def blocks(self) -> Dict:
        """Return the blocks of the block."""
        return self._blocks

    @property
    def block_type(self, ignore_missing: bool = True) -> str:
        """Return the type of the block."""
        if "type" in self.attributes:
            attr = self.attributes["type"]
            return attr.value if isinstance(attr, Attribute) else attr
        elif ignore_missing:
            return None
        raise AttributeError("Block type not defined.")

    @block_type.setter
    def block_type(self, block_type: str):
        """
        Set the type of the block.

        Parameters
        ----------
        block_type : str
            The type of the block.
        """
        self.attributes["type"] = Attribute("type", block_type)

    def add_attribute(self, name: str, *args, force: bool = False, **kwargs):
        """
        Add an attribute to the block.

        Parameters
        ----------
        name : str
            The name of the attribute
        value : any
            The value of the attribute. Can be provided as a positional argument
            or as an Attribute object.
        force : bool (default: False)
            If True, overwrite the attribute if it exists.

        Returns
        -------
        Attribute
            Returns the Attribute object being created.
        """
        if not force and name in self.attributes:
            raise ValueError(f"Attribute {name} already exists.")
        if len(args) == 1:
            if isinstance(args[0], Attribute):
                self.attributes[name] = args[0]
            else:
                self.attributes[name] = Attribute(name, args[0])
        else:
            raise ValueError("Attribute value must be provided as a single argument.")
        return self.attributes[name]

    def add_dimension(self, name: str, *args, force: bool = False, **kwargs):
        """
        Add a dimension to the block.

        Parameters
        ----------
        name : str
            The name of the dimension
        value : int
            The value of the dimension. Can be provided as a positional argument
            or as a Dimension object.
        force : bool (default: False)
            If True, overwrite the dimension if it exists.

        Returns
        -------
        Dimension
            Returns the Dimension object being created.
        """
        if not force and name in self.dimensions:
            raise ValueError(f"Dimension {name} already exists.")
        if len(args) == 1:
            if isinstance(args[0], Dimension):
                self.dimensions[name] = args[0]
            else:
                self.dimensions[name] = Dimension(name, args[0])
        else:
            raise ValueError("Dimension value must be provided as a single argument.")
        return self.dimensions[name]

    def add_variable(
        self,
        name,
        *args,
        force: bool = False,
        **kwargs,
    ):
        """
        Add a variable to the block.

        Parameters
        ----------
        name : str
            The name of the variable
        var_type : str
            The type of the variable
        dimensions : tuple
            The dimensions of the variable
        data : float | list | np.ndarray
            The data of the variable
        force : bool (default: False)
            If True, overwrite the variable if it exists.

        Returns
        -------
        Returns the variable being created.
        """
        if not force and name in self.variables:
            raise ValueError(f"Variable {name} already exists.")
        if len(args) == 1:
            assert isinstance(args[0], Variable), "args must be a Variable object."
            self.variables[name] = args[0]
        else:
            self.variables[name] = Variable(name, *args, **kwargs)
        return self.variables[name]

    def add_block(self, name: str, *args, **kwargs):
        """
        Add a block.

        >>> add_block("Block_0", block=Block())
        >>> add_block("Block_0", Block())
        >>> add_block("Block_0", **kwargs})

        Parameters
        ----------
        name : str
            The name of the block
        args : list
            The arguments to pass to the Block constructor.
            If a Block argument is passed, it is used as the block.
        kwargs : dict
            The attributes of the block.
            If the argument "block" is present, the block is set to that value.
            Otherwise, arguments are passed to the Block constructor.

        Returns
        -------
        Returns the block being created.
        """
        force = kwargs.pop("force", False)
        if not force and name in self.blocks:
            raise ValueError(f"Block {name} already exists.")
        if "block" in kwargs:
            if not isinstance(kwargs["block"], Block):
                raise ValueError("block must be a Block object.")
            self.blocks[name] = kwargs["block"]
        elif len(args) >= 1:
            if len(args) == 1 and isinstance(args[0], Block):
                self.blocks[name] = args[0]
            else:
                raise ValueError("Non accepted arguments have been passed.")
        else:
            self.blocks[name] = Block().from_kwargs(**kwargs)
        return self

    def from_kwargs(self, **kwargs):
        """
        Populate the Block from keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing block components. If 'block_type' is
            provided, it sets the block type and other arguments are added as
            components based on the block type configuration.

        Returns
        -------
        Block
            Returns self for method chaining.
        """
        if "block_type" in kwargs:
            btype = kwargs.pop("block_type")
            self.block_type = btype
        for key, value in kwargs.items():
            nc_cmp = get_attr_field(self.block_type, key, "smspp_object")
            self.add(nc_cmp, key, value)
        return self

    # Input/Output operations

    def _to_netcdf_helper(self, grp: nc.Dataset | nc.Group):
        """
        Recursively save Block and sub-blocks to a NetCDF group.

        Parameters
        ----------
        grp : netCDF4.Dataset or netCDF4.Group
            The NetCDF dataset or group to write to.
        """
        # Add the block's attributes
        for key, attr in self.attributes.items():
            value = attr.value if isinstance(attr, Attribute) else attr
            grp.setncattr(key, value)

        # Add the dimensions
        for key, dim in self.dimensions.items():
            value = dim.value if isinstance(dim, Dimension) else dim
            grp.createDimension(key, value)

        # Add the variables
        for key, value in self.variables.items():
            var = grp.createVariable(key, value.var_type, value.dimensions)
            var[:] = value.data

        # Save each sub-Block as a subgroup
        for key, sub_block in self.blocks.items():
            subgrp = grp.createGroup(key)
            sub_block._to_netcdf_helper(subgrp)

    def to_netcdf(self, fp: Path | str, force: bool = False):
        """
        Write the SMSNetwork object to a netCDF4 file.

        Parameters
        ----------
        fp : Path | str
            The path to the file to write.
        force : bool (default: False)
            If True, overwrite the file if it exists.
        """
        if not force and os.path.exists(fp):
            raise FileExistsError("File already exists; reading file not implemented.")

        with nc.Dataset(fp, "w") as ds:
            self._to_netcdf_helper(ds)

    @classmethod
    def _from_netcdf(cls, grb: nc.Dataset | nc.Group):
        """
        Recursively load Block and sub-blocks from a NetCDF group.

        Parameters
        ----------
        grb : netCDF4.Dataset or netCDF4.Group
            The NetCDF dataset or group to read from.

        Returns
        -------
        Block
            A new Block instance populated with data from the NetCDF group.
        """
        # Create a new block
        new_block = cls()

        # Retrieve attributes
        for name in grb.ncattrs():
            new_block.add_attribute(name, grb.getncattr(name), force=True)

        # Retrieve dimensions
        for dimname, dimobj in grb.dimensions.items():
            new_block.add_dimension(dimname, dimobj.size)

        # Retrieve variables
        for varname, varobj in grb.variables.items():
            new_block.add_variable(
                varname,
                var_type=varobj.dtype,
                dimensions=varobj.dimensions,
                data=varobj[:],
            )

        # Recursively load sub-blocks
        for subgrp_name, subgrb in grb.groups.items():
            new_block.add_block(subgrp_name, block=Block._from_netcdf(subgrb))

        return new_block

    @classmethod
    def from_netcdf(cls, filename):
        """
        Deserialize a NetCDF file to create a Block instance.

        Parameters
        ----------
        filename : str or Path
            Path to the NetCDF file to read.

        Returns
        -------
        Block
            A new Block instance with nested sub-blocks from the file.
        """
        with nc.Dataset(filename, "r") as ncfile:
            return cls._from_netcdf(ncfile)

    # Functions

    def add(self, component_name, name, *args, **kwargs):
        """
        Add a component to the block.

        Dispatches to the appropriate add method based on component type.

        Parameters
        ----------
        component_name : str
            The SMS++ component class name (e.g., 'Attribute', 'Dimension',
            'Variable', or a Block type).
        name : str
            The name of the component to add.
        *args : tuple
            Positional arguments passed to the specific add method.
        **kwargs : dict
            Keyword arguments passed to the specific add method.

        Returns
        -------
        Attribute, Dimension, Variable, or Block
            The created component object.
        """
        component_nctype = self.components[component_name]["nctype"]
        if component_nctype == "Attribute":
            return self.add_attribute(name, *args, **kwargs)
        elif component_nctype == "Dimension":
            return self.add_dimension(name, *args, **kwargs)
        elif component_nctype == "Variable":
            return self.add_variable(name, *args, **kwargs)
        elif component_nctype == "Block":
            return self.add_block(name, *args, block_type=component_name, **kwargs)
        else:
            raise ValueError(f"Class {component_name} not supported.")

    # Utilities

    def remove(self, component_name: str, name: str):
        """
        Remove a component from the block.

        Parameters
        ----------
        component_name : str
            The SMS++ component class name.
        name : str
            The name of the component to remove.

        Returns
        -------
        Attribute, Dimension, Variable, or Block
            The removed component object.
        """
        return self.static(component_name).pop(name)

    def static(self, component_name: str) -> Dict:
        """
        Return the Dictionary of static components for component_name.
        For example, for component_name = "attribute", the Dictionary of attributes is returned.

        Parameters
        ----------
        component_name : string

        Returns
        -------
        Dict

        """
        return getattr(self, self.components[component_name]["list_name"])

    def print_tree(
        self,
        name: str = None,
        show_dimensions: bool = False,
        show_variables: bool = False,
        show_attributes: bool = False,
        _indent: str = "",
        _is_last: bool = True,
        _is_root: bool = True,
    ) -> None:
        """
        Print a tree representation of the block structure.

        This method displays the hierarchical structure of blocks in a tree format,
        with optional display of dimensions, variables, and attributes.

        Parameters
        ----------
        name : str, optional
            The name of the block. If not provided, uses the block_type if available,
            otherwise defaults to "Block".
        show_dimensions : bool, optional
            Whether to display dimensions (default: False).
        show_variables : bool, optional
            Whether to display variables (default: False).
        show_attributes : bool, optional
            Whether to display attributes (default: False).
        _indent : str, optional
            Internal parameter for indentation (default: "").
        _is_last : bool, optional
            Internal parameter to track if this is the last child (default: True).
        _is_root : bool, optional
            Internal parameter to track if this is the root node (default: True).

        Examples
        --------
        >>> from pysmspp import Block
        >>> block = Block(fp="network.nc4")
        >>> block.print_tree()  # Uses block_type as name
        UCBlock [UCBlock]
        └── Block_0 [UCBlock]
            ├── UnitBlock_0 [ThermalUnitBlock]
            └── UnitBlock_1 [BatteryUnitBlock]

        >>> block.print_tree("MyNetwork")  # Uses custom name
        MyNetwork [UCBlock]
        └── Block_0 [UCBlock]
            ...

        >>> block.print_tree(show_dimensions=True, show_variables=True)
        UCBlock [UCBlock]
          Dimensions (2): n=10, m=5
          Variables (3): var1, var2, var3
        └── Block_0 [UCBlock]
            ...
        """
        # Determine the name to use
        if name is None:
            # Use block_type if available, otherwise default to "Block"
            if hasattr(self, "block_type") and self.block_type:
                name = self.block_type
            else:
                name = "Block"

        # Get block type - if it's None or missing, we'll omit the brackets
        block_type = None
        if hasattr(self, "block_type") and self.block_type:
            block_type = self.block_type

        # Print the current block
        if _is_root:
            # Root level - no connector
            if block_type:
                print(f"{name} [{block_type}]")
            else:
                print(f"{name}")
            child_indent = ""
        else:
            connector = "└── " if _is_last else "├── "
            if block_type:
                print(f"{_indent}{connector}{name} [{block_type}]")
            else:
                print(f"{_indent}{connector}{name}")
            child_indent = _indent + ("    " if _is_last else "│   ")

        # Print dimensions if requested
        if show_dimensions and self.dimensions:
            dims_str = ", ".join(
                f"{key}={value}" for key, value in self.dimensions.items()
            )
            detail_indent = child_indent if not _is_root else "  "
            print(f"{detail_indent}Dimensions ({len(self.dimensions)}): {dims_str}")

        # Print variables if requested
        if show_variables and self.variables:
            vars_list = list(self.variables.keys())
            if len(vars_list) <= 5:
                vars_str = ", ".join(vars_list)
            else:
                vars_str = ", ".join(vars_list[:5]) + f", ... ({len(vars_list)} total)"
            detail_indent = child_indent if not _is_root else "  "
            print(f"{detail_indent}Variables ({len(self.variables)}): {vars_str}")

        # Print attributes if requested (exclude 'type' since it's shown in brackets)
        if show_attributes and self.attributes:
            attrs = {k: v for k, v in self.attributes.items() if k != "type"}
            if attrs:
                attrs_list = [f"{k}={v}" for k, v in list(attrs.items())[:5]]
                if len(attrs) <= 5:
                    attrs_str = ", ".join(attrs_list)
                else:
                    attrs_str = ", ".join(attrs_list) + f", ... ({len(attrs)} total)"
                detail_indent = child_indent if not _is_root else "  "
                print(f"{detail_indent}Attributes ({len(attrs)}): {attrs_str}")

        # Recursively print sub-blocks
        if self.blocks:
            sub_blocks = list(self.blocks.items())
            for i, (sub_name, sub_block) in enumerate(sub_blocks):
                is_last_child = i == len(sub_blocks) - 1
                sub_block.print_tree(
                    sub_name,
                    show_dimensions,
                    show_variables,
                    show_attributes,
                    child_indent,
                    is_last_child,
                    False,
                )


class SMSNetwork(Block):
    """
    Top-level network container for SMS++ optimization models.

    SMSNetwork is the main entry point for creating and managing complete SMS++
    models. It extends Block with network-specific functionality including file
    type management and optimization execution.

    An SMSNetwork can contain multiple blocks organized hierarchically to represent
    complex optimization problems such as unit commitment, investment planning, or
    multi-stage stochastic problems.

    Attributes
    ----------
    file_type : SMSFileType
        The type of SMS++ file (eProbFile, eBlockFile, eConfigFile, or eSolutionFile).
    attributes : Dict
        Inherited from Block. Network-level attributes.
    dimensions : Dict
        Inherited from Block. Network-level dimensions.
    variables : Dict
        Inherited from Block. Network-level variables.
    blocks : Dict
        Inherited from Block. Nested blocks forming the model structure.

    Examples
    --------
    Create an empty network:

    >>> network = SMSNetwork()

    Create a network with block file type:

    >>> network = SMSNetwork(file_type=SMSFileType.eBlockFile)

    Load a network from file:

    >>> network = SMSNetwork(fp="model.nc")

    Create and optimize a network:

    >>> network = SMSNetwork(file_type=SMSFileType.eBlockFile)
    >>> network.add("UCBlock", "Block_0", TimeHorizon=24, NumberUnits=1)
    >>> result = network.optimize(config, temp_file, output_file)

    See Also
    --------
    Block : Base class for hierarchical components
    SMSConfig : Configuration manager for SMS++ solvers
    SMSFileType : Enumeration of file types
    """

    def __init__(
        self,
        fp: Path | str = "",
        file_type: SMSFileType | int = SMSFileType.eProbFile,
        **kwargs,
    ):
        """
        Initialize an SMSNetwork object.

        Creates a new SMS++ network, either empty, from a file, or with specified
        components. The file_type determines how the network will be stored and used.

        Parameters
        ----------
        fp : Path | str, optional
            Path to a NetCDF file to load the network from. If provided, the network
            is loaded from the file. Default is empty string (create empty network).
        file_type : SMSFileType | int, optional
            The type of SMS++ file to create. Options:
            - eProbFile (0): Problem file with block and configuration
            - eBlockFile (1): Block file only (no configuration)
            - eConfigFile (2): Configuration file only
            - eSolutionFile (3): Solution file
            Default is eProbFile.
        **kwargs : dict
            Additional keyword arguments to pass to the Block constructor for
            dynamic component creation.

        Examples
        --------
        >>> network = SMSNetwork()
        >>> network = SMSNetwork(file_type=SMSFileType.eBlockFile)
        >>> network = SMSNetwork(fp="existing_model.nc")
        """
        if fp:
            super().__init__()
            sms_network = self.from_netcdf(fp)
            self._attributes = sms_network.attributes
            self._dimensions = sms_network.dimensions
            self._variables = sms_network.variables
            self._blocks = sms_network.blocks
        else:
            super().__init__(**kwargs)
            self.file_type = file_type

    def __repr__(self):
        """
        Return a string representation of the SMSNetwork object.

        Returns
        -------
        str
            A formatted string identifying this as an SMSNetwork with its components.
        """
        return f"SMSNetwork Object\n{super().__repr__()}"

    @property
    def file_type(self) -> SMSFileType:
        """Return the file type of the SMS file."""
        return SMSFileType(self._attributes["SMS++_file_type"])

    @file_type.setter
    def file_type(self, ft: SMSFileType | int):
        """Return the file type of the SMS file."""
        self._attributes["SMS++_file_type"] = int(ft)

    @classmethod
    def _from_netcdf(cls, ncfile: nc.Dataset):
        """Deserialize a NetCDF file to create a Block instance with nested sub-blocks."""
        blk = super()._from_netcdf(ncfile)
        file_type = ncfile.getncattr("SMS++_file_type")
        return SMSNetwork(
            file_type=file_type,
            attributes=blk.attributes,
            dimensions=blk.dimensions,
            variables=blk.variables,
            blocks=blk.blocks,
        )

    def print_tree(
        self,
        name: str = None,
        show_dimensions: bool = False,
        show_variables: bool = False,
        show_attributes: bool = False,
        _indent: str = "",
        _is_last: bool = True,
        _is_root: bool = True,
    ) -> None:
        """
        Print a tree representation of the SMSNetwork structure.

        This method overrides Block.print_tree() to use "SMSNetwork" as the default name.

        Parameters
        ----------
        name : str, optional
            The name of the network. If not provided, defaults to "SMSNetwork".
        show_dimensions : bool, optional
            Whether to display dimensions (default: False).
        show_variables : bool, optional
            Whether to display variables (default: False).
        show_attributes : bool, optional
            Whether to display attributes (default: False).
        _indent : str, optional
            Internal parameter for indentation (default: "").
        _is_last : bool, optional
            Internal parameter to track if this is the last child (default: True).
        _is_root : bool, optional
            Internal parameter to track if this is the root node (default: True).

        Examples
        --------
        >>> from pysmspp import SMSNetwork
        >>> net = SMSNetwork(fp="network.nc4")
        >>> net.print_tree()  # Uses "SMSNetwork" as default name
        SMSNetwork
        └── Block_0 [UCBlock]
            ...
        """
        # Use "SMSNetwork" as default name for SMSNetwork objects
        if name is None:
            name = "SMSNetwork"

        # Call parent class method
        super().print_tree(
            name=name,
            show_dimensions=show_dimensions,
            show_variables=show_variables,
            show_attributes=show_attributes,
            _indent=_indent,
            _is_last=_is_last,
            _is_root=_is_root,
        )

    def optimize(
        self,
        configfile: SMSConfig | Path | str,
        fp_temp: Path | str = "temp.nc",
        fp_log: Path | str = None,
        fp_solution: Path | str = None,
        smspp_solver: SMSPPSolverTool | str = "auto",
        inner_block_name: str = "Block_0",
        **kwargs,
    ):
        """
        Optimize the SMSNetwork object.

        Parameters
        ----------
        configfile : SMSConfig | Path | str
            The configuration file. If a path is provided, it is first parsed into a SMSConfig object.
        fp_temp : Path | str (default: "temp.nc")
            The path to the temporary file.
        fp_log : Path | str (default: None)
            The path to the log file.
        fp_solution : Path | str (default: None)
            The path to the solution file.
        smspp_tool : SMSPPSolverTool | str (default: "auto")
            The optimization mode. It supports a SMSPPSolverTool or string-based values.
            If string value is passed, the supported values are:

            - "auto": Automatically select the optimization mode by the type of the inner block.
              If UCBlock, then it selects UCBlockSolver.
            - "UCBlockSolver": Use the UCBlockSolver tool.

        inner_block_name : str (default: "Block_0")
            The name of the inner block, to decide on the automatic solver to use.
        kwargs : dict
            The arguments to pass to the optimization function.
        """

        # Map block type to default solver (for 'auto' mode)
        default_solver_map = {
            "UCBlock": "UCBlockSolver",
            "InvestmentBlock": "InvestmentBlockTestSolver",
            "SDDPBlock": "InvestmentBlockSolver",
        }

        # Map solver names to actual solver classes
        solver_factory = {
            "UCBlockSolver": UCBlockSolver,
            "InvestmentBlockTestSolver": InvestmentBlockTestSolver,
            "InvestmentBlockSolver": InvestmentBlockSolver,
        }

        if isinstance(smspp_solver, str) and smspp_solver == "auto":
            ib = self.blocks[inner_block_name]
            try:
                smspp_solver = default_solver_map[ib.block_type]
            except KeyError:
                raise ValueError(
                    f'"auto" smspp_solver option not supported for block type {ib.block_type}.'
                )
        # Instantiate solver
        if isinstance(smspp_solver, str):
            try:
                solver_class = solver_factory[smspp_solver]
            except KeyError:
                raise ValueError(f"SMS++ tool {smspp_solver} not supported.")

            if not isinstance(configfile, SMSConfig):
                configfile = SMSConfig(configfile)
            smspp_solver = solver_class(
                configfile=str(configfile),
                fp_network=fp_temp,
                fp_solution=fp_solution,
                fp_log=fp_log,
                **kwargs,
            )

        self.to_netcdf(fp_temp, force=True)
        return smspp_solver.optimize(**kwargs)
