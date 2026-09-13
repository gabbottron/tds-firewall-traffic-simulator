# FSTO/1 Contract Specification

## Identity and Version

**Name:** FortiOS-Shaped Traffic Observation v1
**Shorthand:** FSTO/1
**Version:** 1
**Date:** 2026-09-10

## Purpose and Scope

Define exact, reproducible, synthetic firewall traffic-observation bytes for
teaching the first raw-collection boundary. This contract specifies
application-layer message content only; it does not specify IP packets, UDP
datagrams, network addresses, or socket behavior.

Scope: A minimal source-shaped text record representing one completed TCP session
(proto=6, dstport=443) observed and allowed by a firewall, exported for external
collection. Based on documented FortiOS 7.4.8 Traffic/forward session-end field
names and key-value syntax.

**This is NOT captured, observed, or vendor-verified FortiOS output.** This is a
synthetic teaching contract. The teaching record crosses the first edge in a UDP
datagram, distinct from the TCP traffic it describes.

## Canonical Record

**Exact 180-byte sequence:**

```
devid=FW-TEACHING-01 eventtime=1672531200000000000 logid=0000000013 type=traffic subtype=forward action=close proto=6 srcip=192.0.2.10 dstip=198.51.100.20 dstport=443 sentbyte=4096
```

**Hexadecimal representation:**

```
00000000: 64 65 76 69 64 3d 46 57  2d 54 45 41 43 48 49 4e  |devid=FW-TEACHIN|
00000010: 47 2d 30 31 20 65 76 65  6e 74 74 69 6d 65 3d 31  |G-01 eventtime=1|
00000020: 36 37 32 35 33 31 32 30  30 30 30 30 30 30 30 30  |6725312000000000|
00000030: 30 30 20 6c 6f 67 69 64  3d 30 30 30 30 30 30 30  |00 logid=0000000|
00000040: 30 31 33 20 74 79 70 65  3d 74 72 61 66 66 69 63  |013 type=traffic|
00000050: 20 73 75 62 74 79 70 65  3d 66 6f 72 77 61 72 64  | subtype=forward|
00000060: 20 61 63 74 69 6f 6e 3d  63 6c 6f 73 65 20 70 72  | action=close pr|
00000070: 6f 74 6f 3d 36 20 73 72  63 69 70 3d 31 39 32 2e  |oto=6 srcip=192.|
00000080: 30 2e 32 2e 31 30 20 64  73 74 69 70 3d 31 39 38  |0.2.10 dstip=198|
00000090: 2e 35 31 2e 31 30 30 2e  32 30 20 64 73 74 70 6f  |.51.100.20 dstpo|
000000a0: 72 74 3d 34 34 33 20 73  65 6e 74 62 79 74 65 3d  |rt=443 sentbyte=|
000000b0: 34 30 39 36                                       |4096            |
```

**Byte length:** 180 bytes
**Encoding:** UTF-8
**SHA-256:** 62bf0871bd1148b2c1f1afbe3a500740d5a936af5d1dec3b724ab1c85486a653

## Structure

- **Field delimiter:** Single space character (U+0020)
- **Key-value format:** `key=value` with no surrounding whitespace
- **Field order:** Fixed teaching order (see below); the eleven field names and
  applicable values are source-shaped from FortiOS documentation; their exact
  sequence is FSTO/1's deterministic teaching-contract order, not a claim about
  FortiOS field ordering
- **Quoting:** None; values contain no spaces, equals, or special characters
- **All fields present:** Every field appears in every canonical record
- **No envelope:** Bare key-value body only; no syslog priority, timestamp, hostname, facility
- **No length prefix:** None
- **No terminator:** Message ends after last field value; no newline, NUL, or other terminator
- **One record per UDP send:** Teaching simplification

## Field-by-Field Provenance

| Position | Field | Value | Provenance |
|----------|-------|-------|------------|
| 1 | devid | FW-TEACHING-01 | Teaching simplification (fictional device ID) |
| 2 | eventtime | 1672531200000000000 | Vendor-documented with qualification (epoch nanoseconds per Traffic log ID 13; generic field page conflict noted) |
| 3 | logid | 0000000013 | Vendor-documented (log ID 13 = Traffic/forward session-end) |
| 4 | type | traffic | Vendor-documented |
| 5 | subtype | forward | Vendor-documented (forwarded-traffic subtype) |
| 6 | action | close | Vendor-documented allowed-session end status under Traffic/forward; no TCP shutdown sequence is inferred |
| 7 | proto | 6 | Vendor-documented field; standards-derived value (IANA protocol 6=TCP) |
| 8 | srcip | 192.0.2.10 | Standards-derived synthetic (RFC 5737 TEST-NET-1) |
| 9 | dstip | 198.51.100.20 | Standards-derived synthetic (RFC 5737 TEST-NET-2) |
| 10 | dstport | 443 | Teaching simplification (HTTPS port) |
| 11 | sentbyte | 4096 | Teaching simplification (small readable value) |

## Vendor Documentation Limitations

**Source:** FortiOS 7.4.8 documentation (V1-V3, V11, V13 from platform root research)

**eventtime documentation conflict:** Generic Fortinet field page shows 10-digit
second-based epoch example. Specific Traffic log ID 13 definition and FortiOS
7.4.8 sample logs establish 19-digit nanosecond representation. This contract
uses nanoseconds per the most specific source.

**Unresolved vendor behavior:**

- Complete default-format envelope bytes
- Record packing (one vs. multiple per datagram)
- Exact field order
- Quoting/escaping rules
- Character encoding (UTF-8 assumed, not explicitly documented)
- Build-specific variations

**action semantics:** subtype=forward identifies Fortinet's forwarded-traffic
subtype. Under applicable Traffic/forward session-end semantics, action=close is
an allowed-session end status. This teaching contract does not infer a particular
TCP shutdown sequence from it; it is not policy decision alone.

## Teaching Simplifications

- **One record per UDP datagram:** Excludes FortiOS batching, packing, queueing
- **Bare key-value body:** Excludes syslog envelope (unresolved by vendor docs)
- **No terminator:** Datagram boundary is message boundary
- **Fixed field order:** Deterministic generation; not claimed as FortiOS ordering
- **No quoting:** Values contain no special characters
- **UTF-8 encoding:** Not explicitly documented; responsibly reconstructed
- **All fields present:** Excludes optional field behavior
- **Printable ASCII only:** Excludes international characters, control codes
- **Fixed numeric eventtime:** Excludes formatted timestamps, sub-nanosecond precision
- **Eleven fields only:** Minimum for teaching TCP session observation and time distinction

## Conformance Rules

An implementation conforms to FSTO/1 if:

1. Generated bytes exactly match the 180-byte canonical sequence
2. Generation is deterministic (same inputs → same bytes)
3. One application message per UDP write operation
4. All bytes decode as valid UTF-8
5. Eleven fields in documented order, space-delimited, key=value format
6. No byte-order marker, length prefix, syslog header, or trailing newline/NUL
7. Attempt accounting is separate from payload (attempt time ≠ eventtime)
8. Contract version is visible in execution evidence, not embedded in payload

## Versioning Rules

- **Compatible variation:** Different TEST-NET addresses, different sentbyte counts, different fictional devid (preserving structure)
- **New fixture:** Adding fields, changing field order, adding envelope/terminator → version increment
- **New contract version:** Changes to field structure, encoding, delimiter rules → FSTO/2
- **Vendor-profile revision:** Evidence that FortiOS 7.4.8 differs or decision to use different FortiOS version → new contract

## Three-Way Time Distinction

- **Source observation time (eventtime=1672531200000000000 in payload):** When the firewall observed the TCP session end (nanoseconds since Unix epoch)
- **Simulator attempt time (metadata, outside payload):** When simulator submitted teaching record to UDP socket
- **Receiver receipt time (metadata, outside payload):** When experimental receiver observed datagram arrival

These three times answer different questions and must not be conflated.

## Explicit Non-Claims

This contract does NOT claim:

- These bytes were emitted by FortiOS
- FortiOS packing/batching matches one-per-datagram rule
- Field order matches FortiOS output
- Envelope treatment matches FortiOS default format
- Encoding is verified as FortiOS behavior
- These bytes are suitable for production use
- This is a universal platform event schema
