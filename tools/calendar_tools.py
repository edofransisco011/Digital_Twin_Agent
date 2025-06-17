# digital_twin_agent/core/agent.py

import os
import datetime
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
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

# --- Define the BASE System Prompt ---
# This is the static part of the prompt.
system_prompt_template = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You will manage schedules, handle emails, and draft communications that match the user's persona. "
    "When asked about schedules or plans, use the google_calendar_reader tool.\n\n"
    "Current date: {current_date}" # Placeholder for the dynamic date.
)

# --- Initialize Tools ---
calendar_tool = GoogleCalendarTool()

# --- Initialize the Assistant Agent ---
# We initialize the agent without a system message first. We will add it dynamically.
digital_twin = Assistant(
    llm=llm_config,
    function_list=[calendar_tool] 
)

def run_agent_with_dynamic_prompt(messages: list) -> list:
    """
    Injects the current date into the system prompt before running the agent.
    """
    # Get today's date in YYYY-MM-DD format.
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    # Format the system prompt with the current date.
    dynamic_system_prompt = system_prompt_template.format(current_date=today_str)
    
    # Set the dynamic system message for the agent for this specific run.
    digital_twin.system_message = dynamic_system_prompt
    
    # Run the agent and return the full response stream.
    return digital_twin.run(messages=messages)


# Main execution block
if __name__ == '__main__':
    # Add a check to ensure API credentials are provided
    if not llm_config['model_server'] or not llm_config['api_key']:
        print("Error: MODEL_STUDIO_URL and MODEL_STUDIO_API_KEY must be set in the .env file.")
    else:
        print("Digital Twin agent initialized successfully.")
        print(f"Connecting to model server at: {llm_config['model_server']}")
        
        # The user's message
        user_messages = [{'role': 'user', 'content': 'What does my schedule look like today?'}]
        
        # Run the agent using our new wrapper function
        final_response = None
        for response in run_agent_with_dynamic_prompt(user_messages):
            final_response = response
        
        # Print only the final, complete response after the streaming is done.
        if final_response:
            print("\n--- Tool Call and Final Response ---")
            # We print the full final response list to see the agent's reasoning and tool output
            for item in final_response:
                print(item)