from pysmspp import SMSFileType, SMSNetwork, Block, Variable, Dimension, Attribute
import os
import re
import numpy as np
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--force-smspp", action="store_true", default=False, help="Force SMS++ tests"
    )


@pytest.fixture
def force_smspp(request):
    return request.config.getoption("--force-smspp")


# Reads a sample network; microgrid_ALLbutStore_1N_optimized.nc4 is composed by:
# on node 0: 2 intermittent, 1 battery (StorageUnit), 1 hydro (StorageUnit), 1 thermal, and 1 load
# on nodes 1-3: 1 load each
sample_networks = [
    "microgrid_ALLbutStore_1N.nc4",
]


def get_datafile(fname):
    return os.path.join(os.path.dirname(__file__), "test_data", fname)


def get_network(fname=sample_networks[0]):
    return get_datafile(fname)


def get_temp_folder():
    return os.path.join(os.path.dirname(__file__), "temp")


def get_temp_file(fname):
    return os.path.join(get_temp_folder(), fname)


def check_compare_nc(fp_n1, fp_n2, fp_log=get_temp_file("tmp.txt")):
    """
    Utility function to compare two netCDF files and check if they are the same.

    Parameters
    ----------
    fp_n1 : str
        File path to the first netCDF file.
    fp_n2 : str
        File path to the second netCDF file.
    fp_log : str (optional)
        File path to the log file.
    """
    os.system(
        f"ncompare {fp_n1} {fp_n2} --only-diffs --show-attributes --file-text {fp_log}"
    )

    # ensure file exists
    assert os.path.isfile(fp_log)

    # read the file
    with open(fp_log, "r") as f:
        lines = f.read()

    # check that the flag items are the same are True
    matches = re.findall(r"Are all items the same\? ---> (True|False).", lines)

    assert len(matches) == 2
    assert matches[0] == matches[1]
    assert matches[0] == "True"

    # check that the number of shared items is the same
    for line in lines.splitlines():
        # Check if the line contains the target phrase
        if "Total number of shared items" in line:
            # Extract integers from this line
            numbers = re.findall(r"\d+", line)

            assert len(numbers) == 2

            assert numbers[0] == numbers[1]


def add_base_ucblock(
    b,
    n_nodes=1,
    n_lines=0,
    n_units=0,
    n_elec_generators=0,
    max_p=100.0,
    time_horizon=24,
    active_p=10.0,
    name_inner_block="Block_0",
):
    """
    Create a base UCBlock with 3 nodes and 2 lines.
    """
    kwargs = {
        "id": "0",
        "TimeHorizon": time_horizon,
        "NumberUnits": n_units,
        "NumberElectricalGenerators": n_elec_generators,
        "NumberNodes": n_nodes,
        "NumberLines": n_lines,
        "ActivePowerDemand": Variable(
            "ActivePowerDemand",
            "float",
            (
                "NumberNodes",
                "TimeHorizon",
            ),
            np.full((n_nodes, time_horizon), active_p),
        ),
    }
    if n_lines > 0:
        kwargs = {
            **kwargs,
            **{
                "StartLine": Variable(
                    "StartLine", "int", ("NumberLines",), list(range(n_lines))
                ),
                "EndLine": Variable(
                    "EndLine", "int", ("NumberLines",), list(range(1, n_lines + 1))
                ),
                "MinPowerFlow": Variable(
                    "MinPowerFlow", "float", ("NumberLines",), [0.0] * n_lines
                ),
                "MaxPowerFlow": Variable(
                    "MaxPowerFlow", "float", ("NumberLines",), [max_p] * n_lines
                ),
            },
        }
    if n_elec_generators > 0:
        kwargs["GeneratorNode"] = Variable(
            "GeneratorNode",
            "int",
            ("NumberElectricalGenerators",),
            [0] * n_elec_generators,
        )
    b.add("UCBlock", name_inner_block, **kwargs)


def build_base_tub(max_p=100.0, linear_term=0.3):
    """
    Build a ThermalUnitBlock with MinPower, MaxPower, and LinearTerm.
    """
    return Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", (), 0.0),
        MaxPower=Variable("MaxPower", "float", (), max_p),
        LinearTerm=Variable("LinearTerm", "float", (), linear_term),
        InitUpDownTime=Variable("InitUpDownTime", "int", (), 1),
    )


def build_base_bub(max_p=100.0, max_e=200.0, eta=0.9):
    """
    Build a BatteryUnitBlock.
    """
    return Block().from_kwargs(
        block_type="BatteryUnitBlock",
        MinPower=Variable("MinPower", "float", (), -max_p),
        MaxPower=Variable("MaxPower", "float", (), max_p),
        MinStorage=Variable("MinStorage", "float", (), 0.0),
        MaxStorage=Variable("MaxStorage", "float", (), max_e),
        InitialStorage=Variable("InitialStorage", "float", (), max_e),
        StoringBatteryRho=Variable("StoringBatteryRho", "float", (), eta),
        ExtractingBatteryRho=Variable("ExtractingBatteryRho", "float", (), 1 / eta),
    )


def build_base_hub(
    max_p=100.0, min_p=-100.0, max_flow=200.0, max_e=200, inflow_t=1, eta=0.9
):
    """
    Build a HydroUnitBlock.
    """
    N_ARCS = 3  # Number of arcs: 1 arc for discharge, 1 spill, 1 recharge
    return Block().from_kwargs(
        block_type="HydroUnitBlock",
        NumberReservoirs=1,
        NumberArcs=N_ARCS,
        StartArc=Variable("StartArc", "int", ("NumberArcs",), np.full((N_ARCS,), 0)),
        EndArc=Variable("EndArc", "int", ("NumberArcs",), np.full((N_ARCS,), 1)),
        MaxPower=Variable(
            "MaxPower", "double", ("NumberArcs",), np.array([max_p, 0.0, 0.0])
        ),
        MinPower=Variable(
            "MinPower", "double", ("NumberArcs",), np.array([0.0, 0.0, min_p])
        ),
        MinFlow=Variable(
            "MinFlow", "double", ("NumberArcs",), np.array([0.0, 0.0, -max_flow])
        ),
        MaxFlow=Variable(
            "MaxFlow",
            "double",
            ("NumberArcs",),
            np.array([max_p * 100.0, max_flow, 0.0]),
        ),
        MinVolumetric=Variable("MinVolumetric", "double", (), 0.0),
        MaxVolumetric=Variable("MaxVolumetric", "double", (), max_e),
        Inflows=Variable(
            "Inflows",
            "double",
            ("NumberReservoirs", "TimeHorizon"),
            np.full((1, inflow_t), 0.0),
        ),
        InitialVolumetric=Variable("InitialVolumetric", "double", (), max_e),
        NumberPieces=Variable(
            "NumberPieces", "int", ("NumberArcs",), np.full((N_ARCS,), 1)
        ),
        TotalNumberPieces=N_ARCS,
        LinearTerm=Variable(
            "LinearTerm", "double", ("TotalNumberPieces",), [1 / eta, 0.0, 1 / eta]
        ),
        ConstantTerm=Variable(
            "ConstantTerm", "double", ("TotalNumberPieces",), np.full((N_ARCS,), 0.0)
        ),
    )


def build_base_iub(max_p=100.0):
    """
    Build a IntermittentUnitBlock.
    """
    return Block().from_kwargs(
        block_type="IntermittentUnitBlock",
        MinPower=Variable("MinPower", "float", (), 0.0),
        MaxPower=Variable("MaxPower", "float", (), max_p),
    )


def build_base_sub(max_p=100.0, cost=1000.0):
    """
    Build a SlackUnitBlock.
    """
    return Block().from_kwargs(
        block_type="SlackUnitBlock",
        MaxPower=Variable("MaxPower", "float", (), max_p),
        ActivePowerCost=Variable("ActivePowerCost", "float", (), cost),
    )


def get_new_ucname(b):
    """
    Get the next available UCBlock name.
    """
    return f"UnitBlock_{len(b.blocks)}"


def add_tub_to_ucblock(b, name_inner_block="Block_0", **kwargs):
    """
    Add a ThermalUnitBlock to an existing UCBlock.
    """
    tb = build_base_tub(**kwargs)

    ucb = b.blocks[name_inner_block]
    ucname = get_new_ucname(ucb)

    ucb.dimensions["NumberUnits"].value += 1
    ucb.dimensions["NumberElectricalGenerators"].value += 1

    ucb.add("ThermalUnitBlock", ucname, block=tb)
    return b


def add_bub_to_ucblock(b, name_inner_block="Block_0", **kwargs):
    """
    Add a BatteryUnitBlock to an existing UCBlock.
    """
    bub = build_base_bub(**kwargs)

    ucb = b.blocks[name_inner_block]
    ucname = get_new_ucname(ucb)

    ucb.dimensions["NumberUnits"].value += 1
    ucb.dimensions["NumberElectricalGenerators"].value += 1

    ucb.add("BatteryUnitBlock", ucname, block=bub)
    return b


def add_hub_to_ucblock(b, name_inner_block="Block_0", **kwargs):
    """
    Add a HydroUnitBlock to an existing UCBlock.
    """
    hub = build_base_hub(**kwargs)

    ucb = b.blocks[name_inner_block]
    ucname = get_new_ucname(ucb)

    ucb.dimensions["NumberUnits"].value += 1
    ucb.dimensions["NumberElectricalGenerators"].value += 1

    ucb.add("HydroUnitBlock", ucname, block=hub)
    return b


def add_iub_to_ucblock(b, name_inner_block="Block_0", **kwargs):
    """
    Add a IntermittentUnitBlock to an existing UCBlock.
    """
    iub = build_base_iub(**kwargs)

    ucb = b.blocks[name_inner_block]
    ucname = get_new_ucname(ucb)

    ucb.dimensions["NumberUnits"].value += 1
    ucb.dimensions["NumberElectricalGenerators"].value += 1

    ucb.add("IntermittentUnitBlock", ucname, block=iub)
    return b


def add_sub_to_ucblock(b, name_inner_block="Block_0", **kwargs):
    """
    Add a SlackUnitBlock to an existing UCBlock.
    """
    sub = build_base_sub(**kwargs)

    ucb = b.blocks[name_inner_block]
    ucname = get_new_ucname(ucb)

    ucb.dimensions["NumberUnits"].value += 1
    ucb.dimensions["NumberElectricalGenerators"].value += 1

    ucb.add("SlackUnitBlock", ucname, block=sub)
    return b


def add_ucblock_with_one_unit(b, name_inner_block="Block_0", **kwargs):
    """
    Create a UCBlock with one unit and a ThermalUnitBlock.
    """
    n_units = kwargs.get("n_units", 1)
    n_egs = kwargs.get("n_elec_generators", 1)
    add_base_ucblock(b, n_units=n_units, n_elec_generators=n_egs, **kwargs)
    tb = build_base_tub()
    b.blocks[name_inner_block].add("ThermalUnitBlock", "UnitBlock_0", block=tb)
    return b


def build_base_investmentblock(b, innerblock=None):
    """
    Build a sample InvestmentBlock to the network.
    """
    if innerblock is None:
        temp = Block()
        add_ucblock_with_one_unit(temp, name_inner_block="Block_0", active_p=200.0)
        innerblock = temp.blocks["Block_0"]
    b.add(
        "InvestmentBlock",
        "InvestmentBlock",
        NumAssets=1,
        Assets=Variable("Assets", "int", ("NumAssets",), [1]),
        AssetType=Variable("AssetType", "int", ("NumAssets",), [0]),
        Cost=Variable("Cost", "int", ("NumAssets",), [1]),
        LowerBound=Variable("LowerBound", "double", ("NumAssets",), [1e-6]),
        UpperBound=Variable("UpperBound", "double", ("NumAssets",), [10000.0]),
        InnerBlock=innerblock,
    )
    return b


def build_tssb_block(fp_tssb):
    """
    Build a test SMSNetwork containing a TSSB (two-stage stochastic block) structure.
    This helper loads a benchmark network from ``fp_tssb`` and uses it as a template
    to construct a new in-memory network in block-file mode. The new network
    contains a top-level block with a discrete scenario set, one or more abstract
    paths, and a stochastic block whose dimensions (scenario size, number of
    scenarios, and data mappings) and key data arrays are consistent with those
    of the benchmark network.

    Parameters
    ----------
    fp_tssb : str or os.PathLike
        Path to an existing TSSB network.

    Returns
    -------
    SMSNetwork
        A newly created :class:`pysmspp.SMSNetwork` instance with
        ``file_type=SMSFileType.eBlockFile``.
    """
    sn_benchmark = SMSNetwork(fp_tssb)

    sn = SMSNetwork(file_type=SMSFileType.eBlockFile)

    ScenarioSize = 48  # For DiscreteScenarioSet
    NumberScenarios = 9  # For DiscreteScenarioSet
    NumberDataMappings = NumberScenarios  # for StochasticBlock

    PathDim = 5  # for AbstractPath
    TotalLength = 10  # for AbstractPath

    SizeDim_perScenario = 2  # for StochBlock
    SizeElements_perScenario = 4  # for StochBlock
    PathDim2 = 9  # for AbstractPath in StochasticBlock

    # Variables of DiscreteScenarioSet

    pool_weights = (
        sn_benchmark.blocks["Block_0"]
        .blocks["DiscreteScenarioSet"]
        .variables["PoolWeights"]
        .data
    )

    scenarios = (
        sn_benchmark.blocks["Block_0"]
        .blocks["DiscreteScenarioSet"]
        .variables["Scenarios"]
        .data
    )

    # Variables of StaticAbstractPath

    path_node_types = np.tile(["B", "V"], TotalLength // 2)

    def mask_by_node_type(arr, path_node_types):
        return np.ma.masked_array(arr, mask=path_node_types == "B")

    path_element_indices = mask_by_node_type(np.zeros(TotalLength), path_node_types)
    path_range_indices = mask_by_node_type(np.ones(TotalLength), path_node_types)

    # Variables of StochasticBlock

    set_size = (
        sn_benchmark.blocks["Block_0"]
        .blocks["StochasticBlock"]
        .variables["SetSize"]
        .data
    )

    set_elements = (
        sn_benchmark.blocks["Block_0"]
        .blocks["StochasticBlock"]
        .variables["SetElements"]
        .data
    )

    sn.add(
        "TwoStageStochasticBlock",
        "Block_0",
        id="0",
        NumberScenarios=NumberScenarios,
        DiscreteScenarioSet=Block(
            block_type="DiscreteScenarioSet",
            ScenarioSize=ScenarioSize,
            NumberScenarios=NumberScenarios,
            Scenarios=Variable(
                "Scenarios",
                "double",
                ("NumberScenarios", "ScenarioSize"),
                scenarios,
            ),
            PoolWeights=Variable(
                "PoolWeights",
                "double",
                ("NumberScenarios",),
                pool_weights,
            ),
        ),
        StaticAbstractPath=Block(
            PathDim=Dimension("PathDim", PathDim),
            TotalLength=Dimension("TotalLength", TotalLength),
            PathElementIndices=Variable(
                "PathElementIndices",
                "u4",
                ("TotalLength",),
                path_element_indices,  # important to have missing values! only ones does not work
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
                path_node_types,
            ),
            PathRangeIndices=Variable(
                "PathRangeIndices",
                "u4",
                ("TotalLength",),
                path_range_indices,  # important to have missing values! only ones does not work
            ),
            PathStart=Variable(
                "PathStart",
                "u4",
                ("PathDim",),
                np.arange(0, TotalLength, 2, dtype=np.uint32),  # ignored missing values
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
                set_size,
            ),
            SetElements=Variable(
                "SetElements",
                "u4",
                ("SetElements_dim",),
                set_elements,
            ),
            AbstractPath=Block(
                PathDim=Dimension("PathDim", PathDim2),
                TotalLength=Dimension("TotalLength", 0),  # Unlimited
                PathGroupIndices=Variable(
                    "PathGroupIndices",
                    "str",
                    ("TotalLength",),
                    np.array([], dtype="object"),
                ),
                PathElementIndices=Variable(
                    "PathElementIndices",
                    "u4",
                    ("TotalLength",),
                    [],  # ignored missing values (masked array)
                ),
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
                PathNodeTypes=Variable("PathNodeTypes", "c", ("TotalLength",), []),
            ),
            Block=Block(
                id=Attribute("id", "0"),
                filename=Attribute("filename", "EC_CO_Test_TUB.nc4[0]"),
            ),
        ),
    )

    return sn
