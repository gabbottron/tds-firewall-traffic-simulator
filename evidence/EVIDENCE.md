# FSTO/1 Evidence Artifacts

This directory contains evidence from FSTO/1 experiment runs.

## Current validated evidence

**experiment-20260913-145108.json**
- Execution time: 2026-09-13 14:51:08 UTC
- Implementation revision: a62ac9897e0086ff256f996249ed56154717773c (clean)
- Git dirty: false
- Test results: 15/15 passed
- Scenarios: clean_success (success), receiver_unavailable (success)
- Status: **VALIDATED** - cited by Article 2

This artifact was produced from the clean implementation commit a62ac98 with
no uncommitted changes.

### Interpretation limitation

The validated `receiver_unavailable` artifact records a successful local send to
UDP port 25140 and a timeout on different port 35140. It does not observe port
25140, so it does not establish destination non-receipt or locate loss. Treat a
successful UDP send as attempt evidence, not application-receipt evidence.

## Superseded artifacts

**experiment-20260912-005655-SUPERSEDED.json**
- Execution time: 2026-09-12 00:56:55 UTC
- Implementation revision: 9dfda243d64fff561053cf8d49e11cb1230fc042 (dirty)
- Git dirty: true
- Superseded reason: Evidence was captured from dirty working tree with untracked
  implementation files, not from immutable clean commit
- Superseded by: experiment-20260913-145108.json
- Status: **SUPERSEDED** - not cited by Article 2

This artifact was produced during initial implementation before creating the
implementation commit. The experiment results were materially identical (both
scenarios succeeded, byte preservation verified), but the evidence did not cite
an immutable clean implementation revision. It is preserved for historical
record but is not used to support Article 2 claims.
