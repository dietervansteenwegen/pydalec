"""Helpers for configuring pydalec logging in applications and REPL sessions."""

import logging

_DEBUG_HANDLER_NAME = 'pydalec.debug'


def enable_debug_logging(level: int = logging.DEBUG) -> logging.Logger:
    """Enable console logging for the pydalec logger without touching root logger.

    This helper is intentionally opt-in and idempotent.
    """
    logger = logging.getLogger('pydalec')
    logger.setLevel(level)

    handler_exists = any(handler.get_name() == _DEBUG_HANDLER_NAME for handler in logger.handlers)
    if not handler_exists:
        handler = logging.StreamHandler()
        handler.set_name(_DEBUG_HANDLER_NAME)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
        logger.addHandler(handler)

    return logger
