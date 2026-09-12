# tds-firewall-traffic-simulator

## Authority

This repository owns:

- FSTO/1 teaching contract implementation
- Deterministic canonical record generation
- Bounded UDP experiment execution
- Source-attempt and receiver-receipt observations
- Experiment evidence artifacts

## Explicit non-authority

This repository does NOT own:

- Real FortiOS behavior (FSTO/1 is synthetic, source-shaped, not vendor-verified)
- Platform event model
- Production collector implementation
- Durable handoff
- Parser or normalization
- Message broker or storage
- Device identity resolution
- Detection, enrichment, or classification
- Deployment or tenancy architecture

## Purpose

Implement and execute the smallest reproducible experiment demonstrating the
FSTO/1 teaching contract and the attempt-versus-receipt distinction at the first
raw collection boundary.

FSTO/1 (FortiOS-Shaped Traffic Observation v1) is a 180-byte synthetic teaching
contract based on documented FortiOS 7.4.8 Traffic/forward session-end field
names and key-value syntax. It represents one completed TCP session observed and
allowed by a firewall, exported for external collection.

## Implementation choices

**Language:** Python 3.9+

**Rationale:** Standard-library socket operations for UDP send/receive; exact
byte construction with no encoding surprises; deterministic test assertions;
clear inspection by readers; locally available without additional toolchain.

**Structure:** Minimal. Contract specification, generator module, receiver
harness, tests, experiment runner, evidence recorder.

This is an implementation choice for the bounded experiment, not platform
architecture.

## Relationship to tds-platform-root

**Platform root:** `/Users/gabbott/git/gabbottron/tds-platform-root` owns
cross-service boundaries, platform intent, decisions, questions, risks, and
article evidence.

**This repository:** Implements the accepted FSTO/1 contract for Article 2
teaching experiment only. Does not establish platform-wide transport, framing,
or event model.

**Evidence rules:**

- Keep vendor documentation, synthetic teaching contract, implemented behavior,
  experimental observation, inference, and unknown distinct
- Do not claim these bytes were emitted by FortiOS
- Do not claim receiver_unavailable proves production network loss
- Do not claim clean_success proves real-network UDP delivery
- Preserve the distinction between firewall observation timestamp (eventtime in
  payload), simulator attempt time (metadata), and receiver receipt time
  (metadata)

## Validation commands

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run golden-byte verification
python3 -m pytest tests/test_contract.py::test_canonical_golden_bytes -v

# Run clean_success scenario
python3 run_experiment.py clean_success

# Run receiver_unavailable scenario
python3 run_experiment.py receiver_unavailable

# Verify both scenarios and evidence
python3 run_experiment.py all
```

## Prohibited scope

Until separately justified, this repository must NOT introduce:

- Kafka, NATS, RabbitMQ, or other message brokers
- HTTP metrics, Prometheus, StatsD, or monitoring infrastructure
- Databases or persistent storage beyond evidence files
- Parsers, field extractors, or normalized schemas
- Detection, alerting, or enrichment logic
- syslog envelopes, length prefixes, or run-ID payload fields
- Production collector behavior
- Deployment infrastructure (containers, orchestration, cloud resources)
- Mechanisms not explicitly required by FSTO/1 or the experiment claims

## Historical repository relationship

The historical `firewall-simulator` and `firewall-ingestor` repositories are
read-only reference material for UDP send/receive patterns only. They are NOT:

- Series implementation authorities
- Selection justification for FSTO/1
- Article 2 evidence
- Templates to copy wholesale

FSTO/1 contract and experiment must be independently implemented against the
accepted contract specification.

## Evidence artifacts

Execution evidence is recorded in `evidence/` directory with:

- Experiment schema/version
- FSTO/1 contract version
- Implementation Git revision and clean/dirty state
- Scenario name and declared inputs
- Exact commands
- Source-attempt count, successful local-write count, receiver-receipt count
- Attempt/receipt timestamps (metadata, not payload)
- Byte-equality verification
- Explicit limitations and non-claims

## Agent recovery instructions

If taking over this repository:

1. Read this README completely
2. Read `CONTRACT.md` for complete FSTO/1 specification
3. Inspect `fsto1/` module for generator implementation
4. Review `tests/` for golden-byte and conformance tests
5. Check `evidence/` for execution results
6. Verify relationship to platform root before making architectural changes
7. Do not implement production capabilities without platform-root authorization
8. Preserve evidence rules and explicit non-claims
