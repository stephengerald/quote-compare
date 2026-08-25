from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "quote_compare.py"
SDK = "v0.2.16"
PROMPT = "Independently compare one contractor quote"
SCOPE = "Repaint a small community-room interior, including wall preparation, two finish coats, trim protection, cleanup, and a written work schedule."
STANDARD = "A requirement is covered only when the quote expressly commits to it. Risk is high for material exclusions or contradictory terms, medium for bounded ambiguity, and low otherwise. Do not judge price fairness."


def deploy(vm, direct_deploy, alice):
    vm.sender = alice
    return direct_deploy(str(CONTRACT), SCOPE, STANDARD, sdk_version=SDK)


def prepare(contract, vm, alice, bob, charlie):
    contract.add_requirement("prep", "Patch small holes, sand repaired areas, and clean surfaces before painting.")
    contract.add_requirement("finish", "Apply two finish coats and protect trim and flooring during the work.")
    contract.open_quotes()
    vm.sender = bob
    contract.submit_quote("q-bob", "Includes patching and sanding, surface cleaning, two finish coats, full floor and trim protection, cleanup, and a three-day schedule.", 4200)
    vm.sender = charlie
    contract.submit_quote("q-charlie", "Includes surface preparation, two finish coats, trim protection, daily cleanup, and a four-day written schedule.", 3900)
    vm.sender = alice
    contract.lock_quotes()


def test_assess_shortlist_and_select(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    prepare(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "11", "risk": "LOW"}))
    contract.assess_quote("q-bob")
    contract.assess_quote("q-charlie")
    contract.shortlist_quote("q-bob")
    contract.select_quote("q-bob")
    assert contract.get_state()["phase"] == "SELECTED"
    assert contract.get_quote("q-bob")["status"] == "ELIGIBLE"
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True


def test_incomplete_quote_cannot_be_shortlisted(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    prepare(contract, direct_vm, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "10", "risk": "MEDIUM"}))
    contract.assess_quote("q-bob")
    contract.assess_quote("q-charlie")
    with direct_vm.expect_revert("only_eligible_quote"):
        contract.shortlist_quote("q-bob")


def test_one_quote_per_bidder_and_bad_mask_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = deploy(direct_vm, direct_deploy, direct_alice)
    contract.add_requirement("prep", "Prepare every wall according to the frozen room scope before applying finish coats.")
    contract.add_requirement("finish", "Apply all stated coats and protect the identified room surfaces.")
    contract.open_quotes()
    direct_vm.sender = direct_bob
    contract.submit_quote("first", "The quote expressly includes all wall preparation, both finish coats, surface protection, cleanup, and the requested schedule.", 4000)
    with direct_vm.expect_revert("one_quote_per_bidder"):
        contract.submit_quote("second", "A second quote from the same bidder must not enter this comparison round or replace the first quote.", 3800)
    direct_vm.sender = direct_charlie
    contract.submit_quote("other", "The quote includes wall preparation, both finish coats, surface protection, cleanup, and a dated schedule.", 4100)
    direct_vm.sender = direct_alice
    contract.lock_quotes()
    direct_vm.mock_llm(PROMPT, json.dumps({"coverage_mask": "111", "risk": "LOW"}))
    with direct_vm.expect_revert("invalid_coverage_mask"):
        contract.assess_quote("first")
    assert contract.get_state()["assessed_count"] == 0

