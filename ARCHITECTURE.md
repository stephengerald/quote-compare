# Architecture

## State machine

A customer freezes requirements, at least two bidders submit quotes, consensus assesses coverage and risk, and the customer alone shortlists and selects.

The relevant roles are customer and at least two bidders. Write methods enforce role, phase, uniqueness, and bounded-storage rules before any state transition.

## Consensus boundary

Validators produce a requirement-coverage bitmask and LOW, MEDIUM, or HIGH delivery risk from each stored quote. The leader returns a small JSON schema; validators independently rerun the same decision function and accept only exact enum or bitmask values. Malformed model output raises a tagged model error and writes no decision.

## Deterministic boundary

Enrollment, authorization, commitments, counters, phase changes, caps, masks, and any score or credit arithmetic are deterministic contract logic. Only semantic interpretation of the stored evidence occurs inside `run_nondet_unsafe`.

## Off-chain boundary

Wallet custody, identity verification, indexing, notifications, private file storage, source authentication, money movement, legal process, and user-interface behavior are outside this repository. Coverage is not legal advice, vendor due diligence, or a binding procurement decision. Identity, licensing, references, and contract execution stay off-chain.
