"""Integration tests for UDP send/receive."""

import time
import pytest
from fsto1.generator import generate_canonical
from fsto1.simulator import send_fsto1_record
from fsto1.receiver import ReceiverHarness


def test_clean_success_local():
    """Test clean_success: one send results in one receipt with byte preservation."""
    canonical = generate_canonical()

    # Start receiver
    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=15140)
    receiver.start()

    try:
        # Send one record
        bytes_sent, attempt_time, sent_bytes = send_fsto1_record(
            '127.0.0.1', 15140, timeout=1.0
        )

        # Verify send
        assert bytes_sent == 180
        assert sent_bytes == canonical
        assert attempt_time > 0  # Attempt time is metadata, not in payload

        # Receive one datagram
        result = receiver.receive_one(timeout=2.0)

        assert result is not None, "No receipt observed"

        (payload, peer_host, peer_port, receipt_time,
         payload_length, listener_port) = result

        # Verify receipt metadata
        assert peer_host == '127.0.0.1'
        assert isinstance(peer_port, int)
        assert receipt_time > attempt_time  # Receipt after attempt
        assert payload_length == 180
        assert listener_port == 15140

        # Verify byte preservation - golden-byte equality
        assert payload == canonical
        assert len(payload) == 180

        # Verify three-way time distinction
        # 1. eventtime in payload: 1672531200000000000 (not extracted, opaque)
        # 2. attempt_time: simulator metadata
        # 3. receipt_time: receiver metadata
        assert attempt_time != 1672531200  # Attempt time is current, not eventtime
        assert receipt_time != 1672531200  # Receipt time is current, not eventtime

    finally:
        receiver.stop()


def test_receiver_unavailable():
    """Test receiver_unavailable: send succeeds but no receipt observed."""
    canonical = generate_canonical()

    # Ensure no receiver is listening on this port
    # (just pick an unlikely port and don't start a receiver)
    dest_port = 25140

    # Send one record to unreachable destination
    bytes_sent, attempt_time, sent_bytes = send_fsto1_record(
        '127.0.0.1', dest_port, timeout=0.5
    )

    # Verify local send succeeded
    assert bytes_sent == 180
    assert sent_bytes == canonical
    assert attempt_time > 0

    # Verify no receiver observed the receipt
    # (We can't prove global absence, but we can verify the bounded
    # experiment condition: no receiver was listening)

    # Try to receive on a fresh receiver - should timeout
    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=35140)
    receiver.start()

    try:
        # Wait for potential receipt
        result = receiver.receive_one(timeout=1.0)

        # Should timeout - no datagram should arrive at this receiver
        assert result is None, "Unexpected receipt observed"

    finally:
        receiver.stop()

    # This demonstrates: successful local UDP write does NOT guarantee
    # receiver receipt. It does NOT prove where a production message was lost
    # or establish real-network behavior.


def test_opaque_preservation():
    """Verify receiver treats payload as opaque bytes."""
    canonical = generate_canonical()

    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=45140)
    receiver.start()

    try:
        send_fsto1_record('127.0.0.1', 45140)

        result = receiver.receive_one(timeout=2.0)
        assert result is not None

        payload, _, _, _, _, _ = result

        # Receiver must preserve exact bytes
        assert payload == canonical

        # Should be able to decode, but receiver doesn't parse
        decoded = payload.decode('utf-8')
        assert 'eventtime=1672531200000000000' in decoded  # As string, not parsed

    finally:
        receiver.stop()


def test_one_send_one_datagram():
    """Verify one application message becomes one UDP send operation."""
    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=55140)
    receiver.start()

    try:
        # Send exactly once
        send_fsto1_record('127.0.0.1', 55140)

        # Should receive exactly one datagram
        result1 = receiver.receive_one(timeout=1.0)
        assert result1 is not None

        # Should NOT receive a second datagram
        result2 = receiver.receive_one(timeout=0.5)
        assert result2 is None

    finally:
        receiver.stop()
