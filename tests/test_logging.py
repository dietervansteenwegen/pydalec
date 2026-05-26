"""Unit tests for pydalec logging helpers and behavior."""

import logging

from pydalec.logging_utils import _DEBUG_HANDLER_NAME, enable_debug_logging


def _remove_debug_handlers(logger: logging.Logger) -> None:
    tagged_handlers = [
        handler for handler in logger.handlers if handler.get_name() == _DEBUG_HANDLER_NAME
    ]
    for handler in tagged_handlers:
        logger.removeHandler(handler)


def test_enable_debug_logging_does_not_touch_root_logger():
    root_logger = logging.getLogger()
    before_handlers = list(root_logger.handlers)
    before_level = root_logger.level

    package_logger = logging.getLogger('pydalec')
    _remove_debug_handlers(package_logger)

    try:
        enable_debug_logging()

        tagged_handlers = [
            handler
            for handler in package_logger.handlers
            if handler.get_name() == _DEBUG_HANDLER_NAME
        ]
        assert len(tagged_handlers) == 1
        assert root_logger.handlers == before_handlers
        assert root_logger.level == before_level
    finally:
        _remove_debug_handlers(package_logger)


def test_enable_debug_logging_is_idempotent():
    package_logger = logging.getLogger('pydalec')
    _remove_debug_handlers(package_logger)

    try:
        enable_debug_logging()
        enable_debug_logging()

        tagged_handlers = [
            handler
            for handler in package_logger.handlers
            if handler.get_name() == _DEBUG_HANDLER_NAME
        ]
        assert len(tagged_handlers) == 1
    finally:
        _remove_debug_handlers(package_logger)
