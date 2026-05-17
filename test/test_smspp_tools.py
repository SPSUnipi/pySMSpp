import sys

import pytest

from pysmspp import SMSPPSolverTool


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
