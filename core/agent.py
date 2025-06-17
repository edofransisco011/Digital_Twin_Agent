# digital_twin_agent/core/agent.py

import os
import datetime
import pprint
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
from tools.calendar_tools import GoogleCalendarTool
from tools.email_tools import GmailTool
from tools.style_retriever_tool import StyleRetrieverTool # Import the new tool

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
# We've updated the instructions for email drafting.
system_prompt_template = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "When asked about schedules, use the google_calendar_reader tool. "
    "When asked about your inbox, use the gmail_reader tool.\n"
    "IMPORTANT: When asked to DRAFT an email, you MUST follow these two steps:\n"
    "1. First, use the `style_retriever` tool to get examples of the user's writing style. The topic for the tool should be the core message of the email.\n"
    "2. Second, use the retrieved style examples to write the email draft, ensuring the tone, phrasing, and structure match the examples.\n\n"
    "Current date: {current_date}"
)

# --- Initialize Tools ---
print("Initializing tools...")
calendar_tool = GoogleCalendarTool()
gmail_tool = GmailTool()
style_tool = StyleRetrieverTool() # Create an instance of the new tool
print("Tools initialized successfully.")

# --- Initialize the Assistant Agent ---
# Add the new tool to the agent's function list
digital_twin = Assistant(
    llm=llm_config,
    function_list=[calendar_tool, gmail_tool, style_tool] 
)

def run_agent_with_dynamic_prompt(messages: list) -> list:
    """
    Injects the current date into the system prompt before running the agent.
    """
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    dynamic_system_prompt = system_prompt_template.format(current_date=today_str)
    digital_twin.system_message = dynamic_system_prompt
    return digital_twin.run(messages=messages)


# --- Main Interactive Chat Loop ---
if __name__ == '__main__':
    if not llm_config['model_server'] or not llm_config['api_key']:
        print("Error: MODEL_STUDIO_URL and MODEL_STUDIO_API_KEY must be set in the .env file.")
    else:
        print("\n--- Digital Twin Assistant ---")
        print("Try asking me to 'draft an email to a colleague about our project update'.")
        print("Type 'quit' or 'exit' to end the conversation.")
        
        chat_history = []

        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Assistant: Goodbye!")
                break

            chat_history.append({'role': 'user', 'content': user_input})
            
            final_response = None
            response_stream = run_agent_with_dynamic_prompt(chat_history)
            
            print("Assistant: ", end="", flush=True)
            for response in response_stream:
                final_response = response
            
            if final_response:
                assistant_message = final_response[-1] 
                print(assistant_message['content'])
                chat_history.extend(final_response)
            else:
                print("I'm sorry, I encountered an error and couldn't process your request.")