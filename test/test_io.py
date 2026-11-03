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


def _write_part(g, i, extra=False):
    """Write in g a part of the stacks of test_read_stacked, i its values."""
    g.setncattr("type", "Part")
    g.createDimension("T", 3)
    g.createVariable("x", "f8", ("T",))[:] = [i, i + 1, i + 2]
    g.createVariable("k", "i4")[...] = i
    if extra:
        g.createVariable("e", "f8")[...] = 10 * i
    s = g.createGroup("Sub")
    s.createDimension("N", 2)
    s.createVariable("v", "f8", ("N",))[:] = [i, -i]


def _write_stack(g, values, extra=False, outer=()):
    """
    Write in g the stack of the parts of _write_part() with the values in
    values, as SMS++ does, each variable with the dimensions outer in front.
    """
    name = "Stacked"
    g.setncattr("type", "Part")
    g.createDimension(name, values.shape[-1])
    g.createDimension("T", 3)
    dims = outer + (name,)
    g.createVariable("x", "f8", dims + ("T",))[:] = np.stack(
        [values, values + 1, values + 2], axis=-1
    )
    g.createVariable("k", "i4", dims)[:] = values
    if extra:
        g.createVariable("e", "f8", dims)[:] = 10 * values
    s = g.createGroup("Sub")
    s.createDimension("N", 2)
    s.createVariable("v", "f8", dims + ("N",))[:] = np.stack([values, -values], axis=-1)


def _tree(g):
    """The content of a netCDF group, values included, as nested tuples."""
    return (
        sorted((a, str(g.getncattr(a))) for a in g.ncattrs()),
        sorted((d, len(v)) for d, v in g.dimensions.items()),
        sorted(
            (n, v.dimensions, np.asarray(v[...]).tolist())
            for n, v in g.variables.items()
        ),
        [(n, _tree(s)) for n, s in g.groups.items()],
    )


def test_read_stacked():
    """
    The parts that SMS++ stacks in one group [see write_stacked() in
    SMSnetCDF.h] are read as the groups "<name>_i" that SMS++ writes when it
    does not stack them: parts of two trees, with one stack per tree and the
    index of the parts, and parts with a stack nested in them, whose
    dimension "Stacked_1" is the outer one.
    """
    import netCDF4 as nc

    fp_plain = "test/temp/stacked_plain.nc4"
    fp_stack = "test/temp/stacked_stack.nc4"
    os.makedirs(os.path.dirname(fp_plain), exist_ok=True)

    with nc.Dataset(fp_plain, "w") as f:
        for i in range(4):
            _write_part(f.createGroup(f"P_{i}"), i, extra=i % 2 == 1)
        for j in range(2):
            o = f.createGroup(f"O_{j}")
            for m in range(2):
                _write_part(o.createGroup(f"In_{m}"), 10 * j + m)

    with nc.Dataset(fp_stack, "w") as f:
        p = f.createGroup("P")
        p.createDimension("NumberParts", 4)
        p.createVariable("PartStack", "i4", ("NumberParts",))[:] = [0, 1, 0, 1]
        p.createVariable("PartPosition", "i4", ("NumberParts",))[:] = [0, 0, 1, 1]
        _write_stack(p.createGroup("Stack_0"), np.array([0, 2]))
        _write_stack(p.createGroup("Stack_1"), np.array([1, 3]), extra=True)
        o = f.createGroup("O")
        o.createDimension("Stacked_1", 2)
        inner = o.createGroup("In")
        values = np.array([[0, 1], [10, 11]])
        # the dimension of the inner stack is "Stacked", that of the outer one
        # "Stacked_1"
        _write_stack(inner, values, outer=("Stacked_1",))

    fp_a = "test/temp/stacked_plain_resaved.nc4"
    fp_b = "test/temp/stacked_stack_resaved.nc4"
    pysmspp.Block.from_netcdf(fp_plain).to_netcdf(fp_a, force=True)
    pysmspp.Block.from_netcdf(fp_stack).to_netcdf(fp_b, force=True)
    with nc.Dataset(fp_a) as a, nc.Dataset(fp_b) as b:
        assert _tree(a) == _tree(b)
