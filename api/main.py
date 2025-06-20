# digital_twin_agent/api/main.py

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Import the core agent runner function from our existing module.
from core.agent import run_agent_with_dynamic_prompt

# --- Pydantic Models for Data Validation ---
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

# --- Synchronous Helper Function ---
def get_agent_response(chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    This is a synchronous wrapper that runs the agent's generator and returns
    only the final, complete response list. This function will be run in a separate thread.
    """
    final_response_list = None
    # The run method is a synchronous generator, so we use a regular for loop.
    for response in run_agent_with_dynamic_prompt(chat_history):
        final_response_list = response
    return final_response_list

# --- API Endpoint Definition ---
@app.post("/chat", response_model=ChatResponse, tags=["Agent Interaction"])
async def chat_with_agent(request: ChatRequest):
    """
    Receives a user message and conversation history, runs the agent in a separate
    thread to avoid blocking the server, and returns the agent's final response.
    """
    print(f"Received async chat request: {request.message}")

    chat_history = request.history
    chat_history.append({'role': 'user', 'content': request.message})
    
    # Run the blocking, synchronous `get_agent_response` function in a separate thread
    # and wait for its result without blocking the main FastAPI event loop.
    final_response_list = await asyncio.to_thread(get_agent_response, chat_history)
    
    if final_response_list:
        assistant_reply = final_response_list[-1]['content']
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
