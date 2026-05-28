"""Client library for interacting with In-situ Marine Optics DALEC."""

import logging

from pydalec.__version__ import __version__  # noqa: F401
from pydalec.instrument import Dalec  # noqa: F401
from pydalec.logging_utils import enable_debug_logging  # noqa: F401

# Set up logging default to work for use as a library:
# * do not configure root logging on import
# * avoid "No handlers could be found for logger 'pydalec'" warnings.
logging.getLogger('pydalec').addHandler(logging.NullHandler())
