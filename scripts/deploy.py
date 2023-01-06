import argparse
import json

from eth_account.signers.base import BaseAccount
from web3 import HTTPProvider, Web3, eth

from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.lang.vm.crypto import get_crypto_lib_context_manager
from starkware.cairo.sharp.sharp_client import init_client, SharpClient
from utils import send_transaction, deploy_contract

def deploy_treasury(
    w3: Web3,
    operator: BaseAccount,
    sharp_client: SharpClient,
    solidity_compiled_code_path: str,
    cairo_code_path: str,
) -> eth.Contract:
    program = sharp_client.compile_cairo(source_code_path=cairo_code_path)
    program_hash = compute_program_hash_chain(program)
    print(f"Cairo program hash: {program_hash}")
    cairo_verifier = sharp_client.contract_client.contract.address
    print(f"Cairo verifier contract address: {cairo_verifier}")

    with open(solidity_compiled_code_path) as f:
        artifacts = json.loads(f.read())
    treasury = w3.eth.contract(abi=artifacts["abi"], bytecode=artifacts["bytecode"])

    transaction = treasury.constructor(
        program_hash,
        cairo_verifier,
    )

    tx_deploy = deploy_contract(w3, operator, transaction)
    return w3.eth.contract(address=tx_deploy.contractAddress, abi=artifacts["abi"])

def deploy_token(
    w3: Web3,
    operator: BaseAccount,
    solidity_compiled_code_path: str,
    token_name: str,
    token_symbol: str,
) -> eth.Contract:
    with open(solidity_compiled_code_path) as f:
        artifacts = json.loads(f.read())
    token = w3.eth.contract(abi=artifacts["abi"], bytecode=artifacts["bytecode"])

    transaction = token.constructor(
        name_=token_name,
        symbol_=token_symbol
    )

    tx_deploy = deploy_contract(w3, operator, transaction)
    return w3.eth.contract(address=tx_deploy.contractAddress, abi=artifacts["abi"])


def main():
    """
    The main demonstration program.
    """

    parser = argparse.ArgumentParser(description="AMM demo")
    parser.add_argument(
        "--rpc_url",
        type=str,
        default="https://eth-goerli.g.alchemy.com/v2/DxDV89UmF7aRrlPaKrKcUcKhe1uDNUqN",
    )
    parser.add_argument(
        "--program",
        type=str,
    )
    parser.add_argument(
        "--contract",
        type=str,
    )
    parser.add_argument(
        "--key",
        type=str,
        default="0xc8b486d1cd5cb4835025983c1e41bfcb91421e3e83dca926514394204409b9a8",
    )
    args = parser.parse_args()

    # Connect to an Ethereum node.
    w3 = Web3(HTTPProvider(args.rpc_url))
    if not w3.isConnected():
        print("Error: could not connect to the Ethereum node.")
        exit(1)

    # Initialize Ethereum account for on-chain transaction sending.
    operator = eth.Account.from_key(args.key)

    # Initialize the system.
    sharp_client = init_client(bin_dir="", node_rpc_url=args.rpc_url)

    # Deploy contract
    treasury_contract = deploy_treasury(
        sharp_client, args.program, args.contract, w3, operator
    )
    print(treasury_contract)

if __name__ == "__main__":
    with get_crypto_lib_context_manager("Release"):
        main()
