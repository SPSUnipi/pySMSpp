from conftest import get_network, check_compare
import smspy

def test_load_save_network():

    fp_n1 = get_network()
    fp_n2 = "resaved_file.nc4"
    # Load a sample network
    net = smspy.SMSNetwork(fp_n1)
    # Save the network to a temporary file
    net.to_netcdf(fp_n2, force=True)
    
    check_compare(fp_n1, fp_n2)