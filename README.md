# Quote Compare

Compares contractor quotes against numbered requirements while keeping price outside the validator judgment.

## Why GenLayer

Validators produce a requirement-coverage bitmask and LOW, MEDIUM, or HIGH delivery risk from each stored quote.

## Reusable workflow

A customer freezes requirements, at least two bidders submit quotes, consensus assesses coverage and risk, and the customer alone shortlists and selects. Constructor parameters create a new independent instance, so the code is reusable; state is not shared between deployments.

The contract is deliberately non-custodial. It records a decision, entitlement, score, or approval signal and never transfers GEN.

## Evidence boundary

Validators judge only on-chain requirements and quote text. No contractor history, licensing database, market price, or external source is collected.

## Verify locally

```powershell
genvm-lint check contracts/quote_compare.py
genvm-lint typecheck contracts/quote_compare.py
pytest tests/direct -q
python tests/run_glsim.py --validators 5
```

With GLSim running in another terminal:

```powershell
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The live smoke test requires fresh test-only keys in `GENLAYER_PRIVATE_KEY`, `GENLAYER_SECONDARY_PRIVATE_KEY`, `GENLAYER_TERTIARY_PRIVATE_KEY`. Never commit a `.env` file or use a production wallet.

```powershell
gltest tests/integration/test_studionet_smoke.py --network studionet -s -q --default-wait-interval=6000 --default-wait-retries=240
```

The public StudioNet endpoint enforced 30 requests per minute during the first run; the documented 6-second polling interval passed cleanly.

See `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md`, and `deployments/studionet.json` for the review boundary and exact public evidence.
