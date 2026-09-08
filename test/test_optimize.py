import os
import shutil
from pathlib import Path

import numpy as np
import pytest
from conftest import (
    add_base_ucblock,
    add_bub_to_ucblock,
    add_hub_to_ucblock,
    add_iub_to_ucblock,
    add_sub_to_ucblock,
    add_tub_to_ucblock,
    add_ucblock_with_one_unit,
    build_svm_network,
    build_tssb_block,
    get_network,
    get_temp_file,
)

from pysmspp import (
    InvestmentBlockSolver,
    SMSConfig,
    SMSFileType,
    SMSNetwork,
    UCBlockSolver,
)

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


def test_shell_ucblocksolver():
    # skip if not linux os
    if os.name != "posix":
        pytest.skip("Shell command test only applicable on Linux/Unix systems")

    fp_network = get_network("microgrid_ALLbutStore_1N.nc4")
    fp_config = SMSConfig(template="UCBlock/uc_solverconfig.txt")

    solver_cmd = "bash -lc \"printf 'Status = Success\\nUpper bound = 123.0\\nLower bound = 120.0\\n'\""

    ucs = UCBlockSolver(
        solver_path=solver_cmd,
        fp_network=str(fp_network),
        configfile=str(fp_config),
        shell=True,
    )

    ucs.optimize(logging=False)

    assert "Success" in ucs.status
    assert ucs.objective_value == pytest.approx(123.0)
    assert ucs.lower_bound == pytest.approx(120.0)


def test_help_investmentblocksolver(force_smspp):
    ibts = InvestmentBlockSolver()

    if ibts.is_available() or force_smspp:
        help_msg = ibts.help()

        assert "SMS++ investment solver" in help_msg
    else:
        pytest.skip("InvestmentBlockSolver not available in PATH")


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


def test_optimize_example_custom_solver_path(force_smspp):
    if not UCBlockSolver().is_available() and not force_smspp:
        pytest.skip("UCBlockSolver not available in PATH and --force-smspp not set")

    fp_network = get_network()
    fp_log = get_temp_file("test_optimize_example.txt")
    configfile = SMSConfig(template="UCBlock/uc_solverconfig.txt")

    path_ucsolver = shutil.which("ucblock_solver")

    ucs = UCBlockSolver(
        solver_path=Path(path_ucsolver),
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    ucs.optimize(logging=False)

    assert "Success" in ucs.status
    assert np.isclose(ucs.objective_value, 3615.760710, atol=ATOL, rtol=RTOL)


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
    else:
        pytest.skip("UCBlockSolver not available in PATH")


def test_investmentsolvertest(force_smspp):
    fp_network = get_network("investment_1N.nc4")
    fp_log = get_temp_file("test_optimize_investmentsolvertest.txt")
    configfile = SMSConfig(template="InvestmentBlock/BSPar.txt")

    ucs = InvestmentBlockSolver(
        configfile=str(configfile),
        fp_network=fp_network,
        fp_log=fp_log,
    )

    if InvestmentBlockSolver().is_available() or force_smspp:
        ucs.optimize(logging=True)

        assert "success" in ucs.status.lower()
    else:
        pytest.skip("InvestmentBlockSolver not available in PATH")


def test_is_smspp_installed(force_smspp):
    """Test the is_smspp_installed() function."""
    from pysmspp import InvestmentBlockSolver, UCBlockSolver, is_smspp_installed

    # The function should return a boolean
    result = is_smspp_installed()
    assert isinstance(result, bool)

    # Test with multiple solvers
    result_multi = is_smspp_installed([UCBlockSolver(), InvestmentBlockSolver()])
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

    from pysmspp import TSSBSolver

    tssb_solver = TSSBSolver(
        fp_network=fp_network,
        fp_log=fp_log,
        configfile=str(configfile),
    )

    tssb_solver_new = TSSBSolver(
        fp_network=fp_tssb_new,
        fp_log=fp_log_new,
        configfile=str(configfile),
    )

    if tssb_solver.is_available() or force_smspp:
        tssb_solver.optimize(logging=True)

        assert "success" in tssb_solver.status.lower()

        tssb_solver_new.optimize(logging=True)

        assert "success" in tssb_solver_new.status.lower()

        obj_orig = tssb_solver.objective_value
        obj_new = tssb_solver_new.objective_value
        assert obj_orig == pytest.approx(obj_new, rel=1e-4), (
            f"Objective values should match between original ({obj_orig:.2f}) and new ({obj_new:.2f}) TSSB blocks"
        )
    else:
        pytest.skip("TSSBBlockSolver not available in PATH")


def test_help_svmsolver(force_smspp):
    from pysmspp import SVMSolver

    svm = SVMSolver()

    if svm.is_available() or force_smspp:
        assert "SMS++ SVM solver" in svm.help()
    else:
        pytest.skip("SVMSolver not available in PATH")


def test_optimize_svmblock_classification(force_smspp):
    """
    Train a SVCBlock with the ad hoc SMOSolver.
    """
    from pysmspp import SVMSolver

    b = build_svm_network("SVCBlock", C=10.0)

    fp_log = get_temp_file("test_optimize_svcblock.txt")
    fp_temp = get_temp_file("test_optimize_svcblock.nc")
    configfile = SMSConfig(template="SVMBlock/SVMSCfg.txt")

    if SVMSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log)

        assert "Success" in result.status
        assert result.score_name == "accuracy"
        assert result.training_score >= 0.9
    else:
        pytest.skip("SVMSolver not available in PATH")


def test_optimize_svmblock_regression(force_smspp):
    """
    Train a SVRBlock with the ad hoc SMOSolver.
    """
    from pysmspp import SVMSolver

    b = build_svm_network("SVRBlock", C=100.0, Epsilon=0.1)

    fp_log = get_temp_file("test_optimize_svrblock.txt")
    fp_temp = get_temp_file("test_optimize_svrblock.nc")
    configfile = SMSConfig(template="SVMBlock/SVMSCfg.txt")

    if SVMSolver().is_available() or force_smspp:
        result = b.optimize(configfile, fp_temp, fp_log)

        assert "Success" in result.status
        assert result.score_name == "R2"
        assert result.training_score >= 0.9
    else:
        pytest.skip("SVMSolver not available in PATH")


def test_optimize_svmblock_formulations(force_smspp):
    """
    The training problem has the same value in every formulation and with
    every Solver: the Wolfe dual and the primal solved by a :MILPSolver, the
    dual solved by the ad hoc SMOSolver, the consensus structure of the
    problem in chunks solved by a LagrangianDualSolver, and LIBSVM, which is
    only in the Solver factory when SVMBlock has been built with it.
    """
    from pysmspp import SVMSolver

    if not SVMSolver().is_available() and not force_smspp:
        pytest.skip("SVMSolver not available in PATH")

    fp_network = get_temp_file("test_svmblock_formulations.nc")
    build_svm_network("SVCBlock", C=10.0).to_netcdf(fp_network, force=True)

    runs = {
        "dual/SMO": ("SVMBlock/SVMSCfg.txt", {}),
        "dual/MILP": ("SVMBlock/SVMSCfg_grb.txt", {}),
        "primal/MILP": ("SVMBlock/SVMSCfg_grb.txt", {"B": "SVMCfg-primal.txt"}),
        "chunks/LD": ("SVMBlock/SVMSCfg-LD.txt", {"s": 4}),
        "dual/LIBSVM": ("SVMBlock/SVMSCfg-libsvm.txt", {}),
    }

    values = {}
    for name, (template, kwargs) in runs.items():
        svm = SVMSolver(
            fp_network=fp_network,
            configfile=str(SMSConfig(template=template)),
            **kwargs,
        )
        svm.optimize(logging=False)

        if name == "dual/LIBSVM" and "Success" not in svm.status:
            # LIBSVMSolver is only in the Solver factory when SVMBlock has
            # been built with LIBSVM, which is an optional dependency
            continue

        assert "Success" in svm.status
        values[name] = svm.objective_value

    reference = values["dual/SMO"]
    for name, value in values.items():
        assert value == pytest.approx(reference, rel=1e-4), (
            f"the value of the training problem of {name} ({value:.6f}) differs from the "
            f"one of dual/SMO ({reference:.6f})"
        )


def test_svmsolver_model_selection(force_smspp):
    """
    A k-fold cross-validation over a grid of hyper-parameters reports the
    score of each point of the grid and the best one.
    """
    from pysmspp import SVMSolver

    if not SVMSolver().is_available() and not force_smspp:
        pytest.skip("SVMSolver not available in PATH")

    fp_network = get_temp_file("test_svmsolver_model_selection.nc")
    build_svm_network("SVCBlock").to_netcdf(fp_network, force=True)

    svm = SVMSolver(
        fp_network=fp_network,
        configfile=str(SMSConfig(template="SVMBlock/SVMSCfg.txt")),
        k=4,
        g="C=0.1,1,10",
    )
    svm.optimize(logging=False)

    assert "Success" in svm.status
    assert len(svm.scores) == 3

    for point in svm.scores:
        assert len(point["scores"]) == 4  # one score per fold
        assert set(point["params"]) == {"C"}

    assert svm.best_score == pytest.approx(max(p["score"] for p in svm.scores))
    assert svm.best_params["C"] in (0.1, 1.0, 10.0)


def test_svmblock_hyperparameters(force_smspp):
    """
    The hyper-parameters reach the solver, i.e., they are scalar variables of
    the group and not attributes of it, which SMS++ would silently ignore.
    """
    from pysmspp import SVMSolver

    if not SVMSolver().is_available() and not force_smspp:
        pytest.skip("SVMSolver not available in PATH")

    configfile = str(SMSConfig(template="SVMBlock/SVMSCfg.txt"))

    def train(**kwargs):
        fp_network = get_temp_file("test_svmblock_hyperparameters.nc")
        build_svm_network("SVCBlock", **kwargs).to_netcdf(fp_network, force=True)

        svm = SVMSolver(fp_network=fp_network, configfile=configfile)
        svm.optimize(logging=False)

        assert "Success" in svm.status
        return svm.objective_value

    reference = train(C=1.0)

    # a larger C penalises the training errors more, and a nonlinear kernel,
    # a squared loss or a regularised bias are a different problem altogether
    assert train(C=10.0) > reference
    assert train(C=1.0, Kernel=2, Gamma=0.5) != pytest.approx(reference)
    assert train(C=1.0, SquaredLoss=1, RegBias=1) != pytest.approx(reference)


def test_svmsolver_trained_model(force_smspp):
    """
    The trained model is written to the solution file as a SVMBlockSolution,
    i.e., as the multipliers and the bias, and the samples whose multiplier
    is nonzero are the support vectors.
    """
    from pysmspp import SVMSolver

    if not SVMSolver().is_available() and not force_smspp:
        pytest.skip("SVMSolver not available in PATH")

    fp_network = get_temp_file("test_svmsolver_trained_model.nc")
    fp_solution = get_temp_file("test_svmsolver_trained_model_sol.nc")

    n_samples = 40
    build_svm_network("SVCBlock", C=10.0).to_netcdf(fp_network, force=True)

    svm = SVMSolver(
        fp_network=fp_network,
        configfile=str(SMSConfig(template="SVMBlock/SVMSCfg.txt")),
        fp_solution=fp_solution,
    )
    svm.optimize(logging=False)

    assert "Success" in svm.status

    model = svm.solution.blocks["Solution_0"]

    assert model.attributes["type"].value == "SVMBlockSolution"

    alphas = np.asarray(model.variables["Multipliers"].data)
    assert alphas.size == n_samples
    assert np.all(alphas >= -1e-9)
    assert np.all(alphas <= 10.0 + 1e-9)  # the multipliers are bounded by C

    support = np.count_nonzero(alphas)
    assert 0 < support < n_samples  # some samples support the model, not all

    assert np.isfinite(model.variables["Bias"].data)


def test_optimize_sddp(force_smspp):
    fp_network = get_network("sddp/SDDPBlock.nc4")
    fp_log = get_temp_file("test_optimize_sddp.txt")
    configfile = SMSConfig(template="SDDPBlock/SDDPSCfg.txt")

    from pysmspp import SDDPSolver

    sddp_solver = SDDPSolver(
        fp_network=fp_network,
        fp_log=fp_log,
        configfile=str(configfile),
    )

    if sddp_solver.is_available() or force_smspp:
        sddp_solver.optimize(logging=True)

        assert "success" in sddp_solver.status.lower()
    else:
        pytest.skip("SDDPSolver not available in PATH")
