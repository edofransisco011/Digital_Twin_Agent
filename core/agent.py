# digital_twin_agent/core/agent.py

import os
import datetime
from dotenv import load_dotenv
from qwen_agent.agents import Assistant

# --- Custom Tool Imports ---
from tools.calendar_tools import GoogleCalendarTool
from tools.email_tools import GmailTool
from tools.style_retriever_tool import StyleRetrieverTool
from tools.writer_tools import GmailSenderTool, CalendarCreatorTool
from tools.content_retriever_tool import ContentRetrieverTool # Import new tool

# --- Load Environment Variables ---
load_dotenv()

# --- Configure the Language Model (LLM) ---
llm_config = {
    'model_server': os.getenv('MODEL_STUDIO_URL'),
    'api_key': os.getenv('MODEL_STUDIO_API_KEY'),
    'model': 'qwen-max', 
    'generate_cfg': {'top_p': 0.8}
}

# --- Define the BASE System Prompt ---
# The instructions now include guidance on using the new content retrieval tool.
system_prompt_template = (
    "You are a highly capable AI personal assistant, a 'Digital Twin'. "
    "Your primary goal is to learn from the user's data and communication style to assist them proactively. "
    "You have access to read-only tools (`google_calendar_reader`, `gmail_reader`, `style_retriever`, `email_content_retriever`) "
    "and write-action tools (`gmail_sender`, `calendar_event_creator`).\n"
    "GUIDELINES:\n"
    "1. For questions about your inbox status, use `gmail_reader`.\n"
    "2. For questions about the CONTENT of past emails (e.g., 'what did X say about Y'), use `email_content_retriever`.\n"
    "3. To DRAFT an email, you MUST first use `style_retriever` to get style examples.\n"
    "4. SAFETY: For any write-action tool, you MUST present your plan and ask 'Shall I proceed? [y/n]' before acting.\n\n"
    "Current date: {current_date}"
)

# --- Initialize Tools ---
print("Initializing tools...")
calendar_tool = GoogleCalendarTool()
gmail_tool = GmailTool()
style_tool = StyleRetrieverTool()
content_tool = ContentRetrieverTool() # Create instance of new tool
gmail_sender_tool = GmailSenderTool()
calendar_creator_tool = CalendarCreatorTool()
print("Tools initialized successfully.")

# --- Initialize the Assistant Agent ---
digital_twin = Assistant(
    llm=llm_config,
    function_list=[
        calendar_tool, gmail_tool, style_tool, content_tool,
        gmail_sender_tool, calendar_creator_tool
    ] 
)

def run_agent_with_dynamic_prompt(messages: list) -> list:
    """Injects the current date into the system prompt before running the agent."""
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    dynamic_system_prompt = system_prompt_template.format(current_date=today_str)
    digital_twin.system_message = dynamic_system_prompt
    return digital_twin.run(messages=messages)

# This file is now primarily a library. The main execution points are app.py and run_proactive_assistant.py.
if __name__ == '__main__':
    print("This script contains the core agent logic and is intended to be imported, not run directly.")
    print("To chat with the agent, please run 'python app.py'.")

