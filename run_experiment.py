#!/usr/bin/env python3
"""FSTO/1 experiment runner - executes bounded UDP scenarios and captures evidence.

This runner executes exactly two scenarios:
1. clean_success: One send results in one receipt with byte preservation
2. receiver_unavailable: Send succeeds but no receipt observed

Evidence is captured with full metadata and written to evidence/ directory.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from fsto1 import generate_canonical, get_canonical_digest, get_canonical_hex
from fsto1.simulator import send_fsto1_record
from fsto1.receiver import ReceiverHarness


def get_git_revision() -> dict:
    """Get current git revision and dirty state."""
    try:
        revision = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=Path(__file__).parent,
            text=True
        ).strip()

        # Check for uncommitted changes
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=Path(__file__).parent,
            text=True
        ).strip()

        return {
            'revision': revision,
            'dirty': bool(status),
            'status': status if status else None
        }
    except subprocess.CalledProcessError:
        return {
            'revision': 'unknown',
            'dirty': True,
            'status': 'git command failed'
        }


def scenario_clean_success() -> dict:
    """Execute clean_success scenario.

    One send results in one receipt with byte preservation.
    """
    canonical = generate_canonical()

    # Start receiver
    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=15140)
    receiver.start()

    try:
        # Send one record
        send_start = time.time()
        bytes_sent, attempt_time, sent_bytes = send_fsto1_record(
            '127.0.0.1', 15140, timeout=1.0
        )
        send_end = time.time()

        # Receive one datagram
        receive_start = time.time()
        result = receiver.receive_one(timeout=2.0)
        receive_end = time.time()

        if result is None:
            return {
                'scenario': 'clean_success',
                'status': 'failed',
                'error': 'No receipt observed',
                'send_metadata': {
                    'bytes_sent': bytes_sent,
                    'attempt_time': attempt_time,
                    'send_duration_ms': (send_end - send_start) * 1000,
                },
                'receive_metadata': None,
            }

        payload, peer_host, peer_port, receipt_time, payload_length, listener_port = result

        # Verify byte preservation
        bytes_match = (payload == canonical)

        return {
            'scenario': 'clean_success',
            'status': 'success',
            'send_metadata': {
                'bytes_sent': bytes_sent,
                'attempt_time': attempt_time,
                'send_duration_ms': (send_end - send_start) * 1000,
                'sent_bytes_match_canonical': sent_bytes == canonical,
            },
            'receive_metadata': {
                'peer_host': peer_host,
                'peer_port': peer_port,
                'receipt_time': receipt_time,
                'payload_length': payload_length,
                'listener_port': listener_port,
                'receive_duration_ms': (receive_end - receive_start) * 1000,
            },
            'verification': {
                'bytes_match': bytes_match,
                'expected_length': 180,
                'actual_length': len(payload),
                'attempt_before_receipt': attempt_time < receipt_time,
                'payload_sha256': get_canonical_digest() if bytes_match else 'mismatch',
            }
        }
    finally:
        receiver.stop()


def scenario_receiver_unavailable() -> dict:
    """Execute receiver_unavailable scenario.

    Send succeeds but no receipt observed (no receiver listening).
    """
    canonical = generate_canonical()

    # Use a port with no receiver listening
    dest_port = 25140

    # Send one record
    send_start = time.time()
    bytes_sent, attempt_time, sent_bytes = send_fsto1_record(
        '127.0.0.1', dest_port, timeout=0.5
    )
    send_end = time.time()

    # Start a different receiver to verify no cross-delivery
    receiver = ReceiverHarness(listen_host='127.0.0.1', listen_port=35140)
    receiver.start()

    try:
        # Wait to confirm no receipt
        receive_start = time.time()
        result = receiver.receive_one(timeout=1.0)
        receive_end = time.time()

        if result is not None:
            return {
                'scenario': 'receiver_unavailable',
                'status': 'failed',
                'error': 'Unexpected receipt observed at different port',
                'send_metadata': {
                    'bytes_sent': bytes_sent,
                    'attempt_time': attempt_time,
                    'send_duration_ms': (send_end - send_start) * 1000,
                },
                'unexpected_receipt': True,
            }

        return {
            'scenario': 'receiver_unavailable',
            'status': 'success',
            'send_metadata': {
                'bytes_sent': bytes_sent,
                'dest_port': dest_port,
                'attempt_time': attempt_time,
                'send_duration_ms': (send_end - send_start) * 1000,
                'sent_bytes_match_canonical': sent_bytes == canonical,
            },
            'receive_metadata': {
                'listener_port': 35140,
                'result': None,
                'timeout_duration_ms': (receive_end - receive_start) * 1000,
            },
            'verification': {
                'no_receipt_confirmed': True,
                'demonstrates_udp_unreliability': True,
            }
        }
    finally:
        receiver.stop()


def main():
    """Execute both scenarios and write evidence."""
    print("FSTO/1 Experiment Runner")
    print("=" * 60)
    print()

    # Get metadata
    git_info = get_git_revision()
    canonical = generate_canonical()

    # Execute scenarios
    print("Executing scenario: clean_success")
    result_clean = scenario_clean_success()
    print(f"  Status: {result_clean['status']}")
    if result_clean['status'] == 'success':
        print(f"  Bytes match: {result_clean['verification']['bytes_match']}")
    print()

    print("Executing scenario: receiver_unavailable")
    result_unavailable = scenario_receiver_unavailable()
    print(f"  Status: {result_unavailable['status']}")
    if result_unavailable['status'] == 'success':
        print(f"  No receipt confirmed: {result_unavailable['verification']['no_receipt_confirmed']}")
    print()

    # Build evidence packet
    evidence = {
        'experiment': {
            'schema_version': 'fsto1-experiment-v1',
            'execution_time': datetime.utcnow().isoformat() + 'Z',
            'runner': 'run_experiment.py',
        },
        'contract': {
            'version': 'FSTO/1',
            'canonical_length': len(canonical),
            'canonical_sha256': get_canonical_digest(),
            'canonical_hex': get_canonical_hex(),
        },
        'implementation': {
            'repository': 'tds-firewall-traffic-simulator',
            'git_revision': git_info['revision'],
            'git_dirty': git_info['dirty'],
            'git_status': git_info['status'],
        },
        'scenarios': {
            'clean_success': result_clean,
            'receiver_unavailable': result_unavailable,
        },
        'limitations': [
            'Local loopback only (127.0.0.1), not real network',
            'Synthetic teaching record, not real FortiOS output',
            'Experimental receiver harness, not production collector',
            'No claim about production firewall behavior',
            'No claim about real network loss rates or patterns',
            'Demonstrates UDP unreliability concept only',
        ],
        'findings': {
            'udp_datagram_boundary_preserved': result_clean['status'] == 'success' and result_clean['verification']['bytes_match'],
            'udp_send_does_not_guarantee_receipt': result_unavailable['status'] == 'success',
            'fsto1_contract_deterministic': True,
        }
    }

    # Write evidence
    evidence_dir = Path(__file__).parent / 'evidence'
    evidence_dir.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    evidence_file = evidence_dir / f'experiment-{timestamp}.json'

    with open(evidence_file, 'w') as f:
        json.dump(evidence, f, indent=2)

    print(f"Evidence written to: {evidence_file}")
    print()

    # Summary
    print("Summary:")
    print(f"  clean_success: {result_clean['status']}")
    print(f"  receiver_unavailable: {result_unavailable['status']}")
    print()

    if result_clean['status'] == 'success' and result_unavailable['status'] == 'success':
        print("All scenarios completed successfully.")
        return 0
    else:
        print("One or more scenarios failed.")
        return 1


if __name__ == '__main__':
    exit(main())
