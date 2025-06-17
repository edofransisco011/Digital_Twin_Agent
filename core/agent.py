# digital_twin_agent/core/agent.py

import os
import datetime
import pprint
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
from tools.calendar_tools import GoogleCalendarTool
from tools.email_tools import GmailTool
from tools.style_retriever_tool import StyleRetrieverTool
from tools.writer_tools import GmailSenderTool, CalendarCreatorTool # Import writer tools

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
# The instructions now include a safety protocol for write actions.
system_prompt_template = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You have access to read-only tools (`google_calendar_reader`, `gmail_reader`, `style_retriever`) "
    "and write-action tools (`gmail_sender`, `calendar_event_creator`).\n"
    "SAFETY PROTOCOL: For any task that requires a write-action tool "
    "(sending an email, creating an event), you MUST first present your plan and the parameters for the tool. "
    "Then, you MUST ask for confirmation by ending your response with the exact phrase 'Shall I proceed? [y/n]'. "
    "DO NOT call the write-action tool until the user responds with 'y' or 'yes'."
    "Current date: {current_date}"
)

# --- Initialize Tools ---
print("Initializing tools...")
calendar_tool = GoogleCalendarTool()
gmail_tool = GmailTool()
style_tool = StyleRetrieverTool()
gmail_sender_tool = GmailSenderTool()
calendar_creator_tool = CalendarCreatorTool()
print("Tools initialized successfully.")

# --- Initialize the Assistant Agent ---
digital_twin = Assistant(
    llm=llm_config,
    function_list=[
        calendar_tool, gmail_tool, style_tool, 
        gmail_sender_tool, calendar_creator_tool
    ] 
)

def run_agent_with_dynamic_prompt(messages: list) -> list:
    """Injects the current date into the system prompt before running the agent."""
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
        print("Try asking me to 'send an email to test@example.com'.")
        print("Type 'quit' or 'exit' to end the conversation.")
        
        chat_history = []
        last_assistant_response = ""

        while True:
            user_input = input("\nYou: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Assistant: Goodbye!")
                break
            
            # If the last response was a confirmation request and user says 'y',
            # instruct the agent to proceed.
            if "Shall I proceed? [y/n]" in last_assistant_response and user_input.lower() in ['y', 'yes']:
                chat_history.append({'role': 'user', 'content': 'Yes, please proceed with the planned action.'})
            else:
                chat_history.append({'role': 'user', 'content': user_input})
            
            final_response = None
            response_stream = run_agent_with_dynamic_prompt(chat_history)
            
            print("Assistant: ", end="", flush=True)
            for response in response_stream:
                final_response = response
            
            if final_response:
                assistant_message = final_response[-1]
                last_assistant_response = assistant_message['content']
                print(last_assistant_response)
                chat_history.extend(final_response)
            else:
                print("I'm sorry, I encountered an error.")
                last_assistant_response = ""
