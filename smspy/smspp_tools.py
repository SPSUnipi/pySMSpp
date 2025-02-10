import shutil
from pathlib import Path
import subprocess
import re

IS_SMSPP_INSTALLED = shutil.which("ucblock_solver") is not None


class SMSPPSolverTool:
    def __init__(self):
        self._status = None
        self._log = None
        self._objective_value = None
        self._lower_bound = None
        self._upper_bound = None
        raise NotImplementedError("This class is not meant to be instantiated")

    def optimize(self):
        raise NotImplementedError("This class is not meant to be instantiated")

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @property
    def status(self):
        return self._status

    @property
    def log(self):
        return self._log


class UCBlockSolver(SMSPPSolverTool):
    """
    Class to interact with the UCBlockSolver tool from SMS++.
    """

    def __init__(
        self,
        fp_network: Path | str,
        configfile: Path | str,
        fp_out: Path | str = None,
        force=True,
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
        force : bool, optional
            Whether to overwrite existing files, by default True.
        """
        self._log = None
        self._status = None
        self._objective_value = None
        self.fp_network = str(Path(fp_network).resolve())
        self.configfile = str(Path(configfile).resolve())
        self.configdir = str(Path(configfile).resolve().parent.resolve())
        self.fp_out = None if fp_out is None else str(Path(fp_out).resolve())
        if not self.configdir.endswith("/"):
            self.configdir += "/"
        self.force = force

    def __repr__(self):
        return f"UCBlockSolverTool\n\tstatus={self.status}\n\tconfigfile={self.configfile}\n\tfp_network={self.fp_network}\n\tfp_out={self.fp_out}\n\tforce={self.force}"

    def optimize(self, **kwargs):
        """
        Run the UCBlockSolver tool.

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
            f"ucblock_solver {self.fp_network} -c {self.configdir} -S {self.configfile}",
            capture_output=True,
            shell=True,
        )
        self._log = result.stdout.decode("utf-8")
        self.parse_ucblock_solver_log()
        # write output to file, if option passed
        if self.fp_out is not None:
            Path(self.fp_out).parent.mkdir(parents=True, exist_ok=True)
            with open(self.fp_out, "w") as f:
                f.write(self._log)

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
        smspp_status = res.group(1).replace("\r", "")
        self._status = smspp_status

        res = re.search("Upper bound = (.*)\n", self._log)
        up = float(res.group(1).replace("\r", ""))

        res = re.search("Lower bound = (.*)\n", self._log)
        lb = float(res.group(1).replace("\r", ""))

        self._objective_value = up
        self._lower_bound = up
        self._upper_bound = lb
