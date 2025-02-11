from pysmspp import Block, Variable
import os
import re
import numpy as np

# Reads a sample network; microgrid_ALL_4N.nc4 is composed by:
# on node 0: 2 intermittent, 1 battery, 1 hydro, 1 thermal, and 1 load
# on nodes 1-3: 1 load each
sample_networks = [
    "microgrid_ALL_4N.nc4",
]


def get_datafile(fname):
    return os.path.join(os.path.dirname(__file__), "test_data", fname)


def get_network(fname=sample_networks[0]):
    return get_datafile(fname)


def get_temp_file(fname):
    return os.path.join(os.path.dirname(__file__), "temp", fname)


def check_compare_nc(fp_n1, fp_n2, fp_out=get_temp_file("tmp.txt")):
    """
    Utility function to compare two netCDF files and check if they are the same.

    Parameters
    ----------
    fp_n1 : str
        File path to the first netCDF file.
    fp_n2 : str
        File path to the second netCDF file.
    fp_out : str (optional)
        File path to the output file.
    """
    os.system(
        f"ncompare {fp_n1} {fp_n2} --only-diffs --show-attributes --file-text {fp_out}"
    )

    # ensure file exists
    assert os.path.isfile(fp_out)

    # read the file
    with open(fp_out, "r") as f:
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
    b.add("UCBlock", "Block_0", **kwargs)


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


def add_ucblock_with_one_unit(b, **kwargs):
    """
    Create a UCBlock with one unit and a ThermalUnitBlock.
    """
    n_units = kwargs.get("n_units", 1)
    n_egs = kwargs.get("n_elec_generators", 1)
    add_base_ucblock(b, n_units=n_units, n_elec_generators=n_egs, **kwargs)
    tb = build_base_tub()
    b.blocks["Block_0"].add_block("UnitBlock_0", block=tb)
    return b
