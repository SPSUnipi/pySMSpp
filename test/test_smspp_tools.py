import sys
from pathlib import Path

import numpy as np
import pytest

from pysmspp import InvestmentBlockSolver, SDDPSolver, SMSPPSolverTool, UCBlockSolver


class FakeSolver(SMSPPSolverTool):
    def calculate_executable_call(self):
        code = (
            "import sys, time; "
            "print('solver stdout line', flush=True); "
            "print('solver stderr line', file=sys.stderr, flush=True); "
            "time.sleep(0.05); "
            "print('Status = Success', flush=True); "
            "print('Upper bound = 123.0', flush=True); "
            "print('Lower bound = 120.0', flush=True)"
        )
        return [sys.executable, "-c", code]


def test_optimize_reads_subprocess_output_portably(tmp_path):
    fp_network = tmp_path / "network.nc4"
    fp_config = tmp_path / "config.txt"
    fp_log = tmp_path / "solver.log"
    fp_network.write_text("fake network")
    fp_config.write_text("fake config")

    solver = FakeSolver(
        solver_path=sys.executable,
        fp_network=fp_network,
        configfile=fp_config,
        fp_log=fp_log,
    )

    result = solver.optimize(logging=False, tracking_period=0.01)

    assert result.status == "Success"
    assert result.objective_value == pytest.approx(123.0)
    assert result.lower_bound == pytest.approx(120.0)
    assert "solver stdout line" in result.log
    assert "solver stderr line" in result.log
    assert "Peak CPU Usage" in result.log
    assert fp_log.read_text() == result.log


def test_status_code_of_a_log():
    """The status of a run is the one SMS++ printed, not a finite value."""
    solver = UCBlockSolver()

    solver._log = (
        "Status = 10 (Success)\nUpper bound = 1.5e+02\nLower bound = 1.5e+02\n"
    )
    solver.parse_solver_log()
    assert solver.status_code == 10
    assert solver.is_optimal
    assert solver.objective_value == pytest.approx(150.0)

    # kLowPrecision, which comes with a value that looks like an optimum
    solver._log = (
        "Status = 20 (Low precision)\nUpper bound = 1.5e+02\nLower bound = 1.4e+02\n"
    )
    solver.parse_solver_log()
    assert solver.status_code == 20
    assert not solver.is_optimal
    assert np.isfinite(solver.objective_value)

    solver._log = "nothing of the kind\n"
    solver.parse_solver_log()
    assert solver.status_code is None
    assert not solver.is_optimal


def test_investment_status_is_not_the_value():
    """A finite objective of an InvestmentBlock run that failed is no success."""
    solver = InvestmentBlockSolver()

    solver._log = "Fi* = 1.4472748944e+11\nSolver status: 10\n"
    solver.parse_solver_log()
    assert solver.status_code == 10
    assert solver.is_optimal
    assert solver.status.startswith("Success")

    solver._log = "Fi* = 0.0000000000e+00\nSolver status: 18\n"
    solver.parse_solver_log()
    assert solver.status_code == 18
    assert not solver.is_optimal
    assert solver.status.startswith("Failed")


def test_sddp_lagrangian_recipe_passes_its_block_config():
    """The Lagrangian recipe of the SDDPBlock templates is the pair -B -S:
    without -B the tool reads its default SDDPBCfg.txt, i.e., the formulation
    of the units for the linear programs, whatever -S says."""
    from pysmspp import SMSConfig

    configfile = SMSConfig(template="SDDPBlock/SDDPSCfg-LD.txt")
    training = SDDPSolver(
        fp_network="net/SDDPBlock.nc4",
        configfile=str(configfile),
        B="SDDPBCfg-LD.txt",
    ).calculate_executable_call()
    simulation = SDDPSolver(
        fp_network="net/SDDPBlock.nc4",
        configfile=str(configfile).replace("SDDPSCfg-LD", "SDDPSCfg-greedy-LD"),
        s=None,
        B="SDDPBCfg-LD.txt",
    ).calculate_executable_call()

    for command in (training, simulation):
        assert command[command.index("-B") + 1] == "SDDPBCfg-LD.txt"
        configdir = command[command.index("-c") + 1]
        for name in ("SDDPBCfg-LD.txt", command[command.index("-S") + 1]):
            assert (Path(configdir) / name).is_file()
    assert "-s" in simulation
    assert simulation[simulation.index("-S") + 1] == "SDDPSCfg-greedy-LD.txt"
