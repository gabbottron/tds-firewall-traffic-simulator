"""FSTO/1 UDP receiver harness - minimal experimental receiver."""

import socket
import time
from typing import Optional, Tuple


class ReceiverHarness:
    """Minimal UDP receiver for FSTO/1 experiment.

    This is an experimental harness, NOT a production collector.
    Receives UDP datagrams, preserves application bytes opaquely,
    records receipt metadata.
    """

    def __init__(self, listen_host: str = '127.0.0.1', listen_port: int = 5140):
        """Initialize receiver harness.

        Args:
            listen_host: Local address to bind
            listen_port: Local UDP port to bind
        """
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.sock: Optional[socket.socket] = None
        self.running = False

    def start(self) -> None:
        """Start the receiver and bind to the local address."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.listen_host, self.listen_port))
        self.running = True

    def stop(self) -> None:
        """Stop the receiver and close the socket."""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None

    def receive_one(
        self,
        timeout: float = 2.0,
        buffer_size: int = 65535
    ) -> Optional[Tuple[bytes, str, int, float, int, int]]:
        """Receive exactly one UDP datagram.

        Args:
            timeout: How long to wait for a datagram (seconds)
            buffer_size: Maximum datagram size to receive

        Returns:
            None if timeout, otherwise tuple of:
            - payload_bytes: Complete received application bytes (opaque, not parsed)
            - peer_host: Source IP address as seen by receiver
            - peer_port: Source port as seen by receiver
            - receipt_time: When datagram arrived (epoch seconds, receiver metadata)
            - payload_length: Number of application bytes received
            - listener_port: Local port that received the datagram

        Note:
            receipt_time is receiver metadata, distinct from eventtime in payload.
            Payload is preserved opaquely; no parsing, no field extraction.
        """
        if not self.sock or not self.running:
            raise RuntimeError("Receiver not started")

        self.sock.settimeout(timeout)
        try:
            data, addr = self.sock.recvfrom(buffer_size)
            receipt_time = time.time()
            peer_host, peer_port = addr

            return (
                data,
                peer_host,
                peer_port,
                receipt_time,
                len(data),
                self.listen_port
            )
        except socket.timeout:
            return None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
