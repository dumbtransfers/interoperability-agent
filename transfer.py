from web3 import Web3

# Connect to Sepolia network
infura_url = "https://sepolia.infura.io/v3/60cf1667ba5a45bc9f257d9e25e82241"  # Replace with your Infura Project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connected
if web3.is_connected():
    print("Connected to Sepolia")
else:
    print("Failed to connect")

# Your contract's ABI (replace with your contract's ABI)
contract_abi = [
    {
      "inputs": [
        {
          "internalType": "uint64",
          "name": "destinationChainSelector",
          "type": "uint64"
        },
        {
          "internalType": "address",
          "name": "receiver",
          "type": "address"
        },
        {
          "components": [
            {
              "internalType": "address",
              "name": "token",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "amount",
              "type": "uint256"
            }
          ],
          "internalType": "struct Client.EVMTokenAmount[]",
          "name": "tokensToSendDetails",
          "type": "tuple[]"
        },
        {
          "internalType": "enum BasicTokenSender.PayFeesIn",
          "name": "payFeesIn",
          "type": "uint8"
        }
      ],
      "name": "send",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

# Your deployed contract address (replace with your contract address)
contract_address = "0xe6c1Be68455a6Aabc8CCD08B0bb5069eb6dE936F"

# Create the contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Your wallet address and private key
wallet_address = "0x52eF0e850337ecEC348C41919862dBAac42F620B"  # Replace with your wallet address
private_key = ""  # Replace with your wallet's private key


usdc_abi = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "type": "function"
    }
]

def approve_tokens(amount):
    usdc_contract = web3.eth.contract(address='0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238', abi=usdc_abi)
    approve_txn = usdc_contract.functions.approve(
        contract_address,  # Your contract
        amount  # Amount you want to approve
    ).build_transaction({
        'from': wallet_address,
        'gas': 200000,
        'gasPrice': web3.to_wei('1', 'gwei'),
        'nonce': web3.eth.get_transaction_count(wallet_address),
    })

    # Sign and send the approve transaction
    signed_approve_txn = web3.eth.account.sign_transaction(approve_txn, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_approve_txn.raw_transaction)
    web3.eth.wait_for_transaction_receipt(txn_hash)

def check_allowance():
    usdc_contract = web3.eth.contract(address='0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238', abi=usdc_abi)
    allowance = usdc_contract.functions.allowance(wallet_address, contract_address).call()
    print(f"Allowance: {web3.from_wei(allowance, 'mwei')} USDC")

# Function to send tokens
def send_tokens(destination_chain_selector, receiver, tokens_to_send_details, pay_fees_in):
    check_allowance()
    approve_tokens(web3.to_wei(0.00001, 'mwei'))  # Approve enough USDC for sending 1 mwei
    nonce = web3.eth.get_transaction_count(wallet_address)

    # Build the transaction
    txn = contract.functions.send(
        destination_chain_selector,
        receiver,
        tokens_to_send_details,
        pay_fees_in
    ).build_transaction({
        'chainId': 11155111,  # Sepolia chain ID
        'gas': 2000000,  # Adjust the gas limit if necessary
        'gasPrice': web3.to_wei('1', 'gwei'),  # Adjust the gas price if necessary
        'nonce': nonce,
    })


    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)

    # Send the transaction
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent: {web3.to_hex(txn_hash)}")

    # Wait for the transaction receipt
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Transaction receipt: {txn_receipt}")

# Example usage
destination_chain_selector = 14767482510784806043  # Replace with your chain selector
receiver = "0x52eF0e850337ecEC348C41919862dBAac42F620B"  # Replace with receiver address
tokens_to_send_details = [
    {
        "token": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # Replace with the actual USDC token address on Sepolia
        "amount": web3.to_wei(0.00001, 'mwei')  # USDC has 6 decimal places, so use 'mwei' for 100 USDC
    }
]
pay_fees_in = 0  # Adjust based on your contract's expected input

# usdc_contract = web3.eth.contract(address='0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238', abi=usdc_abi)

# # Approve contract to spend tokens
# usdc_contract.functions.approve(contract_address, web3.to_wei(1, 'mwei')).transact({'from': wallet_address})

send_tokens(destination_chain_selector, receiver, tokens_to_send_details, pay_fees_in)
