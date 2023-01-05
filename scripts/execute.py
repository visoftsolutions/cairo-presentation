from time import sleep
from datetime import datetime
from dataclasses import dataclass

from eth_account.signers.base import BaseAccount
from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.sharp.sharp_client import SharpClient
from starkware.cairo.bootloaders.generate_fact import get_program_output
from starkware.cairo.sharp.sharp_client import init_client

from web3 import HTTPProvider, Web3, eth, exceptions
from web3.contract import Contract
from utils import send_transaction, retry
import colorama
from colorama import Fore
import json

TREASURY_ADDRESS = "0x5Bb8f67bF21D7677fFa68D8816EEc055Cefc8F01"

goerli_url = "https://eth-goerli.g.alchemy.com/v2/DxDV89UmF7aRrlPaKrKcUcKhe1uDNUqN"

accounts_conf = {
    "account1": "0xc8b486d1cd5cb4835025983c1e41bfcb91421e3e83dca926514394204409b9a8",
    "account2": "0x435aa22562edbdce8e72101ec2d04c5ed9ce1d9c93378e45a51bb928c49ca04b",
    "account3": "0x637cf0cb529ff41499db61e0913674570ebd68c9d7c9a7a021cffd3c02c85427",
}

treasury_conf = {
    "path": "artifacts/contracts/Treasury.sol/Treasury.json",
    "cairo_code": "provable/main.cairo",
    "cairo_input": "provable/input.json",
}

token_conf = {
    "path": "artifacts/contracts/Token.sol/Token.json",
    "name": "CairoCoin",
    "symbol": "CAIR"
}

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

def main():
    w3 = Web3(HTTPProvider(goerli_url))
    if not w3.isConnected():
        print("Error: could not connect to the Ethereum node")
        exit(1)
    print("Connected to Testnet")

    operator = eth.Account.from_key(accounts_conf["account3"])
    sharp_client = init_client(bin_dir="", node_rpc_url=goerli_url)
    print("\n")

    with open(treasury_conf["path"]) as f:
        artifacts = json.loads(f.read())
    _contract_treasury = w3.eth.contract(address=TREASURY_ADDRESS, abi=artifacts["abi"])

    retry(lambda: update_state(
            w3 = w3,
            operator = operator,
            contract = _contract_treasury,
            sharp_client = sharp_client,
            cairo_code_path = treasury_conf["cairo_code"],
            program_input_path = treasury_conf["cairo_input"],
    ))
    print(f'Update Treasury ' + Fore.LIGHTGREEN_EX + f'successful' )

if __name__ == "__main__":
    colorama.init(autoreset=True)
    main()
