import shutil
from pathlib import Path
import subprocess
import re
import numpy as np
import os


class SMSPPSolverTool:
    """
    Base class for the SMS++ solver tools.
    """

    def __init__(
        self,
        exec_file: str = "",
        exec_optimize=None,
        help_option: str = "-h",
        fp_network: Path | str = None,
        configfile: Path | str = None,
        fp_out: Path | str = None,
        fp_log: Path | str = None,
        out_dir: Path | str = None,
    ):
        """
        Constructor for an abstract SMSPPSolverTool.

        Parameters
        ----------
        exec_file : str
            The name of the executable file.
        exec_optimize : function
            The function to run the optimization.
            It takes as input the SMSPPSolverTool instance and returns the executable path to run the tool.
        help_option : str, optional
            The option to display the help message, by default "-h".
        fp_network : Path | str, optional
            Path to the SMSpp network to solve, by default None.
        configfile : Path | str, optional
            Path to the configuration file, by default None.
        fp_out : Path | str, optional
            Path to the output file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        out_dir : Path | str, optional
            Path to the output directory, by default None.
        """
        self._exec_file = exec_file
        self._exec_optimize = exec_optimize
        self._help_option = help_option

        self.fp_network = str(Path(fp_network).resolve())
        self.configfile = str(Path(configfile).resolve())
        self.configdir = str(Path(configfile).resolve().parent.resolve())
        self.fp_log = None if fp_log is None else str(Path(fp_log).resolve())
        self.fp_out = None if fp_out is None else str(Path(fp_out).resolve())
        if out_dir is not None:
            self.outdir = str(Path(out_dir).resolve())
        elif fp_out is not None:
            self.outdir = str(Path(fp_out).resolve().parent)
        elif fp_log is not None:
            self.outdir = str(Path(fp_log).resolve().parent)
        else:
            self.outdir = None
        if not self.configdir.endswith("/"):
            self.configdir += "/"
        if self.outdir is not None and not self.outdir.endswith("/"):
            self.outdir += "/"

        self._status = None
        self._log = None
        self._objective_value = None
        self._lower_bound = None
        self._upper_bound = None

    def calculate_executable_call(self):
        """
        Calculate the executable call to run the solver tool.
        """
        self._exec_optimize()

    def __repr__(self):
        return f"{type(self).__name__}\n\t\n\texec_file={self._exec_file}\n\tstatus={self.status}\n\tconfigfile={self.configfile}\n\tfp_network={self.fp_network}\n\tfp_out={self.fp_out}"

    def help(self, print_message=True):
        """
        Print the help message of the SMS++ solver tool.

        >>> solver.help()

        Parameters
        ----------
        print_message : bool, optional
            Whether to print the message, by default True.

        Returns
        -------
        The help message.
        """
        result = subprocess.run(
            f"{self._exec_file} {self._help_option}", capture_output=True, shell=True
        )
        msg = result.stdout.decode("utf-8") + os.linesep + result.stderr.decode("utf-8")
        if print_message:
            print(msg)
        return msg

    def optimize(self, **kwargs):
        """
        Run the SMSPP Solver tool.

        Parameters
        ----------
        fp_n : str
            File path to the network file.
        **kwargs
            Additional keyword arguments to pass to the function.
        """
        if not Path(self.configfile).exists():
            raise FileNotFoundError(
                f"Configuration file {self.configfile} does not exist."
            )
        if not Path(self.fp_network).exists():
            raise FileNotFoundError(f"Network file {self.fp_network} does not exist.")
        result = subprocess.run(
            self.calculate_executable_call(),
            capture_output=True,
            shell=True,
        )
        self._log = (
            result.stdout.decode("utf-8") + os.linesep + result.stderr.decode("utf-8")
        )
        self.parse_ucblock_solver_log()
        if result.returncode != 0:
            raise ValueError(
                f"Failed to run {self._exec_file}; error log:\n{result.stderr.decode('utf-8')}"
            )
        # write output to file, if option passed
        if self.fp_log is not None:
            Path(self.fp_log).parent.mkdir(parents=True, exist_ok=True)
            with open(self.fp_log, "w") as f:
                f.write(self._log)

        return self

    def is_available(self):
        """
        Check if the SMS++ tool is available in the PATH.
        """
        return shutil.which(self._exec_file) is not None

    def parse_ucblock_solver_log(self):
        """
        Check the output of the SolverTool.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        Parameters
        ----------
        log : str
            The path to the output file.
        """
        raise NotImplementedError(
            "Method parse_ucblock_solver_log must be implemented in the derived class."
        )

    @property
    def status(self):
        return self._status

    @property
    def log(self):
        return self._log

    @property
    def objective_value(self):
        return self._objective_value

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound


class UCBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the UCBlockSolver tool from SMS++.
    """

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_out: Path | str = None,
        fp_log: Path | str = None,
    ):
        """
        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_out : Path | str, optional
            Path to the output file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="ucblock_solver",
            exec_optimize=self.calculate_executable_call,
            help_option="-h",
            fp_network=fp_network,
            configfile=configfile,
            fp_out=fp_out,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        exec_path = (
            f"ucblock_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        )
        if self.fp_out is not None:
            exec_path += f" -o -O {self.fp_out}"
        return exec_path

    def parse_ucblock_solver_log(self):
        """
        Check the output of the UCBlockSolver.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        Parameters
        ----------
        log : str
            The path to the output file.
        """
        if self._log is None:
            raise ValueError("Optimization was not launched.")

        res = re.search("Status = (.*)\n", self._log)

        if not res:  # if success not found
            self._status = "Failed"
            self._objective_value = np.nan
            self._lower_bound = np.nan
            self._upper_bound = np.nan
            return

        smspp_status = res.group(1).replace("\r", "")
        self._status = smspp_status

        res = re.search("Upper bound = (.*)\n", self._log)
        up = float(res.group(1).replace("\r", ""))

        res = re.search("Lower bound = (.*)\n", self._log)
        lb = float(res.group(1).replace("\r", ""))

        self._objective_value = up
        self._lower_bound = up
        self._upper_bound = lb


class InvestmentBlockTestSolver(SMSPPSolverTool):
    """
    Class to interact with the InvestmentBlockTestSolver tool from SMS++, with executable file "InvestmentBlock_test".
    """

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_out: Path | str = None,
        fp_log: Path | str = None,
    ):
        """
        Constructor for the InvestmentBlockTestSolver, with executable file "InvestmentBlock_test".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_out : Path | str, optional
            Path to the output file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="InvestmentBlock_test",
            exec_optimize=self.calculate_executable_call,
            help_option="-h",
            fp_network=fp_network,
            configfile=configfile,
            fp_out=fp_out,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        exec_path = f"InvestmentBlock_test {self.fp_network} -c {self.configdir} -S {self.configfile}"
        return exec_path

    def parse_ucblock_solver_log(
        self,
    ):  # TODO: needs revision to better capture the output
        """
        Check the output of the InvestmentBlockTestSolver.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        Parameters
        ----------
        log : str
            The path to the output file.
        """
        if self._log is None:
            raise ValueError("Optimization was not launched.")

        res = re.search("Solution value: (.*)\n", self._log)

        if not res:  # if success not found
            self._status = "Failed"
            self._objective_value = np.nan
            self._lower_bound = np.nan
            self._upper_bound = np.nan
            return

        self._objective_value = float(res.group(1).replace("\r", ""))

        res = re.search("Solver status: (.*)\n", self._log)
        smspp_status = res.group(1).replace("\r", "")

        if np.isfinite(self._objective_value):
            self._status = f"Success ({smspp_status})"
        else:
            self._status = f"Failed ({smspp_status})"

        self._lower_bound = np.nan
        self._upper_bound = np.nan


class InvestmentBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the InvestmentBlockSolver tool from SMS++, with name "investment_solver".
    """

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_out: Path | str = None,
        fp_log: Path | str = None,
    ):
        """
        Constructor for the InvestmentBlockSolver, with executable file "investment_solver".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_out : Path | str, optional
            Path to the output file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="investment_solver",
            exec_optimize=self.calculate_executable_call,
            help_option="-h",
            fp_network=fp_network,
            configfile=configfile,
            fp_out=fp_out,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        exec_path = f"investment_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        if self.fp_out is not None:
            exec_path += f" -o -O {self.fp_out}"
        return exec_path

    def parse_ucblock_solver_log(
        self,
    ):  # TODO: needs revision to better capture the output
        """
        Check the output of the InvestmentBlockSolver.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        Parameters
        ----------
        log : str
            The path to the output file.
        """
        if self._log is None:
            raise ValueError("Optimization was not launched.")

        res = re.search("Solution value: (.*)\n", self._log)

        if not res:  # if success not found
            self._status = "Failed"
            self._objective_value = np.nan
            self._lower_bound = np.nan
            self._upper_bound = np.nan
            return

        self._objective_value = float(res.group(1).replace("\r", ""))

        res = re.search("Solver status: (.*)\n", self._log)
        smspp_status = res.group(1).replace("\r", "")

        if np.isfinite(self._objective_value):
            self._status = f"Success ({smspp_status})"
        else:
            self._status = f"Failed ({smspp_status})"

        self._lower_bound = np.nan
        self._upper_bound = np.nan


class SDDPSolver(SMSPPSolverTool):
    """
    Class to interact with the SDDPSolver tool from SMS++, with name "sddp_solver".
    """

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_out: Path | str = None,
        fp_log: Path | str = None,
    ):
        """
        Constructor for the SDDPSolver, with executable file "sddp_solver".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_out : Path | str, optional
            Path to the output file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="sddp_solver",
            exec_optimize=self.calculate_executable_call,
            help_option="-h",
            fp_network=fp_network,
            configfile=configfile,
            fp_out=fp_out,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        exec_path = (
            f"sddp_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        )
        if self.fp_out is not None:
            exec_path += f" -o -O {self.fp_out}"
        return exec_path

    def parse_ucblock_solver_log(
        self,
    ):  # TODO: needs revision to better capture the output
        """
        Check the output of the InvestmentBlockSolver.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        Parameters
        ----------
        log : str
            The path to the output file.
        """
        if self._log is None:
            raise ValueError("Optimization was not launched.")

        res = re.search("Solution value: (.*)\n", self._log)

        if not res:  # if success not found
            self._status = "Failed"
            self._objective_value = np.nan
            self._lower_bound = np.nan
            self._upper_bound = np.nan
            return

        self._objective_value = float(res.group(1).replace("\r", ""))

        res = re.search("Solver status: (.*)\n", self._log)
        smspp_status = res.group(1).replace("\r", "")

        if np.isfinite(self._objective_value):
            self._status = f"Success ({smspp_status})"
        else:
            self._status = f"Failed ({smspp_status})"

        self._lower_bound = np.nan
        self._upper_bound = np.nan
