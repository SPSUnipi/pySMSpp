import os

import numpy as np
import pytest
from conftest import build_svm_network, check_compare_nc, get_network

import pysmspp


def test_load_save_network():
    fp_n1 = get_network()
    fp_n2 = "test/temp/resaved_file.nc4"
    os.makedirs(os.path.dirname(fp_n2), exist_ok=True)

    # Load a sample network
    net = pysmspp.SMSNetwork(fp_n1)
    # Save the network to a temporary file
    net.to_netcdf(fp_n2, force=True)

    check_compare_nc(fp_n1, fp_n2)


@pytest.mark.parametrize("block_type", ["SVCBlock", "SVRBlock"])
def test_load_save_svm_network(block_type):
    """
    The data set and the hyper-parameters of a SVM survive a round trip, the
    hyper-parameters being attributes of the group and not variables.
    """
    fp = f"test/temp/{block_type}.nc4"
    os.makedirs(os.path.dirname(fp), exist_ok=True)

    kwargs = {"C": 10.0, "Kernel": 2, "Gamma": 0.5}
    if block_type == "SVRBlock":
        kwargs["Epsilon"] = 0.2

    net = build_svm_network(block_type, **kwargs)
    net.to_netcdf(fp, force=True)

    block = pysmspp.SMSNetwork(fp).blocks["Block_0"]

    assert block.block_type == block_type
    assert set(kwargs) <= set(block.variables)
    for name, value in kwargs.items():
        assert block.variables[name].data == pytest.approx(value)

    original = net.blocks["Block_0"]
    for name in ("X", "Y"):
        assert np.allclose(block.variables[name].data, original.variables[name].data)


def test_unstack():
    """
    Block.unstack() turns the parts that SMS++ stacks in one group into one
    sub-Block each: here two parts of an outer stack "O", each with an inner
    group "U" of two parts of different trees; a group whose variables do not
    lead with its dimension "Stacked" is left as it is.
    """
    from pysmspp import Block, Dimension, SMSFileType, SMSNetwork, Variable

    def stack(name, values):  # the stack of the parts with the given values
        return Block(
            dimensions={"Stacked": Dimension("Stacked", len(values[0]))},
            variables={
                name: Variable(name, "f8", ("Stacked_1", "Stacked"), np.array(values))
            },
        )

    u = Block(
        dimensions={"NumberParts": Dimension("NumberParts", 2)},
        variables={
            "PartStack": Variable(
                "PartStack",
                "i4",
                ("Stacked_1", "NumberParts"),
                np.array([[0, 1], [1, 0]]),
            ),
            "PartPosition": Variable(
                "PartPosition",
                "i4",
                ("Stacked_1", "NumberParts"),
                np.array([[0, 0], [0, 0]]),
            ),
        },
        blocks={
            "Stack_0": stack("x", [[0.0], [11.0]]),
            "Stack_1": stack("y", [[1.0], [10.0]]),
        },
    )
    plain = Block(
        dimensions={"Stacked": Dimension("Stacked", 3)},
        variables={"z": Variable("z", "f8", ("T",), np.zeros(4))},
    )
    network = SMSNetwork(
        file_type=SMSFileType.eSolutionFile,
        blocks={
            "O": Block(
                dimensions={"Stacked_1": Dimension("Stacked_1", 2)},
                blocks={"U": u},
            ),
            "P": plain,
        },
    )
    root = network.unstack()

    # an SMSNetwork of the same type, which shares nothing with the network
    assert isinstance(root, SMSNetwork)
    assert root.file_type == SMSFileType.eSolutionFile
    root.blocks["P"].variables["z"].data[0] = 1.0
    assert network.blocks["P"].variables["z"].data[0] == 0.0
    assert set(network.blocks) == {"O", "P"}

    assert set(root.blocks) == {"O_0", "O_1", "P"}

    # a group with two stack dimensions is not something SMS++ writes
    plain.add_dimension("Stacked_1", 2)
    with pytest.raises(ValueError):
        network.unstack()
    assert "Stacked" in root.blocks["P"].dimensions
    for k in range(2):
        parts = root.blocks[f"O_{k}"].blocks
        assert set(parts) == {"U_0", "U_1"}
        for j in range(2):
            ((name, var),) = parts[f"U_{j}"].variables.items()
            assert name == ("x" if (k + j) % 2 == 0 else "y")
            assert var.dimensions == () and float(var.data) == 10.0 * k + j


def test_copy():
    """copy.copy() shares the data of the values, copy.deepcopy() does not."""
    import copy

    from pysmspp import Attribute, Variable
    from pysmspp.components import Dict

    d = Dict(x=Variable("x", "f8", ("T",), np.zeros(3)), a=Attribute("a", np.zeros(2)))
    shallow, deep = copy.copy(d), copy.deepcopy(d)
    assert type(shallow) is Dict and type(deep) is Dict
    d["x"].data[0] = 1.0
    d["a"].value[0] = 1.0
    assert shallow["x"].data[0] == 1.0 and deep["x"].data[0] == 0.0
    assert shallow["a"].value[0] == 1.0 and deep["a"].value[0] == 0.0
    v = copy.copy(d["x"])
    assert v is not d["x"] and v.data is d["x"].data
