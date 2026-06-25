from conftest import get_network, check_compare_nc
import netCDF4 as nc
import numpy as np
import pysmspp
import os


def test_load_save_network():
    fp_n1 = get_network()
    fp_n2 = "test/temp/resaved_file.nc4"
    os.makedirs(os.path.dirname(fp_n2), exist_ok=True)

    # Load a sample network
    net = pysmspp.SMSNetwork(fp_n1)
    # Save the network to a temporary file
    net.to_netcdf(fp_n2, force=True)

    check_compare_nc(fp_n1, fp_n2)


def test_save_masked_arrays():
    fp = "test/temp/masked_arrays.nc4"
    os.makedirs(os.path.dirname(fp), exist_ok=True)

    net = pysmspp.Block()
    net.add_dimension("Rows", 1)
    net.add_dimension("TimeHorizon", 24)
    net.add_dimension("PathDim", 2)

    demand = np.ma.masked_array(np.arange(24.0).reshape(1, 24), mask=False)
    path_indices = np.ma.masked_array(
        np.array([0, 1], dtype=np.uint32),
        mask=np.array([True, False]),
    )

    net.add_variable("Demand", "double", ("Rows", "TimeHorizon"), demand)
    net.add_variable("PathElementIndices", "u4", ("PathDim",), path_indices)

    net.to_netcdf(fp)

    with nc.Dataset(fp) as ds:
        np.testing.assert_array_equal(ds.variables["Demand"][:], demand.data)

        saved_path_indices = ds.variables["PathElementIndices"][:]
        assert saved_path_indices.fill_value == nc.default_fillvals["u4"]
        np.testing.assert_array_equal(saved_path_indices.mask, [True, False])
        np.testing.assert_array_equal(
            saved_path_indices.data,
            [nc.default_fillvals["u4"], 1],
        )
