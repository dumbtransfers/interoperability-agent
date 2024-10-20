from phi.agent import Agent
from phi.model.openai import OpenAIChat
from flask import Flask, request, jsonify
from flask_cors import CORS
import config
from transfer import send_tokens  # Import send_tokens function
from web3 import Web3
infura_url = "https://sepolia.infura.io/v3/60cf1667ba5a45bc9f257d9e25e82241"  # Replace with your Infura Project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

# Initialize the agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="You are an AI agent that helps with token transfers and answers general questions. \
    Respond with 'interpolability: true' when the user wants to send tokens, and include a relevant message.",
    markdown=True,
    add_datetime_to_instructions=True
)

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/api/assistant', methods=['POST'])
def ai_assistant():
    data = request.json
    message = data.get('message')

    # Get the agent's response
    response = agent.run(message)

    # Determine if the message indicates a token transfer request
    is_interpolability = "send my tokens" in message.lower()  # Adjust this condition as needed

    # Construct the response JSON
    print(response.content, "test reponse.content")
    print(is_interpolability, "test reponse.is_interpolability")

    agent_response = {
        "message": response.content,
        "interpolability": is_interpolability
    }

    destination_chain_selector = 14767482510784806043  # Replace with your chain selector
    receiver = "0x52eF0e850337ecEC348C41919862dBAac42F620B"  # Replace with receiver address
    tokens_to_send_details = [
        {
            "token": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # Replace with the actual USDC token address on Sepolia
            "amount": web3.to_wei(0.00001, 'mwei')  # USDC has 6 decimal places, so use 'mwei' for 100 USDC
        }
    ]
    pay_fees_in = 0 

    # If the message indicates a token transfer, trigger the send_tokens function
    if agent_response["interpolability"]:
        # Replace these with actual details from the user's message if applicable
        agent_response["message"] = send_tokens(destination_chain_selector, receiver, tokens_to_send_details, pay_fees_in)
    
    print(agent_response, "check the agent_reponse")

    return jsonify(agent_response["message"])
# def ai_assistant():
#     data = request.json
#     message = data.get('message')
#     response = agent.run(message)
    

#     # Process the message and return a response
#     return jsonify(response.content)

if __name__ == '__main__':
    app.run(debug=True)

