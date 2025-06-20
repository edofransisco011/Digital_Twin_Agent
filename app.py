# digital_twin_agent/app.py

import gradio as gr
import requests
import json
from typing import List, Dict, Any, Tuple

# The URL of our running FastAPI backend
FASTAPI_URL = "http://127.0.0.1:8000/chat"

def call_chat_api(message: str, api_history: List[Dict[str, Any]]) -> Tuple[str, List[List[str]], List[Dict[str, Any]]]:
    """
    Makes a POST request to the FastAPI backend to get the agent's response.
    Correctly handles complex histories involving tool calls for display.
    """
    if not message or not message.strip():
        # On page load, just format the existing history for display.
        display_history = format_history_for_display(api_history)
        return "", display_history, api_history

    # Prepare the request payload
    payload = {
        "message": message,
        "history": api_history
    }
    
    try:
        response = requests.post(FASTAPI_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # The API returns the full updated history. This is our new source of truth.
        updated_api_history = data.get("history", [])
        
        # Reformat the entire new history for display in the Gradio chatbot.
        display_history = format_history_for_display(updated_api_history)
        
        return "", display_history, updated_api_history

    except requests.exceptions.RequestException as e:
        print(f"Error calling FastAPI backend: {e}")
        error_message = f"Error: Could not connect to the backend at {FASTAPI_URL}. Please ensure the FastAPI server is running."
        
        # Format existing history and append the error message for display
        display_history = format_history_for_display(api_history)
        display_history.append([message, error_message])

        return "", display_history, api_history

def format_history_for_display(api_history: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Converts the API's detailed history (including tool calls) into the
    simple [user, assistant] list format required by Gradio's Chatbot.
    """
    display_history = []
    current_user_message = None
    
    for turn in api_history:
        role = turn.get("role")
        content = turn.get("content", "")
        
        if role == "user":
            # If there was a previous user message without an assistant reply, log it.
            if current_user_message is not None:
                display_history.append([current_user_message, None])
            current_user_message = content
        
        elif role == "assistant":
            # We only pair with the assistant's final text content, ignoring tool calls.
            if content and current_user_message is not None:
                display_history.append([current_user_message, content])
                current_user_message = None # Reset after pairing.

    # If the last message was from the user, add it to the display history.
    if current_user_message is not None:
        display_history.append([current_user_message, None])
        
    return display_history


# --- Gradio Interface Definition ---

with gr.Blocks(theme=gr.themes.Soft(), title="Digital Twin Assistant") as demo:
    # State variable to store the conversation history in the API's format
    api_history = gr.State([])

    gr.Markdown(
        """
        # Digital Twin AI Personal Assistant
        Chat with your proactive AI assistant. Try asking about your schedule, your unread emails, or ask it to draft a reply.
        """
    )

    chatbot = gr.Chatbot(label="Conversation", height=600)

    with gr.Row():
        txt_message = gr.Textbox(
            label="Your Message",
            placeholder="Type your message here and press Enter...",
            scale=4,
        )
        btn_send = gr.Button("Send", variant="primary", scale=1)

    txt_message.submit(
        call_chat_api,
        inputs=[txt_message, api_history],
        outputs=[txt_message, chatbot, api_history],
    )
    btn_send.click(
        call_chat_api,
        inputs=[txt_message, api_history],
        outputs=[txt_message, chatbot, api_history],
    )

# Launch the Gradio web server
if __name__ == "__main__":
    demo.launch()
