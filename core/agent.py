# digital_twin_agent/core/agent.py

import os
import datetime
import pprint
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
from tools.calendar_tools import GoogleCalendarTool
from tools.email_tools import GmailTool

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
system_prompt_template = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You will manage schedules, handle emails, and draft communications that match the user's persona. "
    "When asked about schedules or plans, use the google_calendar_reader tool. "
    "When asked about emails or your inbox, use the gmail_reader tool.\n\n"
    "Current date: {current_date}"
)

# --- Initialize Tools ---
print("Initializing tools...")
calendar_tool = GoogleCalendarTool()
gmail_tool = GmailTool()
print("Tools initialized successfully.")

# --- Initialize the Assistant Agent ---
digital_twin = Assistant(
    llm=llm_config,
    function_list=[calendar_tool, gmail_tool] 
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
        print("Type 'quit' or 'exit' to end the conversation.")
        
        # This list will store the entire conversation history.
        chat_history = []

        while True:
            # Get user input from the command line.
            user_input = input("\nYou: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Assistant: Goodbye!")
                break

            # Append the user's message to the history.
            chat_history.append({'role': 'user', 'content': user_input})
            
            # Run the agent with the updated history.
            final_response = None
            response_stream = run_agent_with_dynamic_prompt(chat_history)
            
            print("Assistant: ", end="", flush=True)
            for response in response_stream:
                # The final response object holds the complete message.
                final_response = response
                # Print the content stream for a "typing" effect
                # Note: This part needs more logic to print deltas, for now we just print the final message.
                pass # We will accumulate and print the final message at the end of the stream.
            
            # After the stream is complete, process the final response.
            if final_response:
                # The agent's final text response is the last message in the list.
                assistant_message = final_response[-1] 
                print(assistant_message['content'])
                # Add the full agent response (including tool calls and final text) to history
                chat_history.extend(final_response)
            else:
                print("I'm sorry, I encountered an error and couldn't process your request.")
