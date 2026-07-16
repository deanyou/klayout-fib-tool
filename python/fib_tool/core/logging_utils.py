"""Logging helpers that do not depend on KLayout's Macro Development console."""

import builtins
import os
import traceback


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


def _message(level, component, message):
    return "[%s] [%s] %s" % (level, component, message)


def info(component, message):
    """Record an informational diagnostic message."""
    return safe_print(_message("INFO", component, message))


def warning(component, message):
    """Record a recoverable problem."""
    return safe_print(_message("WARNING", component, message))


def error(component, message):
    """Record an operation failure without a traceback."""
    return safe_print(_message("ERROR", component, message))


def exception(component, message):
    """Record an operation failure with the active exception traceback."""
    details = traceback.format_exc()
    return safe_print(_message("ERROR", component, message) + "\n" + details)
