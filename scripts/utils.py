from eth_account.signers.base import BaseAccount
from web3 import Web3, exceptions
from colorama import Fore

yes = {'yes', 'y', 'ye', ''}
no = {'no', 'n'}


def prompt():
    print(" [y/n]")
    while True:
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")


def retry(f):
    while True:
        try:
            ret = f()
        except exceptions.TimeExhausted as err:
            print(Fore.LIGHTRED_EX + str(err))
            print("retrying...")
            continue
        else:
            return ret


def send_transaction(w3: Web3, transaction, operator: BaseAccount):
    """
    Sends an Ethereum transaction and waits for it to be mined.
    w3: a web3 Ethereum client.
    transaction: the transaction to be sent.
    sender_account: the account sending the transaction.
    """
    gas_price = int(w3.eth.gas_price*1.2)
    transaction = transaction.buildTransaction(
        {
            "from": operator.address,
            "gas": 0,
            "gasPrice": gas_price,
            "nonce": w3.eth.getTransactionCount(operator.address)}
    )

    gas = int(w3.eth.estimate_gas(transaction)*1.2)
    transaction.update({"gas": gas})

    signed_transaction = operator.signTransaction(transaction)
    print(
        f'Transaction built and signed. gasPrice: {Web3.fromWei(gas_price, "gwei")} Gwei ', end="", flush=True)
    tx_hash = w3.eth.sendRawTransaction(
        signed_transaction.rawTransaction).hex()

    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    print(Fore.LIGHTGREEN_EX + "successfully mined" + Fore.RESET)
    print("Tx hash " + Fore.LIGHTBLUE_EX + f"{tx_hash}" + Fore.RESET)
    return receipt


def deploy_contract(
    w3: Web3,
    operator: BaseAccount,
    transaction,
):
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
    return tx_receipt
