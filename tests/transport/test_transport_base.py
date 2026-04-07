"""Unit tests for `pydalec.transport.base`."""

import pytest

from pydalec.transport.base import BaseTransport


def test_base_transport_methods_are_abstract():
    """Verify abstract markers are present on BaseTransport methods."""
    assert BaseTransport.__dict__['send'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['receive'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['close'].__isabstractmethod__ is True


def test_base_transport_cannot_be_instantiated_without_methods():
    """Verify subclasses missing abstract methods cannot be instantiated."""

    class IncompleteTransport(BaseTransport):
        pass

    with pytest.raises(expected_exception=TypeError):
        IncompleteTransport()


def test_base_transport_abstract_method_bodies_are_executable_via_super():
    """Execute BaseTransport method bodies to cover their `pass` statements."""

    class ConcreteTransport(BaseTransport):
        def send(self, data: str) -> None:
            return super().send(data)

        def receive(self) -> str:
            return super().receive()

        def close(self) -> None:
            return super().close()

    transport = ConcreteTransport()

    assert transport.send('PING') is None
    assert transport.receive() is None
    assert transport.close() is None
