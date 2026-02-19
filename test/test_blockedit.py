import os
from pysmspp import SMSNetwork, Block, Variable, Attribute, Dimension
from conftest import (
    add_base_ucblock,
    add_ucblock_with_one_unit,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    build_base_investmentblock,
    check_compare_nc,
    get_datafile,
    get_temp_file,
)


def test_blocks_entry():
    from pysmspp import blocks

    assert "ThermalUnitBlock" in blocks.keys()


def test_components_entry():
    from pysmspp import components

    assert "ThermalUnitBlock" in components.index


def test_attribute():
    b = SMSNetwork()

    b.add("Attribute", "test_attr", "test_value")
    assert b.attributes["test_attr"].value == "test_value"
    b.add("Attribute", "test_attr_num", 1)
    assert b.attributes["test_attr_num"].value == 1

    b.remove("Attribute", "test_attr")
    assert "test_attr" not in b.attributes


def test_dimension():
    b = SMSNetwork()
    b.add("Dimension", "test_dim", 1)
    assert b.dimensions["test_dim"].value == 1

    b.remove("Dimension", "test_dim")
    assert "test_dim" not in b.dimensions


def test_variable():
    b = SMSNetwork()
    b.add(
        "Variable",
        "test_var",
        var_type="int",
        dimensions=tuple(),
        data=1,
    )
    assert b.variables["test_var"].data == 1

    b.remove("Variable", "test_var")
    assert "test_var" not in b.variables


def test_fromkwargs():
    tb = Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", None, 0.0),
        MaxPower=Variable("MaxPower", "float", None, 100.0),
        LinearTerm=Variable("LinearTerm", "float", None, 0.3),
    )
    assert tb.block_type == "ThermalUnitBlock"
    assert tb.variables["MinPower"].data == 0


def test_empty_block_type():
    # Block with empty block_type and no other kwargs
    b = Block(block_type="")
    assert b.block_type == ""

    # Block with empty block_type and Attribute kwargs
    b2 = Block(block_type="", id=Attribute("id", "0"))
    assert b2.block_type == ""
    assert b2.attributes["id"].value == "0"


def test_block_constructor():
    kwargs = {
        "block_type": "ThermalUnitBlock",
        "MinPower": Variable("MinPower", "float", None, 0.0),
        "MaxPower": Variable("MaxPower", "float", None, 100.0),
        "LinearTerm": Variable("LinearTerm", "float", None, 0.3),
    }
    tb1 = Block().from_kwargs(**kwargs)
    tb2 = Block(**kwargs)
    assert tb1.block_type == tb2.block_type
    assert tb1.variables["MinPower"].data == tb2.variables["MinPower"].data


def test_add_block():
    b = SMSNetwork()
    add_base_ucblock(b)


def test_add_block_with_subblocks():
    b = SMSNetwork()
    add_ucblock_with_one_unit(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "ThermalUnitBlock"


def test_add_tub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_tub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "ThermalUnitBlock"


def test_add_bub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_bub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "BatteryUnitBlock"


def test_add_hub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_hub_to_ucblock(b)

    assert b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "HydroUnitBlock"


def test_add_iub():
    b = SMSNetwork()
    add_base_ucblock(b)
    add_iub_to_ucblock(b)

    assert (
        b.blocks["Block_0"].blocks["UnitBlock_0"].block_type == "IntermittentUnitBlock"
    )


def test_investment_block():
    b = SMSNetwork()
    build_base_investmentblock(b)
    print(b)
    assert b.blocks["InvestmentBlock"].block_type == "InvestmentBlock"
    assert b.blocks["InvestmentBlock"].blocks["InnerBlock"].block_type == "UCBlock"


def test_add_line_branches():
    n_branches = 2
    n_lines = 1
    n_nodes = 2
    b = SMSNetwork()
    add_base_ucblock(b, n_nodes=n_nodes)
    b.add("Dimension", "NumberLines", n_lines)
    b.add("Dimension", "NumberBranches", n_branches)
    v = Variable("StartLine", "int", ("NumberBranches",), list(range(n_branches)))

    b.blocks["Block_0"].add("Variable", "StartLine", v)
    assert len(b.blocks["Block_0"].variables["StartLine"].data) == n_branches


def test_attribute_class():
    """Test that Attribute class can be imported and used."""
    # Test creating Attribute objects directly
    attr1 = Attribute("test_attr", "test_value")
    assert attr1.name == "test_attr"
    assert attr1.value == "test_value"

    attr2 = Attribute("test_num", 42)
    assert attr2.name == "test_num"
    assert attr2.value == 42

    # Test string representation
    assert str(attr1) == "test_value"
    assert str(attr2) == "42"

    # Test equality
    assert attr1 == "test_value"
    assert attr2 == 42

    # Test with Block
    b = Block()
    b.add_attribute("my_attr", "my_value")
    assert isinstance(b.attributes["my_attr"], Attribute)
    assert b.attributes["my_attr"].value == "my_value"
    assert b.attributes["my_attr"] == "my_value"


def test_dimension_class():
    """Test that Dimension class can be imported and used."""
    # Test creating Dimension objects directly
    dim1 = Dimension("test_dim", 10)
    assert dim1.name == "test_dim"
    assert dim1.value == 10

    dim2 = Dimension("n_nodes", 5)
    assert dim2.name == "n_nodes"
    assert dim2.value == 5

    # Test string representation
    assert str(dim1) == "10"
    assert str(dim2) == "5"

    # Test equality
    assert dim1 == 10
    assert dim2 == 5

    # Test with Block
    b = Block()
    b.add_dimension("my_dim", 20)
    assert isinstance(b.dimensions["my_dim"], Dimension)
    assert b.dimensions["my_dim"].value == 20
    assert b.dimensions["my_dim"] == 20


def test_attribute_dimension_consistency_with_variable():
    """Test that Attribute and Dimension follow the same pattern as Variable."""
    b = Block()

    # All three should be objects stored in dictionaries
    b.add_variable("var1", "float", (), 1.0)
    b.add_attribute("attr1", "value1")
    b.add_dimension("dim1", 10)

    # All should return objects
    assert isinstance(b.variables["var1"], Variable)
    assert isinstance(b.attributes["attr1"], Attribute)
    assert isinstance(b.dimensions["dim1"], Dimension)

    # Access patterns should be consistent
    assert b.variables["var1"].data == 1.0
    assert b.attributes["attr1"].value == "value1"
    assert b.dimensions["dim1"].value == 10


def test_add_block_with_attributes_and_dimensions():
    b = SMSNetwork()
    b.add("Dimension", "n_units", 3)
    b.add("Attribute", "unit_type", "thermal")

    block_kwargs = {
        "MinPower": Variable("MinPower", "float", ("n_units",), [0.0] * 3),
        "MaxPower": Variable("MaxPower", "float", ("n_units",), [100.0] * 3),
        "LinearTerm": Variable("LinearTerm", "float", ("n_units",), [0.3] * 3),
    }
    bb = b.add("Block", "UnitBlock_0", **block_kwargs)

    assert bb.block_type == "Block"

    bb.add("Attribute", "type", "ThermalUnitBlock", force=True)

    assert b.blocks["UnitBlock_0"].block_type == "ThermalUnitBlock"
    assert b.blocks["UnitBlock_0"].variables["MinPower"].data == [0.0] * 3


def test_tssb():
    import numpy as np

    fp_test_tssb = get_temp_file("test_tssb.nc")
    fp_benchmark_tssb = get_datafile("TSSB_EC_CO_Test_TUB_simple.nc4")
    fp_log_tssb = get_temp_file("tmp_tssb.txt")

    os.makedirs(os.path.dirname(fp_test_tssb), exist_ok=True)

    if os.path.exists(fp_test_tssb):
        os.remove(fp_test_tssb)

    sn = SMSNetwork()

    ScenarioSize = 48  # For DiscreteScenarioSet
    NumberScenarios = 9  # For DiscreteScenarioSet
    NumberDataMappings = NumberScenarios  # for StochasticBlock

    PathDim = 5  # for AbstractPath
    TotalLength = 10  # for AbstractPath

    SizeDim_perScenario = 2  # for StochBlock
    SizeElements_perScenario = 4  # for StochBlock
    PathDim2 = 9  # for AbstractPath in StochasticBlock

    sn.add(
        "TwoStageStochasticBlock",
        "Block_0",
        NumberScenarios=NumberScenarios,
        DiscreteScenarioSet=Block(
            block_type="DiscreteScenarioSet",
            ScenarioSize=ScenarioSize,
            NumberScenarios=NumberScenarios,
            PoolWeights=Variable(
                "PoolWeights",
                "double",
                ("NumberScenarios",),
                np.ones(NumberScenarios) / NumberScenarios,
            ),
            Scenarios=Variable(
                "Scenarios",
                "double",
                ("NumberScenarios", "ScenarioSize"),
                np.ones((NumberScenarios, ScenarioSize), dtype=np.float64),
            ),
        ),
        StaticAbstractPath=Block(
            block_type="StaticAbstractPath",
            PathDim=PathDim,
            TotalLength=TotalLength,
            PathElementIndices=Variable(
                "PathElementIndices",
                "u4",
                ("TotalLength",),
                np.zeros(
                    TotalLength, dtype=np.uint32
                ),  # ignored missing values (masked array)
            ),
            PathGroupIndices=Variable(
                "PathGroupIndices",
                "str",
                ("TotalLength",),
                np.array(
                    [
                        "0",
                        "x_thermal",
                        "1",
                        "x_intermittent",
                        "2",
                        "x_battery",
                        "2",
                        "x_converter",
                        "3",
                        "x_intermittent",
                    ],
                    dtype="object",
                ),
            ),
            PathNodeTypes=Variable(
                "PathNodeTypes",
                "c",
                ("TotalLength",),
                np.tile(["B", "V"], TotalLength // 2),
            ),
            PathRangeIndices=Variable(
                "PathRangeIndices",
                "u4",
                ("TotalLength",),
                np.ones(TotalLength, dtype=np.uint32),  # ignored missing values
            ),
            PathStart=Variable(
                "PathStart",
                "u4",
                ("PathDim",),
                list(range(0, TotalLength, 2)),  # ignored missing values
            ),
        ),
        StochasticBlock=Block(
            block_type="StochasticBlock",
            NumberDataMappings=NumberDataMappings,
            SetSize_dim=SizeDim_perScenario * NumberDataMappings,
            SetElements_dim=SizeElements_perScenario * NumberDataMappings,
            FunctionName=Variable(
                "FunctionName",
                "str",
                ("NumberDataMappings",),
                np.repeat(
                    np.array(["UCBlock::set_active_power_demand"], dtype="object"),
                    NumberDataMappings,
                ),
            ),
            Caller=Variable(
                "Caller",
                "c",
                ("NumberDataMappings",),
                np.repeat(["B"], NumberDataMappings),
            ),
            DataType=Variable(
                "DataType",
                "c",
                ("NumberDataMappings",),
                np.repeat(["D"], NumberDataMappings),
            ),
            SetSize=Variable(
                "SetSize",
                "u4",
                ("SetSize_dim",),
                np.zeros(SizeDim_perScenario * NumberDataMappings, dtype=np.uint32),
            ),
            SetElements=Variable(
                "SetElements",
                "u4",
                ("SetElements_dim",),
                np.zeros(
                    SizeElements_perScenario * NumberDataMappings, dtype=np.uint32
                ),
            ),
            AbstractPath=Block(
                block_type="AbstractPath",
                PathDim=PathDim2,
                TotalLength=0,  # Unlimited
                PathElementIndices=Variable(
                    "PathElementIndices",
                    "u4",
                    ("TotalLength",),
                    [],  # ignored missing values (masked array)
                ),
                PathGroupIndices=Variable(
                    "PathGroupIndices",
                    "str",
                    ("TotalLength",),
                    np.array([], dtype="object"),
                ),
                PathNodeTypes=Variable("PathNodeTypes", "c", ("TotalLength",), []),
                PathRangeIndices=Variable(
                    "PathRangeIndices",
                    "u4",
                    ("TotalLength",),
                    [],  # ignored missing values
                ),
                PathStart=Variable(
                    "PathStart",
                    "u4",
                    ("PathDim",),
                    np.repeat([0], PathDim2),  # ignored missing values
                ),
            ),
            Block=Block(
                id=Attribute("id", "0"),
                filename=Attribute("filename", "EC_CO_Test_TUB.nc4[0]"),
            ),
        ),
    )

    sn.to_netcdf(fp_test_tssb)

    check_compare_nc(fp_test_tssb, fp_benchmark_tssb, fp_log_tssb)
