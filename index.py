from web3 import Web3
import os
import config
from phi.agent import Agent, RunResponse
from phi.model.openai import OpenAIChat

# Function to create a new wallet
def create_wallet():
    w3 = Web3()
    account = w3.eth.account.create()  # Create a new wallet
    private_key = account._private_key.hex()  # Get the private key in hex format
    return account.address, private_key  # Return address and private key

def store_private_key(private_key):
    # You could save it to an environment variable or a secure vault instead of printing it
    # os.environ['AGENT_PRIVATE_KEY'] = private_key
    print("Private key (keep it secret):", private_key)

# Create a wallet for your agent
# agent_address, agent_private_key = create_wallet()
# store_private_key(agent_private_key)

# Example of how your agent can use this wallet
def agent_interact_with_contract(agent_private_key):
    # Initialize Web3 connection to your Avalanche L1
    w3 = Web3(Web3.HTTPProvider('https://node.l1marketplace.com/ext/bc/2VGbAG68yBSqUxdRTbCZ9A84yT5YFR7yvKTn6N57WFLtJcAdHR/rpc'))  # Mainnet RPC

    # Create account instance from private key
    account = w3.eth.account.privateKeyToAccount(agent_private_key)

    # ABI for your contract
    contract_abi = [
        {
            "inputs": [{"internalType": "uint256", "name": "_newGasPrice", "type": "uint256"}],
            "name": "updateGasPrice",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    # Contract address for your GasPriceManager
    contract_address = "0xYourContractAddressHere"

    # Create contract instance
    gas_price_manager = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Specify the new gas price (you could fetch this from Chainlink)
    new_gas_price = 100  # Example static value

    # Build the transaction
    tx = gas_price_manager.functions.updateGasPrice(new_gas_price).buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei'),
        'chainId': 43114  # Avalanche C-Chain Mainnet chain ID
    })

    # Sign the transaction
    signed_tx = w3.eth.account.signTransaction(tx, agent_private_key)

    # Send the transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    print(f"Transaction hash: {tx_hash.hex()}")

# Allow the agent to interact with the contract
# agent_interact_with_contract(agent_private_key)


agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    show_tool_calls=True,
    # tools=[BlockchainTools()],
    description="You are an AI agent to help DAO's make wise decisions and help them interacting with contracts and transactions",
    markdown=True,
    # show_tool_calls=True,
    add_datetime_to_instructions=True
    )




# agent = Agent(
#     model=OpenAIChat(id="gpt-4o"),
# )

agent.print_response("How are u doing?")
# Build the transaction
# tx = gas_price_manager.functions.updateGasPrice(new_gas_price).buildTransaction({
#     'nonce': w3.eth.getTransactionCount(account.address),
#     'gas': 2000000,
#     'gasPrice': w3.toWei('50', 'gwei'),
#     'chainId': 43114  # Avalanche C-Chain Mainnet chain ID
# })
