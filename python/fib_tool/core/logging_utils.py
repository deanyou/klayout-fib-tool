"""Logging helpers that do not depend on KLayout's Macro Development console."""

import builtins
import os


def safe_print(*args, **kwargs):
    """Print when possible without allowing console failures to break tool actions.

    KLayout may not provide a usable Python stdout stream until the Macro
    Development window is opened.  If printing fails, preserve the message in
    ``~/.klayout/fib_tool.log`` and never propagate the logging error.
    """
    try:
        builtins.print(*args, **kwargs)
        return True
    except Exception:
        pass

    try:
        log_path = os.path.join(os.path.expanduser("~"), ".klayout", "fib_tool.log")
        separator = kwargs.get("sep", " ")
        ending = kwargs.get("end", "\n")
        message = separator.join(str(arg) for arg in args) + ending
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(message)
    except Exception:
        pass

    return False
