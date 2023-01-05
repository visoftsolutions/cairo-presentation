import json
from execute import update_state
from deploy import deploy_treasury, deploy_token
from web3 import HTTPProvider, Web3, eth
from utils import prompt, send_transaction
from starkware.cairo.sharp.sharp_client import init_client

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

mintAmount_conf = {
    "account1": (10**18)*1000,
    "account2": (10**18)*1000,
}

approvalAmount = (10**18)*100
depositAmount = (10**18)*100

if __name__ == "__main__":
    w3 = Web3(HTTPProvider(goerli_url))
    if not w3.isConnected():
        print("Error: could not connect to the Ethereum node")
        exit(1)
    print("Connected to Testnet")

    signer1 = eth.Account.from_key(accounts_conf["account3"])
    signer2 = eth.Account.from_key(accounts_conf["account2"])
    sharp_client = init_client(bin_dir="", node_rpc_url=goerli_url)

    print(f'Deploy Treasury Phase, press enter to continue.')
    #input()
    print(f'Deploying Treasury cairo_code: {treasury_conf["cairo_code"]}')
    _contract_treasury = deploy_treasury(
        w3=w3,
        operator=signer1,
        sharp_client=sharp_client,
        solidity_compiled_code_path=treasury_conf["path"],
        cairo_code_path=treasury_conf["cairo_code"]
    )
    print(f'Treasury deployed at address: { _contract_treasury.address }')

    print(f'Deploy Token Phase, press enter to continue.')
    #input()
    print(f'Deploying Token name: {token_conf["name"]} symbol: {token_conf["symbol"]} with owner: { signer1.address }')
    _contract_token = deploy_token(
        w3=w3,
        operator=signer1,
        solidity_compiled_code_path=token_conf["path"],
        token_name=token_conf["name"],
        token_symbol=token_conf["symbol"]
    )
    print(f'Token deployed at address: { _contract_token.address }')
        

    print(f'Mint tokens Phase, press enter to continue.')
    #input()
    print(f'Minting {Web3.fromWei(mintAmount_conf["account1"], "ether")} ETH for {signer1.address}')

    mint_tx = _contract_token.functions.mint(to=signer1.address, amount=mintAmount_conf["account1"])
    tx_receipt = send_transaction(w3, mint_tx, signer1)

    print(f'Mint Tx to address {signer1.address} successful with hash: { tx_receipt.transactionHash.hex() }')
    print(f'Minting {Web3.fromWei(mintAmount_conf["account2"], "ether")} ETH for {signer2.address}')

    mint_tx = _contract_token.functions.mint(to=signer2.address, amount=mintAmount_conf["account2"])
    tx_receipt = send_transaction(w3, mint_tx, signer1)

    print(f'Mint Tx to address {signer2.address} successful with hash: { tx_receipt.transactionHash.hex() }')

    print(f'Approve tokens Phase, press enter to continue.')
    #input()
    print(f'Approving {Web3.fromWei(approvalAmount, "ether")} ETH --> {_contract_treasury.address}')

    approve_tx = _contract_token.functions.approve(spender=_contract_treasury.address, amount=approvalAmount)
    tx_receipt = send_transaction(w3, approve_tx, signer1)

    print(f'Approve Tx to address {_contract_treasury.address} successful with hash: { tx_receipt.transactionHash.hex() }')
    
    print(f'RegisterValut Phase, press enter to continue.')
    #input()
    print(f'Registering Vault for {signer1.address}')

    register_tx = _contract_treasury.functions.registerValut(token=_contract_token.address)
    tx_receipt = send_transaction(w3, register_tx, signer1)

    singer1_vaultId = _contract_treasury.functions.getValutId(_contract_token.address).call({'from': signer1.address})
    print(f'Valut for {signer1.address} is {singer1_vaultId}')

    print(f'Registering Vault for {signer2.address}')

    register_tx = _contract_treasury.functions.registerValut(token=_contract_token.address)
    tx_receipt = send_transaction(w3, register_tx, signer2)

    singer2_vaultId = _contract_treasury.functions.getValutId(_contract_token.address).call({'from': signer2.address})
    print(f'Valut for {signer2.address} is {singer2_vaultId}')
    
    print(f'Deposit Phase, press enter to continue.')
    #input()
    deposit_tx = _contract_treasury.functions.deposit(token=_contract_token.address, amount=depositAmount)
    tx_receipt = send_transaction(w3, deposit_tx, signer1)
    print(f'Deposit from {signer1.address} is {Web3.fromWei(depositAmount, "ether")} ETH')

    print(f'Update Treasury Phase, press enter to continue.')
    #input()
    update_tx = update_state(
        w3 = w3,
        operator = signer1,
        contract = _contract_treasury,
        sharp_client = sharp_client,
        cairo_code_path = treasury_conf["cairo_code"],
        program_input_path = treasury_conf["cairo_input"],
    )

