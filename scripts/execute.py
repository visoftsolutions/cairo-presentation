from time import sleep
from datetime import datetime
from dataclasses import dataclass

from eth_account.signers.base import BaseAccount
from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.sharp.sharp_client import SharpClient
from starkware.cairo.bootloaders.generate_fact import get_program_output

from web3 import Web3
from web3.contract import Contract
from utils import send_transaction

OWNER_KEY = "0xc8b486d1cd5cb4835025983c1e41bfcb91421e3e83dca926514394204409b9a8"
TREASURY_ADDRESS = "0x082d29217832234868aCC671C1B0B58e79E1Ea2F"


@dataclass
class Entry:
    valutId: int
    amountBefore: int
    amountAfter: int


@dataclass
class ProgramOutput:
    entries: list[Entry]


def update_state(
    w3: Web3,
    operator: BaseAccount,
    contract: Contract,
    sharp_client: SharpClient,
    cairo_code_path: str,
    program_input_path: str,
):
    verifier_address = sharp_client.contract_client.contract.address
    print(f"verifier_address: {verifier_address}")

    program = sharp_client.compile_cairo(
        source_code_path=cairo_code_path)
    program_hash = compute_program_hash_chain(program)
    print(f"program_hash: {program_hash}")

    cairo_pie = sharp_client.run_program(
        program=program, program_input_path=program_input_path
    )
    job_key = sharp_client.submit_cairo_pie(cairo_pie=cairo_pie)
    print(f"job_key: {job_key}")
    fact = sharp_client.get_fact(cairo_pie)
    print(f"fact: {fact}")
    output = get_program_output(cairo_pie)
    print(f"output: {output}")

    print(f"start time: {datetime.now()}")
    while not sharp_client.fact_registered(fact=fact):
        print(".", end="", flush=True)
        sleep(5)
    print(f"\nend time: {datetime.now()}")

    transaction = contract.functions.updateState(output)
    tx_receipt = send_transaction(w3, transaction, operator)
    return tx_receipt


if __name__ == "__main__":
    pass
