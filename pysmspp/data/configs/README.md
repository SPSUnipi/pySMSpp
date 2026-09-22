# Description of available configuration files

- UCBlock/{uc_solverconfig.txt, OSolCfg.txt} copied from smspp-project/tools/ucblock_solver.
- InvestmentBlock/{BSPar.txt, uc_solverconfig.txt}, copied from smspp-project/InvestmentBlock/test/config.
- TSSBlock/* copied from smspp-project/tools/tssb_solver.
- SVMBlock/* copied from smspp-project/tests/SVMBlock and smspp-project/tools/svm_solver.

For SVMBlock, SVMCfg.txt and SVMCfg-primal.txt are BlockConfig, which is what chooses the formulation of the training problem the abstract representation encodes, respectively the Wolfe dual and the training problem itself; SVMSCfg.txt trains the model with the ad hoc SMOSolver, SVMSCfg_grb.txt with Gurobi and SVMSCfg-LD.txt with a LagrangianDualSolver, the last one applying to the Block that the svm_solver option "s" assembles rather than to the SVMBlock itself.

For uc_solverconfig in both folders, the version using Gurobi is also provided under name uc_solverconfig_grb.
The template configuration option for OSolCfg.txt allows to extract the most information from tools.

TSSBlock/TSSBSCfg-IP.txt, TSSBSCfg-LD-IP.txt, TSSBSCfg-LDLD.txt and TSSBSCfg-LDrec.txt solve a two-stage problem whose scenario is a unit commitment with a :MILPSolver, with the Lagrangian dual of the scenarios, with a chain of two duals down to the units and with the recursive Lagrangian dual, respectively; TSSBSCfg-PPH.txt adds to the dual of the scenarios the PrimalProximalHeur, which gives a feasible solution by fixing the design to its mean over the scenarios. They need the BlockConfig InnerBCfg.txt (option -B, i.e., `B="InnerBCfg.txt"` of TSSBSolver); the duals give a bound, and option `-R BSCfg1-IP.txt` of smspp_tssb_solver recovers a feasible solution from it. TSSBSCfg-LD-IP-par.txt, TSSBSCfg-LDLD-par.txt and TSSBSCfg-LDrec-par.txt are the same three duals with a ParallelBundleSolver, which evaluates the components of an iteration in 8 threads. TSSBSCfg-LP.txt solves the continuous relaxation with a :MILPSolver, and TSSBSCfg-PIPS.txt (with PIPSCfg.txt) the same linear program with PIPS-IPM++, under mpirun.

TSSBlock/TSSBSCfg-BDS.txt attaches a BendersDecompositionSolver, configured by BDSMCfg.txt and BDSSCfg.txt, to the Benders form of a two-stage problem, which smspp_tssb_solver assembles when given -k (`k=None` of TSSBSolver), also around a MultiStageStochasticBlock, whose leaves are then the subproblems. TSSBlock/TSSBSCfg-IB.txt is the ad hoc Benders decomposition of the same problem: a BundleSolver on an InvestmentBlock over the TSSB or the MSSB (the `investment_outside` form of pypsa2smspp), whose inner Block is solved whole at every evaluation by BSCfg-IB.txt.

The templates that use the BundleSolver are written for the BundleSolver 2.0: `strMPBSolverCfg` names MPBCfg.txt, the BlockSolverConfig of the Solver of its master, and they do not load with an SMS++ whose bundle is the 1.0.

