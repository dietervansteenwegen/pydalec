"""Unit tests for `pydalec.transport.base`."""

import pytest

from pydalec.transport.base import BaseTransport


def test_base_transport_methods_are_abstract():
    """Verify abstract markers are present on BaseTransport methods."""
    assert BaseTransport.__dict__['send'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['receive'].__isabstractmethod__ is True


def test_base_transport_cannot_be_instantiated_without_methods():
    """Verify subclasses missing abstract methods cannot be instantiated."""

    class IncompleteTransport(BaseTransport):
        pass

    with pytest.raises(expected_exception=TypeError):
        IncompleteTransport()
