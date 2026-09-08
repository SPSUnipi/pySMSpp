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
