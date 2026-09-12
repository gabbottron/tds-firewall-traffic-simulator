"""FSTO/1 canonical record generator.

Generates the exact 180-byte FSTO/1 teaching contract record deterministically.
"""

# FSTO/1 canonical field values
CANONICAL_FIELDS = {
    'devid': 'FW-TEACHING-01',
    'eventtime': '1672531200000000000',
    'logid': '0000000013',
    'type': 'traffic',
    'subtype': 'forward',
    'action': 'close',
    'proto': '6',
    'srcip': '192.0.2.10',
    'dstip': '198.51.100.20',
    'dstport': '443',
    'sentbyte': '4096',
}

# Fixed teaching order (not a claim about FortiOS ordering)
FIELD_ORDER = [
    'devid', 'eventtime', 'logid', 'type', 'subtype', 'action',
    'proto', 'srcip', 'dstip', 'dstport', 'sentbyte'
]


def generate_canonical() -> bytes:
    """Generate the exact FSTO/1 canonical record.

    Returns:
        Exactly 180 bytes of UTF-8 encoded key-value pairs, space-delimited,
        no envelope, no prefix, no terminator.
    """
    pairs = [f"{field}={CANONICAL_FIELDS[field]}" for field in FIELD_ORDER]
    record_str = ' '.join(pairs)
    record_bytes = record_str.encode('utf-8')

    # Enforce contract: exactly 180 bytes
    if len(record_bytes) != 180:
        raise ValueError(
            f"Generated record is {len(record_bytes)} bytes, expected 180"
        )

    return record_bytes


def get_canonical_hex() -> str:
    """Get hexadecimal representation of canonical record."""
    record = generate_canonical()
    return record.hex()


def get_canonical_digest() -> str:
    """Get SHA-256 digest of canonical record."""
    import hashlib
    record = generate_canonical()
    return hashlib.sha256(record).hexdigest()
