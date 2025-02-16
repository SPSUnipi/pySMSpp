from pysmspp import SMSConfig, SMSNetwork, SMSFileType, UCBlockSolver
from conftest import (
    get_network,
    get_temp_file,
    add_base_ucblock,
    add_ucblock_with_one_unit,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
)
import pytest
import numpy as np

RTOL = 1e-4
ATOL = 1e-2


def test_optimize_example():
    fp_network = get_network()
    fp_out = get_temp_file("test_optimize_example.txt")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    ucs = UCBlockSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_out=fp_out,
    )

    if UCBlockSolver.is_available():
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
    configfile = SMSConfig(template="uc_solverconfig.txt")

    if UCBlockSolver.is_available():
        result = b.optimize(configfile, fp_temp, fp_out)

        assert "Success" in result.status
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_optimize_ucsolver_all_components():
    b = SMSNetwork(file_type=SMSFileType.eBlockFile)

    # Add uc block and specify demand
    add_base_ucblock(b)

    # Add thermal unit block
    add_tub_to_ucblock(b)

    # Add battery unit block
    add_bub_to_ucblock(b)

    # Add hydro unit block
    add_hub_to_ucblock(b)

    # Add intermittent unit block
    add_iub_to_ucblock(b)

    fp_out = get_temp_file("test_optimize_ucsolver_all_components.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver_all_components.nc")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    if UCBlockSolver.is_available():
        result = b.optimize(configfile, fp_temp, fp_out)

        assert "success" in result.status.lower()
        assert "warning" not in result.log.lower()
        assert "error" not in result.log.lower()
        assert "ThermalUnitBlock" in result.log
        assert "BatteryUnitBlock" in result.log
        assert "HydroUnitBlock" in result.log
        assert "IntermittentUnitBlock" in result.log
    else:
        pytest.skip("UCBlockSolver not available in PATH")
