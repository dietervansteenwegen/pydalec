"""Unit tests for `pydalec.transport.tcp`."""

from pydalec.transport.tcp import TCPTransport


class _FakeSocket:
    """Fake socket used to isolate TCPTransport tests from real networking."""

    def __init__(self):
        self.sent: list = []
        self.payload = b'25.55\n'

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, _buffer_size):
        return self.payload


def test_tcp_transport_init_uses_socket_create_connection(monkeypatch):
    """Verify TCPTransport creates a socket with host and port."""
    fake_socket = _FakeSocket()
    recorded = {}

    def fake_create_connection(endpoint):
        recorded['endpoint'] = endpoint
        return fake_socket

    monkeypatch.setattr('pydalec.transport.tcp.socket.create_connection', fake_create_connection)

    transport = TCPTransport('localhost', 9999)

    assert transport.sock is fake_socket
    assert recorded['endpoint'] == ('localhost', 9999)


def test_tcp_transport_send_appends_newline_and_encodes(monkeypatch):
    """Verify send writes newline-terminated UTF-8 bytes."""
    fake_socket = _FakeSocket()
    monkeypatch.setattr(
        'pydalec.transport.tcp.socket.create_connection',
        lambda _endpoint: fake_socket,
    )
    transport = TCPTransport('localhost', 9999)

    transport.send('READ:TEMP?')

    assert fake_socket.sent == [b'READ:TEMP?\n']


def test_tcp_transport_receive_decodes_and_strips(monkeypatch):
    """Verify receive decodes bytes and strips trailing whitespace."""
    fake_socket = _FakeSocket()
    fake_socket.payload = b'  VALUE  \n'
    monkeypatch.setattr(
        'pydalec.transport.tcp.socket.create_connection',
        lambda _endpoint: fake_socket,
    )
    transport = TCPTransport('localhost', 9999)

    assert transport.receive() == 'VALUE'
