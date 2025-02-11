from pysmspp import SMSNetwork, SMSFileType, UCBlockSolver
from conftest import (
    get_network,
    get_temp_file,
    get_datafile,
    add_ucblock_with_one_unit,
)
import pytest
import numpy as np

RTOL = 1e-4
ATOL = 1e-2


def test_optimize_example():
    fp_network = get_network()
    fp_out = get_temp_file("test_optimize_example.txt")
    configfile = get_datafile("configs/UCBlockSolver/uc_solverconfig.txt")
    ucs = UCBlockSolver(
        configfile=configfile,
        fp_network=fp_network,
        fp_out=fp_out,
    )

    if ucs.is_available():
        ucs.optimize()

        assert "Success" in ucs.status
        assert np.isclose(ucs.objective_value, 1.93158759e04, atol=ATOL, rtol=RTOL)
    else:
        pytest.skip("UCBlockSolver not available in PATH")


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

    if ucs.is_available():
        result = b.optimize(configfile, fp_temp, fp_out)

        assert "Success" in result.status
    else:
        pytest.skip("UCBlockSolver not available in PATH")
