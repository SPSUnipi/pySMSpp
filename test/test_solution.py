import os
from pathlib import Path
from pysmspp import (
    SMSConfig,
    SMSNetwork,
    SMSFileType,
    UCBlockSolver,
)
from conftest import (
    get_temp_file,
    add_base_ucblock,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    add_sub_to_ucblock,
)
from conftest import get_datafile
import pytest

RTOL = 1e-4
ATOL = 1e-2


def test_read_solution():
    fp_sol = get_datafile("sol.nc4")

    sol = SMSNetwork(fp_sol)

    assert sol.file_type == SMSFileType.eSolutionFile
    assert "Solution_0" in sol.blocks

    ucsol = sol.blocks["Solution_0"].blocks["UnitBlock_0"]

    assert ucsol.block_type == "UnitBlockSolution"
    assert ucsol.variables["ActivePower"].data[0] > 0.0


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
    fp_solution = get_temp_file("test_optimize_ucsolver_all_components_solution.nc")
    configfile = SMSConfig(template="uc_solverconfig.txt")

    path_out = Path(fp_solution).resolve()
    if path_out.exists():
        os.remove(path_out)

    if UCBlockSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log, fp_solution)
        assert "success" in result.status.lower()
        assert path_out.exists()
        assert result.solution is not None
        assert result.solution.file_type == SMSFileType.eSolutionFile
    else:
        pytest.skip("Impossible to export a solution object")
