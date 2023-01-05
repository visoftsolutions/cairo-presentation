from eth_account.signers.base import BaseAccount
from web3 import HTTPProvider, Web3, eth

yes = {'yes','y', 'ye', ''}
no = {'no','n'}

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