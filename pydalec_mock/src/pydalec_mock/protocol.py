"""Command handling logic for the pydalec mock instrument."""


def handle_command(state, cmd: str) -> str:
    """Translate an incoming command into a mock instrument response."""
    if cmd == 'READ:TEMP?':
        return f'{state.temperature:.2f}'
    return 'ERROR'
