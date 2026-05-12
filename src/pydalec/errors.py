class PyDalecError(Exception):
    """Base class for all DALEC client exceptions."""


class PyDalecConnectionError(PyDalecError):
    """Raised when a connection to the DALEC cannot be established."""


class PyDalecNoPositionDataError(PyDalecError):
    """Raised when no valid GNSS position is received before timeout."""
