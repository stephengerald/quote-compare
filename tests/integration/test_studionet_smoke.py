import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt)
    return receipt


@pytest.mark.integration
def test_studionet_quote_coverage(default_account, secondary_account, tertiary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "quote_compare.py")
    args = ["Repaint a community-room interior, including preparation, two coats, protection, cleanup, and schedule.", "A requirement is covered only when expressly committed. Risk is high for material exclusions, medium for ambiguity, and low otherwise. Do not judge price fairness."]
    deployed = _ok(factory.deploy_contract_tx(args=args, account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    owner = factory.build_contract(address, account=default_account)
    first = factory.build_contract(address, account=secondary_account)
    second = factory.build_contract(address, account=tertiary_account)
    _ok(owner.add_requirement(args=["prep", "Patch and sand small holes and clean every wall before painting."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(owner.add_requirement(args=["finish", "Apply two finish coats and protect flooring and trim."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(owner.open_quotes(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(first.submit_quote(args=["q1", "Includes patching, sanding, cleaning, two finish coats, full trim and floor protection, cleanup, and a three-day schedule.", 4200]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(second.submit_quote(args=["q2", "Includes surface preparation, two finish coats, trim protection, cleanup, and a four-day written schedule.", 3900]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(owner.lock_quotes(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = _ok(owner.assess_quote(args=["q1"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    quote = owner.get_quote(args=["q1"]).call()
    assert len(quote["coverage_mask"]) == 2 and quote["risk"] in ("LOW", "MEDIUM", "HIGH")
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": quote["coverage_mask"] + "/" + quote["risk"]}, sort_keys=True))
