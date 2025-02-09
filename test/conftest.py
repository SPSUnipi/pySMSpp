from smspy import Block, Variable
import os
import re

# Reads a sample network; microgrid_ALL_4N.nc4 is composed by:
# on node 0: 2 intermittent, 1 battery, 1 hydro, 1 thermal, and 1 load
# on nodes 1-3: 1 load each
sample_networks = [
    "microgrid_ALL_4N.nc4",
]


def get_network(fname=sample_networks[0]):
    return os.path.join(os.path.dirname(__file__), "test_data", fname)


def check_compare(fp_n1, fp_n2, fp_out="test/temp/tmp.txt"):
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


def add_base_ucblock(b):
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
        MaxPowerFlow=Variable(
            "MaxPowerFlow", "float", ("NumberNodes",), [100.0, 100.0]
        ),
    )


def build_base_tub():
    return Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", None, 0.0),
        MaxPower=Variable("MaxPower", "float", None, 100.0),
        LinearTerm=Variable("LinearTerm", "float", None, 0.3),
    )
