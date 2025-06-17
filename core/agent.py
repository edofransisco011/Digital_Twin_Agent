# digital_twin_agent/core/agent.py

import os
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
# Import the new tool we just created
from tools.calendar_tools import GoogleCalendarTool

# --- Load Environment Variables ---
load_dotenv()

# --- Configure the Language Model (LLM) ---
llm_config = {
    'model_server': os.getenv('MODEL_STUDIO_URL'),
    'api_key': os.getenv('MODEL_STUDIO_API_KEY'),
    'model': 'qwen-max', 
    'generate_cfg': {
        'top_p': 0.8
    }
}

# --- Define the System Prompt ---
system_prompt = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You will manage schedules, handle emails, and draft communications that match the user's persona. "
    "When asked about schedules or plans, use the google_calendar_reader tool."
)

# --- Initialize Tools ---
# Create an instance of our Google Calendar tool.
# This will trigger the authentication flow if run for the first time.
calendar_tool = GoogleCalendarTool()


# --- Initialize the Assistant Agent ---
# We now provide the 'function_list' with our tool instance. The agent will
# automatically know about this tool and its capabilities.
digital_twin = Assistant(
    llm=llm_config,
    system_message=system_prompt,
    function_list=[calendar_tool] 
)

# You can add a simple test here to ensure the agent is initialized.
if __name__ == '__main__':
    # Add a check to ensure API credentials are provided
    if not llm_config['model_server'] or not llm_config['api_key']:
        print("Error: MODEL_STUDIO_URL and MODEL_STUDIO_API_KEY must be set in the .env file.")
    else:
        print("Digital Twin agent initialized successfully.")
        print(f"Connecting to model server at: {llm_config['model_server']}")
        
        # NEW TEST CASE: This prompt is designed to trigger our new tool.
        messages = [{'role': 'user', 'content': 'What does my schedule look like today?'}]
        
        final_response = None
        
        # Loop through the streaming responses from the agent
        for response in digital_twin.run(messages):
            final_response = response
        
        # Print only the final, complete response after the streaming is done.
        if final_response:
            print("\n--- Tool Call and Final Response ---")
            # We print the full final response list to see the agent's reasoning and tool output
            for item in final_response:
                print(item)