"""Unit tests for `pydalec.transport.base`."""

import pytest

from pydalec.transport.base import BaseTransport


def test_base_transport_methods_are_abstract():
    """Verify abstract markers are present on BaseTransport methods."""
    assert BaseTransport.__dict__['connect'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['send'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['disconnect'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['start_measurements'].__isabstractmethod__ is True
    assert BaseTransport.__dict__['stop_measurements'].__isabstractmethod__ is True


def test_base_transport_cannot_be_instantiated_without_methods():
    """Verify subclasses missing abstract methods cannot be instantiated."""

    class IncompleteTransport(BaseTransport):
        pass

    with pytest.raises(expected_exception=TypeError):
        IncompleteTransport()


def test_base_transport_abstract_method_bodies_are_executable_via_super():
    """Execute BaseTransport method bodies to cover their `pass` statements."""

    class ConcreteTransport(BaseTransport):
        def connect(self) -> None:
            return super().connect()

        def send(self, data: str) -> None:
            return super().send(data)

        def disconnect(self) -> None:
            return super().disconnect()

        def start_measurements(self) -> None:
            return super().start_measurements()

        def stop_measurements(self) -> None:
            return super().stop_measurements()

    transport = ConcreteTransport()

    assert transport.connect() is None
    assert transport.send('PING') is None
    assert transport.disconnect() is None
    assert transport.start_measurements() is None
    assert transport.stop_measurements() is None
