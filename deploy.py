import json

from solcx import compile_standard, install_solc
from web3 import Web3

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.8.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

    # bytecode
    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]

    # abi
    abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x55ccA73711A0E420beb236e0b69F5e97bCd2c146"
private_key = "0x7c298c9dc0fcc233a44eb6c3ea46cd876154cac020203edc720ead50cd0675e9"

# contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.get_transaction_count(my_address)

transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

# interact with contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# ways of interacting with contracts
# call = simulate making a call and getting return value without making a state change
# transact = making a state change
print("Updating...")
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
