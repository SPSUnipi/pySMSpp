import os
from pysmspp import SMSNetwork, Block, Variable
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
    assert b.attributes["test_attr"] == "test_value"
    b.add("Attribute", "test_attr_num", 1)
    assert b.attributes["test_attr_num"] == 1

    b.remove("Attribute", "test_attr")
    assert "test_attr" not in b.attributes


def test_dimension():
    b = SMSNetwork()
    b.add("Dimension", "test_dim", 1)
    assert b.dimensions["test_dim"] == 1

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


def test_tssb():
    import numpy as np

    fp_test_tssb = get_temp_file("test_tssb.nc")
    fp_benchmark_tssb = get_datafile("TSSB_EC_CO_Test_TUB_simple.nc4")
    fp_log_tssb = get_temp_file("tmp_tssb.txt")

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
                np.zeros(TotalLength),  # ignored missing values (masked array)
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
                "PathGroupIndices",
                "c",
                ("TotalLength",),
                np.tile(["B", "V"], TotalLength // 2),
            ),
            PathRangeIndices=Variable(
                "PathGroupIndices",
                "u4",
                ("TotalLength",),
                np.ones(TotalLength),  # ignored missing values
            ),
            PathStart=Variable(
                "PathGroupIndices",
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
                np.zeros(SizeDim_perScenario * NumberDataMappings),
            ),
            SetElements=Variable(
                "SetElements",
                "u4",
                ("SetElements_dim",),
                np.zeros(SizeElements_perScenario * NumberDataMappings),
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
                PathNodeTypes=Variable("PathGroupIndices", "c", ("TotalLength",), []),
                PathRangeIndices=Variable(
                    "PathGroupIndices",
                    "u4",
                    ("TotalLength",),
                    [],  # ignored missing values
                ),
                PathStart=Variable(
                    "PathGroupIndices",
                    "u4",
                    ("PathDim",),
                    np.repeat([0], PathDim2),  # ignored missing values
                ),
            ),
        ),
    )

    sn.to_netcdf(fp_test_tssb)

    check_compare_nc(fp_test_tssb, fp_benchmark_tssb, fp_log_tssb)
