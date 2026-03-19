"""Abstract transport interface used by DALEC clients."""

from abc import ABC, abstractmethod


class BaseTransport(ABC):
    """Abstract interface for synchronous DALEC transports."""

    @abstractmethod
    def send(self, data: str) -> None:
        """Send a command string to the transport backend."""
        pass

    @abstractmethod
    def receive(self) -> str:
        """Receive a response string from the transport backend."""
        pass
