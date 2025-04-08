from subprocess import CompletedProcess
import os


def decode_std(data) -> str:
    """
    Decode bytes to a string.

    Parameters
    -----------
    - data : bytes
        The bytes to decode.

    Returns
    -----------
        str: The decoded string.
    """
    return data.decode("utf-8") if data else ""


def subprocess_result_to_log(result: CompletedProcess) -> str:
    """
    Convert the result of a subprocess to a log string.

    Parameters
    -----------
    - result : CompletedProcess)
        The result of the subprocess.

    Returns
    -----------
        str: The log string.
    """
    stdout_str = decode_std(result.stdout)
    stderr_str = decode_std(result.stderr)
    out_str = stdout_str
    if len(stderr_str) > 0:
        out_str += os.linesep + os.linesep + "STD ERR" + os.linesep + stderr_str
    return out_str
