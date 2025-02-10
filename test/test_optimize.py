from smspy import SMSNetwork, SMSFileType, UCBlockSolver
from conftest import (
    get_network,
    get_temp_file,
    get_datafile,
    add_ucblock_with_one_unit,
)


def test_optimize_example():
    fp = get_network()
    b = SMSNetwork(fp)

    fp_out = get_temp_file("test_optimize_example.txt")
    fp_temp = get_temp_file("test_optimize_example.nc")
    configfile = get_datafile("configs/UCBlockSolver/uc_solverconfig.txt")
    ucs = UCBlockSolver(
        configfile=configfile,
        fp_network=fp_temp,
        fp_out=fp_out,
    )
    b.to_netcdf(fp_temp, force=True)
    ucs.optimize()

    assert "Success" in ucs.status


def test_optimize_ucsolver():
    b = SMSNetwork(file_type=SMSFileType.eBlockFile)
    add_ucblock_with_one_unit(b)

    fp_out = get_temp_file("test_optimize_ucsolver.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver.nc")
    configfile = get_datafile("configs/UCBlockSolver/uc_solverconfig.txt")

    ucs = UCBlockSolver(
        configfile=configfile,
        fp_network=fp_temp,
        fp_out=fp_out,
    )
    b.to_netcdf(fp_temp, force=True)
    ucs.optimize()

    assert "Success" in ucs.status
