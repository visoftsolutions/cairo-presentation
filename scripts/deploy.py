import argparse
import json

from eth_account.signers.base import BaseAccount
from web3 import HTTPProvider, Web3, eth

from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.lang.vm.crypto import get_crypto_lib_context_manager
from starkware.cairo.sharp.sharp_client import init_client, SharpClient


def deploy_contract(
    sharp_client: SharpClient,
    cairo_code_path: str,
    solidity_compiled_code_path: str,
    w3: Web3,
    operator: BaseAccount
) -> eth.Contract:
    program = sharp_client.compile_cairo(source_code_path=cairo_code_path)
    program_hash = compute_program_hash_chain(program)
    print(f"Cairo program hash: {program_hash}")
    cairo_verifier = sharp_client.contract_client.contract.address
    print(f"Cairo verifier contract address: {cairo_verifier}")

    with open(solidity_compiled_code_path) as f:
        artifacts = json.loads(f.read())
    bytecode = artifacts["bytecode"]
    abi = artifacts["abi"]
    new_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = new_contract.constructor(
        program_hash,
        cairo_verifier,
    )
    print("Deploying smart contract...")
    tx_receipt = send_transaction(w3, transaction, operator)
    assert (
        tx_receipt["status"] == 1
    ), f'Failed to deploy contract. Transaction hash: {tx_receipt["transactionHash"]}.'

    contract_address = tx_receipt["contractAddress"]
    print(
        f"Smart contract successfully deployed to address {contract_address}\n"
        "You can track the contract state through this link\n"
        f"https://goerli.etherscan.io/address/{contract_address}"
    )

    return w3.eth.contract(abi=abi, address=contract_address)


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
    treasury_contract = deploy_contract(
        sharp_client, args.program, args.contract, w3, operator
    )


def tx_kwargs(w3: Web3, sender_account: eth.Account):
    """
    Helper function used to send Ethereum transactions.
    w3: a web3 Ethereum client.
    sender_account: the account sending the transaction.
    """
    nonce = w3.eth.getTransactionCount(sender_account)
    return {"from": sender_account, "gas": 5*10**6, "gasPrice": 10**10, "nonce": nonce}


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


if __name__ == "__main__":
    with get_crypto_lib_context_manager("Release"):
        main()
