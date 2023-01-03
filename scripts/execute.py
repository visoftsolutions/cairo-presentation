from time import sleep
from datetime import datetime
from dataclasses import dataclass
import json

from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.sharp.sharp_client import init_client
from starkware.cairo.bootloaders.generate_fact import get_program_output

from eth_account.signers.base import BaseAccount
from web3 import HTTPProvider, Web3, eth

OWNER_KEY = "0xc8b486d1cd5cb4835025983c1e41bfcb91421e3e83dca926514394204409b9a8"
RPC_URL = "https://eth-goerli.g.alchemy.com/v2/DxDV89UmF7aRrlPaKrKcUcKhe1uDNUqN"
TREASURY_ADDRESS = "0x082d29217832234868aCC671C1B0B58e79E1Ea2F"


@dataclass
class Entry:
    valutId: int
    amountBefore: int
    amountAfter: int


@dataclass
class ProgramOutput:
    entries: list[Entry]


def tx_kwargs(w3: Web3, sender_account: eth.Account):
    """
    Helper function used to send Ethereum transactions.
    w3: a web3 Ethereum client.
    sender_account: the account sending the transaction.
    """
    nonce = w3.eth.getTransactionCount(sender_account)
    return {"from": sender_account, "gas": 10**6, "gasPrice": 10000000000, "nonce": nonce}


def send_transaction(w3, transaction, sender_account: BaseAccount):
    """
    Sends an Ethereum transaction and waits for it to be mined.
    w3: a web3 Ethereum client.
    transaction: the transaction to be sent.
    sender_account: the account sending the transaction.
    """
    transaction_dict = transaction.buildTransaction(
        tx_kwargs(w3, sender_account.address))
    signed_transaction = sender_account.signTransaction(transaction_dict)
    print("Transaction built and signed")
    tx_hash = w3.eth.sendRawTransaction(
        signed_transaction.rawTransaction).hex()
    print(f"Transaction sent")
    print(tx_hash)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction successfully mined")
    return receipt


def main():
    sharp_client = init_client(bin_dir="", node_rpc_url=RPC_URL)
    verifier_address = sharp_client.contract_client.contract.address
    print(f"verifier_address: {verifier_address}")

    program = sharp_client.compile_cairo(
        source_code_path="provable/main.cairo")
    program_hash = compute_program_hash_chain(program)
    print(f"program_hash: {program_hash}")

    cairo_pie = sharp_client.run_program(
        program=program, program_input_path="provable/input.json"
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

    w3 = Web3(HTTPProvider(RPC_URL))
    if not w3.isConnected():
        print("Error: could not connect to the Ethereum node.")
        exit(1)
    operator = eth.Account.from_key(OWNER_KEY)
    with open("artifacts/contracts/Treasury.sol/Treasury.json") as f:
        artifacts = json.loads(f.read())
    abi = artifacts["abi"]
    contract = w3.eth.contract(address=TREASURY_ADDRESS, abi=abi)
    transaction = contract.functions.updateState(output)
    tx_receipt = send_transaction(w3, transaction, operator)
    print(tx_receipt)


if __name__ == "__main__":
    main()
