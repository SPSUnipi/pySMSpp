from smspy.components import Dict
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
components = pd.read_csv(os.path.join(dir_name, "components.csv"), index_col=0)

blocks = Dict()
for file_name in os.listdir(os.path.join(dir_name, "blocks")):
    if file_name.endswith(".csv"):
        key = file_name.replace(".csv", "")
        file_path = os.path.join(dir_name, "blocks", file_name)
        blk_conf = pd.read_csv(file_path).iloc[:, 1:]
        blk_conf["attribute"] = blk_conf["attribute"].str.replace("*", "")
        blocks[key] = blk_conf.set_index("attribute")


def get_attr_field(block_type: str, attr_name: str, field: str = None) -> str:
    """
    Return the attibute value.

    Parameters
    ----------
    block_type : str
        The type of the block.
    attr_name : str
        The name of the attribute.

    Returns
    -------
    str
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
    File types for SMS++ files.

    Supported values
    ----------------
    eProbFile (0): Problem file: Block and Configuration
    eBlockFile (1): Block file
    eConfigFile (2): Configuration file

    """

    eProbFile = (0,)  # Problem file: Block and Configuration
    eBlockFile = 1  # Block file
    eConfigFile = 2  # Configuration file


class Variable:
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
        self.name = name
        self.var_type = var_type
        self.dimensions = dimensions
        self.data = data


class Block:
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
            return self.attributes["type"]
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
        self.attributes["type"] = block_type

    def add_attribute(self, name: str, value, force: bool = False):
        """
        Add an attribute to the block.

        Parameters
        ----------
        name : str
            The name of the attribute
        value : any
            The value of the attribute
        force : bool (default: False)
            If True, overwrite the attribute if it exists.
        """
        if not force and name in self.attributes:
            raise ValueError(f"Attribute {name} already exists.")
        self.attributes[name] = value

    def add_dimension(self, name: str, value: int, force: bool = False):
        """
        Add a dimension to the block.

        Parameters
        ----------
        name : str
            The name of the dimension
        value : int
            The value of the dimension
        force : bool (default: False)
            If True, overwrite the dimension if it exists.
        """
        if not force and name in self.dimensions:
            raise ValueError(f"Dimension {name} already exists.")
        self.dimensions[name] = value

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
        """
        if not force and name in self.variables:
            raise ValueError(f"Variable {name} already exists.")
        if len(args) == 1:
            assert isinstance(args[0], Variable), "args must be a Variable object."
            self.variables[name] = args[0]
        else:
            self.variables[name] = Variable(name, *args, **kwargs)

    def add_block(self, name: str, *args, **kwargs):
        """
        Add a block.

        Parameters
        ----------
        name : str
            The name of the block
        kwargs : dict
            The attributes of the block.
            If the argument "block" is present, the block is set to that value.
            Otherwise, arguments are passed to the Block constructor.
        """
        force = kwargs.pop("force", False)
        if not force and name in self.blocks:
            raise ValueError(f"Block {name} already exists.")
        if "block" in kwargs:
            if not isinstance(kwargs["block"], Block):
                raise ValueError("block must be a Block object.")
            self.blocks[name] = kwargs["block"]
        else:
            self.blocks[name] = Block().from_kwargs(**kwargs)
        return self

    def from_kwargs(self, **kwargs):
        """
        Create a new Block from a dictionary.

        Parameters
        ----------
        dct : dict
            The attributes of the block.
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
        """Helper function to recursively save a Block and its sub-blocks to NetCDF."""
        # Add the block's attributes
        for key, value in self.attributes.items():
            grp.setncattr(key, value)

        # Add the dimensions
        for key, value in self.dimensions.items():
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
        """Helper function to recursively load a Block and its sub-blocks from NetCDF."""
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
        """Deserialize a NetCDF file to create a Block instance with nested sub-blocks."""
        with nc.Dataset(filename, "r") as ncfile:
            return cls._from_netcdf(ncfile)

    # Functions

    def add(self, component_name, name, *args, **kwargs):
        """
        Add a new object to the block.

        Parameters
        ----------
        component_name : str
            The class name of the block
        name : str
            The name of the block
        kwargs : dict
            The attributes of the block
        """
        component_nctype = self.components[component_name]["nctype"]
        match component_nctype:
            case "Attribute":
                self.add_attribute(name, *args, **kwargs)
            case "Dimension":
                self.add_dimension(name, *args, **kwargs)
            case "Variable":
                self.add_variable(name, *args, **kwargs)
            case "Block":
                self.add_block(name, *args, block_type=component_name, **kwargs)
            case _:
                raise ValueError(f"Class {component_name} not supported.")
        return self

    # Utilities

    def remove(self, component_name: str, name: str):
        """
        Remove the object with the given name from the block.

        Parameters
        ----------
        component_name : str
            The class name of the block
        name : str
            The name of the block
        """
        self.static(component_name).pop(name)

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


class SMSNetwork(Block):
    """
    SMSNetwork is a subclass of Block that implements the creation of a SMS problem file.
    """

    def __init__(
        self,
        fp: Path | str = "",
        file_type: SMSFileType | int = SMSFileType.eProbFile,
        **kwargs,
    ):
        """
        Initialize a SMSNetwork object with the given file type.
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


tb = Block().from_kwargs(
    block_type="ThermalUnitBlock",
    MinPower=Variable("MinPower", "float", None, 0.0),
    MaxPower=Variable("MaxPower", "float", None, 100.0),
    LinearTerm=Variable("LinearTerm", "float", None, 0.3),
)
b = SMSNetwork()
b.add(
    "UCBlock",
    "UCBlock_0",
    TimeHorizon=24,
    NumberUnits=1,
    NumberElectricalGenerators=0,
    NumberNodes=3,
    NumberLines=2,
    GeneratorNode=Variable(
        "GeneratorNode", "int", ("NumberElectricalGenerators",), [0, 0, 0]
    ),
    StartLine=Variable("StartLine", "int", ("NumberNodes",), [0, 1]),
    EndLine=Variable("EndLine", "int", ("NumberNodes",), [1, 2]),
    MinPowerFlow=Variable("MinPowerFlow", "float", ("NumberNodes",), [0.0, 0.0]),
    MaxPowerFlow=Variable("MaxPowerFlow", "float", ("NumberNodes",), [100.0, 100.0]),
    UnitBlock_0=tb,
)

print("Done.")
