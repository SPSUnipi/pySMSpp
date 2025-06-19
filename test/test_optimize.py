from pysmspp import (
    SMSConfig,
    SMSNetwork,
    SMSFileType,
    UCBlockSolver,
    InvestmentBlockTestSolver,
)
from conftest import (
    get_network,
    get_temp_file,
    add_base_ucblock,
    add_ucblock_with_one_unit,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    add_sub_to_ucblock,
)
from pathlib import Path
import os
import pytest
import numpy as np

RTOL = 1e-4
ATOL = 1e-2


def test_help_ucblocksolver(force_smspp):
    ucs = UCBlockSolver()

    if ucs.is_available() or force_smspp:
        help_msg = ucs.help()

        assert (
            "SMS++ unit commitment solver" in help_msg
            or "SMS++ UCBlock solver" in help_msg
        )
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_help_investmentblocktestsolver(force_smspp):
    ibts = InvestmentBlockTestSolver()

    if ibts.is_available() or force_smspp:
        help_msg = ibts.help()

        assert "SMS++ investment solver" in help_msg
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_optimize_example(force_smspp):
    fp_network = get_network()
    fp_log = get_temp_file("test_optimize_example.txt")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    ucs = UCBlockSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    if ucs.is_available() or force_smspp:
        ucs.optimize()

        assert "Success" in ucs.status
        assert np.isclose(ucs.objective_value, 3615.760710, atol=ATOL, rtol=RTOL)
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_optimize_ucsolver(force_smspp):
    b = SMSNetwork(file_type=SMSFileType.eBlockFile)
    add_ucblock_with_one_unit(b)

    fp_log = get_temp_file("test_optimize_ucsolver.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver.nc")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    if UCBlockSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log)

        assert "Success" in result.status
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_optimize_ucsolver_all_components(force_smspp):
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

    # Add slack unit block
    add_sub_to_ucblock(b)

    fp_log = get_temp_file("test_optimize_ucsolver_all_components.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver_all_components.nc")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    if UCBlockSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log)

        assert "success" in result.status.lower()
        assert "error" not in result.log.lower()
        assert "ThermalUnitBlock" in result.log
        assert "BatteryUnitBlock" in result.log
        assert "HydroUnitBlock" in result.log
        assert "IntermittentUnitBlock" in result.log
        assert "SlackUnitBlock" in result.log
    else:
        pytest.skip("UCBlockSolver not available in PATH")


@pytest.mark.skipif(
    "cplex" not in os.environ["PATH"],
    reason="Skipping test when cplex is not available",
)
def test_investmentsolvertest(force_smspp):
    fp_network = get_network("investment_1N.nc4")
    fp_log = get_temp_file("test_optimize_investmentsolvertest.txt")
    configfile = SMSConfig(template="InvestmentBlock/BSPar.txt")

    ucs = InvestmentBlockTestSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    if InvestmentBlockTestSolver().is_available() or force_smspp:
        ucs.optimize()

        assert "success" in ucs.status.lower()
    else:
        pytest.skip("InvestmentBlockTestSolver not available in PATH")


def test_create_solution(force_smspp):
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

    # Add slack unit block
    add_sub_to_ucblock(b)

    fp_log = get_temp_file("test_optimize_ucsolver_all_components_solution.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver_all_components_solution_network.nc")
    fp_out = get_temp_file("test_optimize_ucsolver_all_components_solution.nc")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    path_out = Path(fp_out).resolve()
    if path_out.exists():
        os.remove(path_out)

    if UCBlockSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log, fp_out)
        assert "success" in result.status.lower()
        assert path_out.exists()
    else:
        pytest.skip("Impossible to export a solution object")
