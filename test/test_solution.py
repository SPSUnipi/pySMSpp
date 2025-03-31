from pysmspp import (
    SMSNetwork,
    SMSFileType,
)
from conftest import get_datafile

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
