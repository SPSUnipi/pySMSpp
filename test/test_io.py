from conftest import get_network, check_compare_nc
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
