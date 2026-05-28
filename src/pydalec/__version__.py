"""Runtime package version exposed as ``pydalec.__version__``."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version('pydalec')
except PackageNotFoundError:
    # Allows source-tree imports before the package is installed.
    __version__ = '0.0.0+unknown'
