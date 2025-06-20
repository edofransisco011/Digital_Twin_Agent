# digital_twin_agent/api/main.py

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Import the core agent runner function from our existing module.
# This allows us to reuse all the agent logic we've already built.
from core.agent import run_agent_with_dynamic_prompt

# --- Pydantic Models for Data Validation ---
# These models define the expected structure for our API requests and responses.
# FastAPI uses them to validate incoming data, serialize outgoing data, and auto-generate documentation.

class ChatMessage(BaseModel):
    """Represents a single message in the chat history."""
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant').")
    content: str = Field(..., description="The text content of the message.")

class ChatRequest(BaseModel):
    """The structure of a request to the /chat endpoint."""
    message: str = Field(..., description="The new message from the user.")
    history: List[Dict[str, Any]] = Field([], description="The previous conversation history.")

class ChatResponse(BaseModel):
    """The structure of a response from the /chat endpoint."""
    reply: str = Field(..., description="The agent's final text response.")
    history: List[Dict[str, Any]] = Field(..., description="The updated conversation history.")

# --- Initialize FastAPI Application ---
app = FastAPI(
    title="Digital Twin AI Assistant API",
    description="API for interacting with a proactive, personalized AI assistant.",
    version="1.0.0"
)

# --- API Endpoint Definition ---
@app.post("/chat", response_model=ChatResponse, tags=["Agent Interaction"])
def chat_with_agent(request: ChatRequest):
    """
    Receives a user message and conversation history, runs the agent,
    and returns the agent's response along with the updated history.
    """
    print(f"Received chat request: {request.message}")

    # The conversation history is passed directly from the request.
    chat_history = request.history
    
    # Append the new user message to the history.
    chat_history.append({'role': 'user', 'content': request.message})
    
    # Run the agent with the updated history.
    final_response_list = None
    response_stream = run_agent_with_dynamic_prompt(chat_history)
    
    for response in response_stream:
        # The last item in the stream is the complete response list.
        final_response_list = response
    
    if final_response_list:
        # The agent's final text reply is the last message in the list.
        assistant_reply = final_response_list[-1]['content']
        
        # Add the agent's full turn (including tool calls) to the history.
        chat_history.extend(final_response_list)
        
        return ChatResponse(reply=assistant_reply, history=chat_history)
    else:
        # Handle cases where the agent might fail
        return ChatResponse(
            reply="I'm sorry, I encountered an error and couldn't process your request.",
            history=chat_history
        )

# --- Root Endpoint for Health Check ---
@app.get("/", tags=["Health Check"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"status": "Digital Twin Assistant API is running"}
