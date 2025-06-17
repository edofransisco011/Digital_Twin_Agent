# digital_twin_agent/core/agent.py

import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Load Environment Variables ---
# This line loads the environment variables from the .env file in the project's root directory.
# It's crucial for securely managing API keys and other configurations.
load_dotenv()

# --- Configure the Language Model (LLM) ---
# This dictionary defines the settings for the LLM that our agent will use.
# We are configuring it to use a custom model deployed via Alibaba Cloud Model Studio.
llm_config = {
    # Instead of 'dashscope', provide the full API Endpoint URL from your Model Studio deployment.
    # This tells the agent to connect to your specific model instance.
    'model_server': os.getenv('MODEL_STUDIO_URL'), # e.g., 'http://<your-model-studio-endpoint>/v1'

    # The API key for your specific Model Studio deployment.
    # We fetch this from the environment variables for security.
    'api_key': os.getenv('MODEL_STUDIO_API_KEY'),

    # The model name can often be a placeholder when using a direct endpoint,
    # but it's good practice to set it to the name of your deployed model.
    'model': 'qwen-max', 

    # Optional: Configuration for the generation process.
    'generate_cfg': {
        'top_p': 0.8
    }
}


# --- Define the System Prompt ---
# The system prompt gives the LLM its core identity and instructions.
# It sets the context for all future interactions.
system_prompt = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You will manage schedules, handle emails, and draft communications that match the user's persona. "
    "Always be helpful, efficient, and maintain the user's voice."
)


# --- Initialize the Assistant Agent ---
# We create an instance of the Assistant agent, which is designed to be a general-purpose
# helper capable of using tools to accomplish tasks.
digital_twin = Assistant(
    llm=llm_config,          # Pass the LLM configuration.
    system_message=system_prompt  # Set the agent's core identity.
)

# You can add a simple test here to ensure the agent is initialized.
if __name__ == '__main__':
    # Add a check to ensure API credentials are provided
    if not llm_config['model_server'] or not llm_config['api_key']:
        print("Error: MODEL_STUDIO_URL and MODEL_STUDIO_API_KEY must be set in the .env file.")
    else:
        print("Digital Twin agent initialized successfully.")
        print(f"Connecting to model server at: {llm_config['model_server']}")
        # A simple test to see if the LLM is responding.
        # This will be replaced with our main CLI loop later.
        messages = [{'role': 'user', 'content': 'Hello, who are you?'}]
        for response in digital_twin.run(messages):
            print(response)

