import shutil
from pysmspp import (
    SMSConfig,
    SMSNetwork,
    SMSFileType,
    UCBlockSolver,
    InvestmentBlockTestSolver,
    SolverLogParser,
    StatusBoundsSolverLogParser,
    ObjectiveValueSolverLogParser,
)
from pysmspp.smspp_tools import (
    SMSPPSolverTool,
    InvestmentBlockSolver,
    SDDPSolver,
    TSSBlockSolver,
)
from conftest import (
    get_network,
    add_base_ucblock,
    add_ucblock_with_one_unit,
    add_tub_to_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    add_sub_to_ucblock,
    build_tssb_block,
    get_temp_file,
)
import pytest
import numpy as np

RTOL = 1e-4
ATOL = 1e-2


def _make_solver(cls):
    """Create a solver instance with no real files, for testing parse_solver_log."""
    obj = object.__new__(cls)
    obj._log = None
    obj._status = None
    obj._objective_value = None
    obj._lower_bound = None
    obj._upper_bound = None
    return obj


# ---------------------------------------------------------------------------
# Tests for SolverLogParser classes
# ---------------------------------------------------------------------------


def test_solver_log_parser_base_raises_not_implemented():
    """SolverLogParser.parse raises NotImplementedError."""
    parser = SolverLogParser()
    with pytest.raises(NotImplementedError):
        parser.parse("some log")


@pytest.mark.parametrize(
    "log, expected",
    [
        (
            "Status = kOpt\nUpper bound = 1234.5\nLower bound = 1234.0\n",
            {
                "status": "kOpt",
                "objective_value": 1234.5,
                "upper_bound": 1234.5,
                "lower_bound": 1234.0,
            },
        ),
        (
            "No status line here",
            {
                "status": "Failed",
                "objective_value": float("nan"),
                "upper_bound": float("nan"),
                "lower_bound": float("nan"),
            },
        ),
        (
            "Status = kUnbounded\n",
            {
                "status": "kUnbounded",
                "objective_value": float("nan"),
                "upper_bound": float("nan"),
                "lower_bound": float("nan"),
            },
        ),
    ],
)
def test_status_bounds_solver_log_parser(log, expected):
    """StatusBoundsSolverLogParser extracts status, bounds, and objective."""
    parser = StatusBoundsSolverLogParser(
        status_pattern="Status = (.*)\n",
        upper_bound_pattern="Upper bound = (.*)\n",
        lower_bound_pattern="Lower bound = (.*)\n",
    )
    result = parser.parse(log)
    assert result["status"] == expected["status"]
    if np.isnan(expected["objective_value"]):
        assert np.isnan(result["objective_value"])
        assert np.isnan(result["upper_bound"])
        assert np.isnan(result["lower_bound"])
    else:
        assert result["objective_value"] == pytest.approx(expected["objective_value"])
        assert result["upper_bound"] == pytest.approx(expected["upper_bound"])
        assert result["lower_bound"] == pytest.approx(expected["lower_bound"])


@pytest.mark.parametrize(
    "log, expected_status, expected_obj",
    [
        (
            "Solution value: 5678.9\nSolver status: kOpt\n",
            "Success (kOpt)",
            5678.9,
        ),
        (
            "No objective line here",
            "Failed",
            float("nan"),
        ),
    ],
)
def test_objective_value_solver_log_parser(log, expected_status, expected_obj):
    """ObjectiveValueSolverLogParser extracts objective value and status."""
    parser = ObjectiveValueSolverLogParser(
        objective_pattern="Solution value: (.*)\n",
    )
    result = parser.parse(log)
    assert result["status"] == expected_status
    if np.isnan(expected_obj):
        assert np.isnan(result["objective_value"])
    else:
        assert result["objective_value"] == pytest.approx(expected_obj)
    assert np.isnan(result["lower_bound"])
    assert np.isnan(result["upper_bound"])


def test_objective_value_solver_log_parser_missing_status():
    """ObjectiveValueSolverLogParser falls back to 'unknown' when status is absent."""
    parser = ObjectiveValueSolverLogParser(
        objective_pattern="Solution value: (.*)\n",
    )
    result = parser.parse("Solution value: 10.0\n")
    assert result["status"] == "Success (unknown)"


# ---------------------------------------------------------------------------
# Tests for parse_solver_log on SMSPPSolverTool and subclasses
# ---------------------------------------------------------------------------


def test_parse_solver_log_raises_when_log_is_none():
    """parse_solver_log raises ValueError if optimize has not been called."""
    for cls in (
        UCBlockSolver,
        TSSBlockSolver,
        InvestmentBlockSolver,
        SDDPSolver,
        InvestmentBlockTestSolver,
    ):
        solver = _make_solver(cls)
        with pytest.raises(ValueError, match="Optimization was not launched"):
            solver.parse_solver_log()


def test_parse_solver_log_base_raises_not_implemented():
    """Base class raises NotImplementedError when no parser is configured."""
    solver = _make_solver(SMSPPSolverTool)
    solver._log = "some log"
    with pytest.raises(NotImplementedError):
        solver.parse_solver_log()


@pytest.mark.parametrize("cls", [UCBlockSolver, TSSBlockSolver])
def test_parse_solver_log_pattern_a_success(cls):
    """Solvers using StatusBoundsSolverLogParser parse a successful log correctly."""
    solver = _make_solver(cls)
    solver._log = "Status = kOpt\nUpper bound = 1234.5\nLower bound = 1234.0\n"
    solver.parse_solver_log()
    assert solver.status == "kOpt"
    assert solver.objective_value == pytest.approx(1234.5)
    assert solver.upper_bound == pytest.approx(1234.5)
    assert solver.lower_bound == pytest.approx(1234.0)


@pytest.mark.parametrize("cls", [UCBlockSolver, TSSBlockSolver])
def test_parse_solver_log_pattern_a_failure(cls):
    """Solvers using StatusBoundsSolverLogParser set Failed when pattern is not found."""
    solver = _make_solver(cls)
    solver._log = "No status line here"
    solver.parse_solver_log()
    assert solver.status == "Failed"
    assert np.isnan(solver.objective_value)
    assert np.isnan(solver.lower_bound)
    assert np.isnan(solver.upper_bound)


@pytest.mark.parametrize("cls", [InvestmentBlockSolver, SDDPSolver])
def test_parse_solver_log_pattern_b_success(cls):
    """Solvers using ObjectiveValueSolverLogParser parse a successful log correctly."""
    solver = _make_solver(cls)
    solver._log = "Solution value: 5678.9\nSolver status: kOpt\n"
    solver.parse_solver_log()
    assert solver.status == "Success (kOpt)"
    assert solver.objective_value == pytest.approx(5678.9)
    assert np.isnan(solver.lower_bound)
    assert np.isnan(solver.upper_bound)


@pytest.mark.parametrize("cls", [InvestmentBlockSolver, SDDPSolver])
def test_parse_solver_log_pattern_b_failure(cls):
    """Solvers using ObjectiveValueSolverLogParser set Failed when pattern is not found."""
    solver = _make_solver(cls)
    solver._log = "No objective value here"
    solver.parse_solver_log()
    assert solver.status == "Failed"
    assert np.isnan(solver.objective_value)


def test_parse_solver_log_investment_block_test_solver_success():
    """InvestmentBlockTestSolver parses Fi* objective correctly."""
    solver = _make_solver(InvestmentBlockTestSolver)
    solver._log = "Fi* = 42.0\nSolver status: kOpt\n"
    solver.parse_solver_log()
    assert solver.status == "Success (kOpt)"
    assert solver.objective_value == pytest.approx(42.0)
    assert np.isnan(solver.lower_bound)
    assert np.isnan(solver.upper_bound)


def test_parse_solver_log_investment_block_test_solver_failure():
    """InvestmentBlockTestSolver sets Failed status when Fi* is not found."""
    solver = _make_solver(InvestmentBlockTestSolver)
    solver._log = "No Fi* line here"
    solver.parse_solver_log()
    assert solver.status == "Failed"
    assert np.isnan(solver.objective_value)


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
    configfile = SMSConfig(template="UCBlock/uc_solverconfig.txt")

    ucs = UCBlockSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    if ucs.is_available() or force_smspp:
        ucs.optimize(logging=False)

        assert "Success" in ucs.status
        assert np.isclose(ucs.objective_value, 3615.760710, atol=ATOL, rtol=RTOL)
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_optimize_ucsolver(force_smspp):
    b = SMSNetwork(file_type=SMSFileType.eBlockFile)
    add_ucblock_with_one_unit(b)

    fp_log = get_temp_file("test_optimize_ucsolver.txt")
    fp_temp = get_temp_file("test_optimize_ucsolver.nc")
    configfile = SMSConfig(template="UCBlock/uc_solverconfig.txt")

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
    configfile = SMSConfig(template="UCBlock/uc_solverconfig.txt")

    if UCBlockSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log, logging=True)

        assert "success" in result.status.lower()
        assert "error" not in result.log.lower()
        assert "ThermalUnitBlock" in result.log
        assert "BatteryUnitBlock" in result.log
        assert "HydroUnitBlock" in result.log
        assert "IntermittentUnitBlock" in result.log
        assert "SlackUnitBlock" in result.log
    else:
        pytest.skip("UCBlockSolver not available in PATH")


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
        ucs.optimize(logging=True)

        assert "success" in ucs.status.lower()
    else:
        pytest.skip("InvestmentBlockTestSolver not available in PATH")


def test_is_smspp_installed(force_smspp):
    """Test the is_smspp_installed() function."""
    from pysmspp import is_smspp_installed, UCBlockSolver, InvestmentBlockTestSolver

    # The function should return a boolean
    result = is_smspp_installed()
    assert isinstance(result, bool)

    # Test with multiple solvers
    result_multi = is_smspp_installed([UCBlockSolver, InvestmentBlockTestSolver])
    assert isinstance(result_multi, bool)

    # When force_smspp is True, is_smspp_installed must return True
    if force_smspp:
        assert result is True, (
            "is_smspp_installed should return True when --force-smspp is set"
        )
        assert result_multi is True, (
            "is_smspp_installed should return True for all solvers when --force-smspp is set"
        )


def test_optimize_tssbsolver(force_smspp):
    fp_network = get_network("TSSB_EC_CO_Test_TUB_simple.nc4")
    fp_log = get_temp_file("test_optimize_tssbsolver.txt")
    configfile = SMSConfig(template="TSSBlock/TSSBSCfg.txt")

    # Create a new TSSB block from the original network and save to a temp file
    fp_tssb_new = get_temp_file("test_tssb_new.nc4")
    fp_log_new = get_temp_file("test_optimize_tssbsolver_new.txt")

    build_tssb_block(fp_network).to_netcdf(fp_tssb_new, force=True)

    # Copy the original EC_CO_Test_TUB.nc4 to a temp location
    fp_ec = get_network("EC_CO_Test_TUB.nc4")
    fp_ec_copy = get_temp_file("EC_CO_Test_TUB.nc4")
    shutil.copy(fp_ec, fp_ec_copy)

    from pysmspp import TSSBlockSolver

    tssb_solver = TSSBlockSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    tssb_solver_new = TSSBlockSolver(
        configfile=str(configfile),
        fp_network=fp_tssb_new,
        fp_log=fp_log_new,
    )

    if tssb_solver.is_available() or force_smspp:
        tssb_solver.optimize(logging=True)

        assert "success" in tssb_solver.status.lower()

        tssb_solver_new.optimize(logging=True)

        assert "success" in tssb_solver_new.status.lower()

        obj_orig = tssb_solver.objective_value
        obj_new = tssb_solver_new.objective_value
        assert obj_orig == pytest.approx(obj_new, rel=1e-4), (
            "Objective values should match between original ({:.2f}) and new ({:.2f}) TSSB blocks".format(
                obj_orig, obj_new
            )
        )
    else:
        pytest.skip("TSSBBlockSolver not available in PATH")
