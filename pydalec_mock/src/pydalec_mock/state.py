"""State model used by the pydalec mock instrument server."""


class InstrumentState:
    """Container for mutable mock instrument values."""

    def __init__(self):
        """Initialize the default instrument state values."""
        self.temperature = 25.0
