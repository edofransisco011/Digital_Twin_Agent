# digital_twin_agent/run_proactive_assistant.py

import json
from core.agent import run_agent_with_dynamic_prompt
from tools.email_tools import GmailTool
from tools.calendar_tools import GoogleCalendarTool

def get_current_context():
    """
    Uses the read-only tools to gather the user's current context.
    
    Returns:
        str: A formatted string containing a summary of unread emails and upcoming calendar events.
    """
    print("--- Gathering Proactive Context ---")
    
    # Initialize the tools to fetch data
    gmail_tool = GmailTool()
    calendar_tool = GoogleCalendarTool()
    
    # Fetch data from tools
    email_data_str = gmail_tool.call()
    calendar_data_str = calendar_tool.call(params='{}')
    
    # Parse the JSON strings
    email_data = json.loads(email_data_str)
    calendar_data = json.loads(calendar_data_str)
    
    # Build a comprehensive context summary string
    context = "Here is a summary of the user's current situation:\n\n"
    context += f"Unread Emails: {email_data.get('summary', 'None')}\n"
    context += f"Today's Schedule: {calendar_data.get('schedule', 'None')}\n"
    
    print("Context gathering complete.")
    return context

def main():
    """
    Main function to run the proactive agent loop.
    """
    print("\n--- Running Proactive Digital Twin Assistant ---")
    
    # 1. Gather the current context
    current_context = get_current_context()
    
    # 2. Define the high-level proactive prompt
    proactive_prompt = (
        "You are in PROACTIVE mode. Here is the user's current context:\n"
        f"{current_context}\n"
        "Analyze this information for potential actions. If you identify a necessary action "
        "that requires a write-action tool, formulate a plan, present the tool you would use "
        "and the exact parameters, and ask for permission by ending your response with the "
        "exact phrase 'Shall I proceed? [y/n]'. If no actions are needed, "
        "simply state that everything looks clear."
    )
    
    # 3. Prepare the message history for the agent
    messages = [{'role': 'user', 'content': proactive_prompt}]
    
    # 4. Run the agent to get its analysis and plan
    print("\n--- Agent is now thinking proactively... ---")
    final_response = None
    response_stream = run_agent_with_dynamic_prompt(messages)
    
    for response in response_stream:
        final_response = response
        
    # 5. Print the agent's proposed plan and handle confirmation
    print("\n--- Proactive Suggestions ---")
    if final_response:
        # Add the agent's suggestion to the conversation history
        messages.extend(final_response)
        assistant_message = final_response[-1]['content']
        print(assistant_message)
        
        # Check if confirmation is required and start an input loop
        if "Shall I proceed? [y/n]" in assistant_message:
            user_confirmation = input("\nConfirm Action [y/n]: ")
            if user_confirmation.lower() in ['y', 'yes']:
                # If confirmed, tell the agent to execute its plan
                print("\n--- Executing Action ---")
                confirmation_prompt = "Yes, please proceed with the planned action."
                messages.append({'role': 'user', 'content': confirmation_prompt})
                
                # Run the agent again with the confirmation message
                execution_response = None
                execution_stream = run_agent_with_dynamic_prompt(messages)
                for response in execution_stream:
                    execution_response = response
                
                if execution_response:
                    execution_result = execution_response[-1]['content']
                    print(f"Agent Execution Result: {execution_result}")
            else:
                print("Action cancelled by user.")
    else:
        print("The agent did not produce a plan.")

if __name__ == '__main__':
    main()
