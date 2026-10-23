# Description of available configuration files

- UCBlock/{uc_solverconfig.txt, OSolCfg.txt} copied from smspp-project/tools/ucblock_solver.
- InvestmentBlock/{BSPar.txt, uc_solverconfig.txt}, copied from smspp-project/InvestmentBlock/test/config.
- TSSBlock/* copied from smspp-project/tools/tssb_solver.
- SVMBlock/* copied from smspp-project/tests/SVMBlock and smspp-project/tools/svm_solver.

For SVMBlock, SVMCfg.txt and SVMCfg-primal.txt are BlockConfig, which is what chooses the formulation of the training problem the abstract representation encodes, respectively the Wolfe dual and the training problem itself; SVMSCfg.txt trains the model with the ad hoc SMOSolver, SVMSCfg_grb.txt with Gurobi and SVMSCfg-LD.txt with a LagrangianDualSolver, the last one applying to the Block that the svm_solver option "s" assembles rather than to the SVMBlock itself.

For uc_solverconfig in both folders, the version using Gurobi is also provided under name uc_solverconfig_grb.
The template configuration option for OSolCfg.txt allows to extract the most information from tools.
