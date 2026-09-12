"""FSTO/1 UDP simulator - sends teaching records."""

import socket
import time
from typing import Tuple

from .generator import generate_canonical


def send_fsto1_record(
    dest_host: str,
    dest_port: int,
    timeout: float = 1.0
) -> Tuple[int, float, bytes]:
    """Send one FSTO/1 canonical record via UDP.

    Args:
        dest_host: Destination hostname or IP
        dest_port: Destination UDP port
        timeout: Socket timeout in seconds

    Returns:
        Tuple of (bytes_sent, attempt_timestamp, record_bytes)
        - bytes_sent: Number of bytes sent by sendto() call
        - attempt_timestamp: Time when send was attempted (epoch seconds)
        - record_bytes: The exact bytes that were sent

    Note:
        attempt_timestamp is simulator metadata, distinct from eventtime
        (1672531200000000000 nanoseconds) in the payload.
    """
    record = generate_canonical()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(timeout)
        attempt_time = time.time()
        bytes_sent = sock.sendto(record, (dest_host, dest_port))
        return (bytes_sent, attempt_time, record)
    finally:
        sock.close()
