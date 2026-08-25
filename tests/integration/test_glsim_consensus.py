from __future__ import annotations
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Independently compare one contractor quote"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"coverage_mask": "11", "risk": "LOW"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_quote_selection():
    owner, bidder_one, bidder_two = create_accounts(3)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "quote_compare.py")
    args = ["Repaint a community-room interior, including preparation, two coats, protection, cleanup, and schedule.", "A requirement is covered only when expressly committed. Risk is high for material exclusions, medium for ambiguity, and low otherwise. Do not judge price fairness."]
    deployed = factory.deploy_contract_tx(args=args, account=owner, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    customer = factory.build_contract(address, account=owner)
    first = factory.build_contract(address, account=bidder_one)
    second = factory.build_contract(address, account=bidder_two)
    ok(customer.add_requirement(args=["prep", "Patch and sand small holes and clean every wall before painting."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.add_requirement(args=["finish", "Apply two finish coats and protect flooring and trim."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.open_quotes(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(first.submit_quote(args=["q1", "Includes patching, sanding, cleaning, two finish coats, full trim and floor protection, cleanup, and a three-day schedule.", 4200]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(second.submit_quote(args=["q2", "Includes surface preparation, two finish coats, trim protection, cleanup, and a four-day written schedule.", 3900]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.lock_quotes(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.assess_quote(args=["q1"]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.assess_quote(args=["q2"]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.shortlist_quote(args=["q1"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(customer.select_quote(args=["q1"]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert customer.get_state(args=[]).call()["selected_quote"] == "q1"

