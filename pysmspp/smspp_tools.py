import shutil
from pathlib import Path
import subprocess
import re
import numpy as np
import os
import time
import psutil


class SMSPPSolverTool:
    """
    Base class for the SMS++ solver tools.
    """

    # Class-level attributes for log parsing.
    # Subclasses configure these to avoid overriding parse_solver_log.
    #
    # Pattern A (UCBlockSolver, TSSBlockSolver): set _log_status_pattern,
    #   _log_upper_bound_pattern, and _log_lower_bound_pattern.
    # Pattern B (InvestmentBlockSolver, SDDPSolver, InvestmentBlockTestSolver):
    #   set _log_objective_pattern (and optionally _log_solver_status_pattern).
    _log_status_pattern = None
    _log_objective_pattern = None
    _log_upper_bound_pattern = None
    _log_lower_bound_pattern = None
    _log_solver_status_pattern = "Solver status: (.*)\n"

    def __init__(
        self,
        exec_file: str = "",
        help_option: str = "-h",
        fp_network: Path | str = None,
        configfile: Path | str = None,
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
    ):
        """
        Constructor for an abstract SMSPPSolverTool.

        Parameters
        ----------
        exec_file : str
            The name of the executable file.
        help_option : str, optional
            The option to display the help message, by default "-h".
        fp_network : Path | str, optional
            Path to the SMSpp network to solve, by default None.
        configfile : Path | str, optional
            Path to the configuration file, by default None.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        self._exec_file = exec_file
        self._help_option = help_option

        self.fp_network = str(Path(fp_network).resolve())
        self.configdir = str(Path(configfile).resolve().parent.resolve())
        self.configfile = str(Path(configfile).resolve().name)
        self.fp_log = None if fp_log is None else str(Path(fp_log).resolve())
        self.fp_solution = (
            None if fp_solution is None else str(Path(fp_solution).resolve())
        )
        if not self.configdir.endswith("/"):
            self.configdir += "/"

        self._status = None
        self._log = None
        self._objective_value = None
        self._lower_bound = None
        self._upper_bound = None
        self._solution = None
        self._subprocess_time = None
        self._solution_time = None
        self._computational_time = None

    def calculate_executable_call(self):
        """
        Calculate the executable call to run the solver tool.

        This method is meant to be overridden by subclasses. The base class
        implementation calls the function provided during initialization.

        Notes
        -----
        Subclasses override this method to return solver-specific command strings.
        """
        raise NotImplementedError(
            "Method calculate_executable_call must be implemented in the derived class."
        )

    def __repr__(self):
        """
        Return a string representation of the solver tool.

        Returns
        -------
        str
            A formatted string showing key solver properties.
        """
        return f"{type(self).__name__}\n\t\n\texec_file={self._exec_file}\n\tstatus={self.status}\n\tconfigfile={self.configfile}\n\tfp_network={self.fp_network}\n\tfp_solution={self.fp_solution}"

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

    def optimize(self, logging=True, tracking_period=0.1, **kwargs):
        """
        Run the SMSPP Solver tool.

        Parameters
        ----------
        logging : bool
            When true, logging is provided, including the executable call.
        tracking_period : float
            Delay in seconds between resource usage tracking samples.
        **kwargs
            Additional keyword arguments to pass to the function.
        """
        from pysmspp import SMSNetwork

        if not Path(Path(self.configdir).joinpath(self.configfile)).exists():
            raise FileNotFoundError(
                f"Configuration file {self.configfile} does not exist."
            )
        if not Path(self.fp_network).exists():
            raise FileNotFoundError(f"Network file {self.fp_network} does not exist.")

        command = self.calculate_executable_call()

        start_time = time.time()
        if logging:
            print(f"Executing command:\n{command}\n")

        process = psutil.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        os.set_blocking(process.stdout.fileno(), False)  # set non-blocking read
        os.set_blocking(process.stderr.fileno(), False)  # set non-blocking read
        process.cpu_percent()  # initialize cpu percent calculation

        def _get_msg_from_pipe(pipe, logging=False, buffer=4096):
            msg = ""
            for i in range(10_000):  # avoid infinite loops
                # read the buffer
                try:
                    msg_temp = os.read(pipe.fileno(), buffer).decode("utf-8")
                    if len(msg_temp) == 0:
                        break
                    msg += msg_temp
                except BlockingIOError:
                    break
            # print if requested
            if logging and len(msg) > 0:
                print(msg)
            return msg

        self._log = ""
        log_error = ""

        peak_memory = 0
        peak_cpu = 0

        loop = True
        while loop:
            if process.poll() is not None:
                loop = False
            else:
                try:
                    # capture resource usage when process is active
                    mem = process.memory_info().rss
                    cpu = process.cpu_percent()

                    # track the peak utilization of the process
                    if mem > peak_memory:
                        peak_memory = mem
                    if cpu > peak_cpu:
                        peak_cpu = cpu
                except psutil.NoSuchProcess:
                    pass

            # read from process without stopping it
            msg_out = _get_msg_from_pipe(process.stdout, logging)
            msg_err = _get_msg_from_pipe(process.stderr, logging)

            self._log += msg_out + msg_err
            log_error += msg_err

            time.sleep(tracking_period)

        # finalize logging
        self._log += _get_msg_from_pipe(process.stdout, logging)
        msg_err = _get_msg_from_pipe(process.stderr, logging)

        self._log += msg_err
        log_error += msg_err

        # add memory info to logging
        self._subprocess_time = time.time() - start_time

        msg = f"Peak CPU Usage: {peak_cpu:.2f} %"
        msg += f"\nPeak Memory Usage: {peak_memory / (1024**2):.2f} MB"
        msg += f"\nTotal Time: {self._subprocess_time:.2f} seconds\n"

        self._log += msg
        if logging:
            print(msg)

        self.parse_solver_log()

        if process.returncode != 0:
            raise ValueError(
                f"Failed to run {self._exec_file} with error log:\n{log_error}\n\nFull log:\n{self._log}"
            )

        # write output to file, if option passed
        if self.fp_log is not None:
            Path(self.fp_log).parent.mkdir(parents=True, exist_ok=True)
            with open(self.fp_log, "w") as f:
                f.write(self._log)

        # sets the solution object
        start_solution_time = time.time()
        if self.fp_solution is not None:
            if Path(self.fp_solution).exists():
                self._solution = SMSNetwork(self.fp_solution)
            else:
                raise FileNotFoundError(
                    f"solution file {self.fp_solution} does not exist."
                )
        else:
            self._solution = None
        self._solution_time = time.time() - start_solution_time
        self._computational_time = time.time() - start_time

        return self

    def is_available(self):
        """
        Check if the SMS++ tool is available in the PATH.
        """
        return shutil.which(self._exec_file) is not None

    def parse_solver_log(self):
        """
        Check the output of the SolverTool.
        It will extract the status, upper bound, lower bound, and objective value from the log.

        The parsing behaviour is controlled by class-level pattern attributes:

        - **Pattern A** (e.g. UCBlockSolver, TSSBlockSolver): set
          ``_log_status_pattern``, ``_log_upper_bound_pattern``, and
          ``_log_lower_bound_pattern``.
        - **Pattern B** (e.g. InvestmentBlockSolver, SDDPSolver,
          InvestmentBlockTestSolver): set ``_log_objective_pattern`` and,
          optionally, ``_log_solver_status_pattern``.

        Subclasses that require custom parsing logic may still override this
        method directly.
        """
        if self._log is None:
            raise ValueError("Optimization was not launched.")

        if self._log_status_pattern is not None:
            # Pattern A: extract status, upper bound, and lower bound
            res = re.search(self._log_status_pattern, self._log)

            if not res:
                self._status = "Failed"
                self._objective_value = np.nan
                self._lower_bound = np.nan
                self._upper_bound = np.nan
                return

            self._status = res.group(1).replace("\r", "")

            if self._log_upper_bound_pattern:
                res = re.search(self._log_upper_bound_pattern, self._log)
                if res:
                    ub = float(res.group(1).replace("\r", ""))
                    self._upper_bound = ub
                    self._objective_value = ub

            if self._log_lower_bound_pattern:
                res = re.search(self._log_lower_bound_pattern, self._log)
                if res:
                    lb = float(res.group(1).replace("\r", ""))
                    self._lower_bound = lb

        elif self._log_objective_pattern is not None:
            # Pattern B: extract objective value and solver status
            res = re.search(self._log_objective_pattern, self._log)

            if not res:
                self._status = "Failed"
                self._objective_value = np.nan
                self._lower_bound = np.nan
                self._upper_bound = np.nan
                return

            self._objective_value = float(res.group(1).replace("\r", ""))
            self._lower_bound = np.nan
            self._upper_bound = np.nan

            res = re.search(self._log_solver_status_pattern, self._log)
            if res:
                smspp_status = res.group(1).replace("\r", "")
            else:
                smspp_status = "unknown"

            if np.isfinite(self._objective_value):
                self._status = f"Success ({smspp_status})"
            else:
                self._status = f"Failed ({smspp_status})"

        else:
            raise NotImplementedError(
                "Method parse_solver_log must be implemented in the derived class "
                "or log patterns must be configured via class attributes."
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

    @property
    def solution(self):
        """
        Returns the solution of the optimization problem.
        This is a placeholder method and should be implemented in derived
        classes if applicable.
        """
        return self._solution

    @property
    def subprocess_time(self):
        """
        Returns the time taken to run the subprocess in seconds.
        This is a placeholder method and should be implemented in derived
        classes if applicable.
        """
        return self._subprocess_time

    @property
    def solution_time(self):
        """
        Returns the time taken to parse the solution in seconds.
        This is a placeholder method and should be implemented in derived
        classes if applicable.
        """
        return self._solution_time

    @property
    def computational_time(self):
        """
        Returns the total computational time of the optimization in seconds.
        This is a placeholder method and should be implemented in derived
        classes if applicable.
        """
        return self._computational_time


class UCBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the UCBlockSolver tool from SMS++.
    """

    _log_status_pattern = "Status = (.*)\n"
    _log_upper_bound_pattern = "Upper bound = (.*)\n"
    _log_lower_bound_pattern = "Lower bound = (.*)\n"

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
        **kwargs,
    ):
        """
        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="ucblock_solver",
            fp_network=fp_network,
            configfile=configfile,
            fp_solution=fp_solution,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        """
        Generate the command-line call for the UCBlock solver.

        Returns
        -------
        str
            The command string to execute the ucblock_solver.
        """
        exec_path = (
            f"ucblock_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        )
        if self.fp_solution is not None:
            exec_path += f" -o -O {self.fp_solution}"
        return exec_path


class InvestmentBlockTestSolver(SMSPPSolverTool):
    """
    Class to interact with the InvestmentBlockTestSolver tool from SMS++, with executable file "InvestmentBlock_test".
    """

    _log_objective_pattern = r"Fi\* = (.*)\n"

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
        **kwargs,
    ):
        """
        Constructor for the InvestmentBlockTestSolver, with executable file "InvestmentBlock_test".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="InvestmentBlock_test",
            fp_network=fp_network,
            configfile=configfile,
            fp_solution=fp_solution,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        """
        Generate the command-line call for the InvestmentBlock test solver.

        Returns
        -------
        str
            The command string to execute the InvestmentBlock_test solver.
        """
        exec_path = f"InvestmentBlock_test {self.fp_network} -c {self.configdir} -S {self.configfile} -v -o"
        if self.fp_solution is not None:
            exec_path += f" -O {self.fp_solution}"
        return exec_path


class InvestmentBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the InvestmentBlockSolver tool from SMS++, with name "investment_solver".
    """

    _log_objective_pattern = "Solution value: (.*)\n"

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
        **kwargs,
    ):
        """
        Constructor for the InvestmentBlockSolver, with executable file "investment_solver".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="investment_solver",
            fp_network=fp_network,
            configfile=configfile,
            fp_solution=fp_solution,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        """
        Generate the command-line call for the Investment solver.

        Returns
        -------
        str
            The command string to execute the investment_solver.
        """
        exec_path = f"investment_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        if self.fp_solution is not None:
            exec_path += f" -o -O {self.fp_solution}"
        return exec_path


class SDDPSolver(SMSPPSolverTool):
    """
    Class to interact with the SDDPSolver tool from SMS++, with name "sddp_solver".
    """

    _log_objective_pattern = "Solution value: (.*)\n"

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
        **kwargs,
    ):
        """
        Constructor for the SDDPSolver, with executable file "sddp_solver".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="sddp_solver",
            fp_network=fp_network,
            configfile=configfile,
            fp_solution=fp_solution,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        """
        Generate the command-line call for the SDDP solver.

        Returns
        -------
        str
            The command string to execute the sddp_solver.
        """
        exec_path = (
            f"sddp_solver {self.fp_network} -c {self.configdir} -S {self.configfile}"
        )
        if self.fp_solution is not None:
            exec_path += f" -o -O {self.fp_solution}"
        return exec_path


class TSSBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the TSSBlockSolver tool from SMS++, with name "tssb_solver".
    """

    _log_status_pattern = "Status = (.*)\n"
    _log_upper_bound_pattern = "Upper bound = (.*)\n"
    _log_lower_bound_pattern = "Lower bound = (.*)\n"

    def __init__(
        self,
        fp_network: Path | str = "",
        configfile: Path | str = "",
        fp_solution: Path | str = None,
        fp_log: Path | str = None,
        **kwargs,
    ):
        """
        Constructor for the TSSBlockSolver, with executable file "tssb_solver".

        Parameters
        ----------
        fp_network : Path | str
            Path to the SMSpp network to solve.
        configfile : Path | str
            Path to the configuration file.
        fp_solution : Path | str, optional
            Path to the solution file, by default None.
        fp_log : Path | str, optional
            Path to the log file, by default None.
        """
        super().__init__(
            exec_file="tssb_solver",
            fp_network=fp_network,
            configfile=configfile,
            fp_solution=fp_solution,
            fp_log=fp_log,
        )

    def calculate_executable_call(self):
        """
        Generate the command-line call for the TSSB solver.

        Returns
        -------
        str
            The command string to execute the tssb_solver.
        """
        fp_dir, fp_name = os.path.split(self.fp_network)
        exec_path = f"tssb_solver {fp_name} -p {fp_dir}/ -c {self.configdir} -S {self.configfile}"
        if self.fp_solution is not None:
            exec_path += f" -o -O {self.fp_solution}"
        return exec_path


def is_smspp_installed(solvers: list[type[SMSPPSolverTool]] = [UCBlockSolver]) -> bool:
    """
    Check if SMS++ is installed by verifying that the specified solver executables
    can be found in the PATH.

    Parameters
    ----------
    solvers : list[type[SMSPPSolverTool]], optional
        List of solver classes to check. Defaults to [UCBlockSolver].
        Available solvers: UCBlockSolver, InvestmentBlockTestSolver,
        InvestmentBlockSolver, SDDPSolver.

    Returns
    -------
    bool
        True if all specified SMS++ solvers are installed, False otherwise.

    Examples
    --------
    >>> import pysmspp
    >>> if pysmspp.is_smspp_installed():
    ...     print("SMS++ is installed and available")
    ... else:
    ...     print("SMS++ is not available")

    >>> # Check multiple solvers
    >>> if pysmspp.is_smspp_installed([pysmspp.UCBlockSolver, pysmspp.InvestmentBlockTestSolver]):
    ...     print("Both solvers are available")
    """
    # Check if all specified solvers are available
    return all(solver().is_available() for solver in solvers)
