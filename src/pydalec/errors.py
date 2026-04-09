class PyDalecError(Exception):
    """Base class for all PyDalec exceptions."""


class DalecConnectionError(PyDalecError):
    """Raised when a connection to the DALEC cannot be established."""
