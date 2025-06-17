# Digital Twin AI Personal Assistant

This project is a sophisticated, proactive AI personal assistant built using the Qwen Large Language Model and the Qwen-Agent framework. The "Digital Twin" is designed to learn its user's unique communication style and assist with managing their digital life, including emails and calendar schedules.

## Core Features

* **Interactive Chat:** A command-line interface for real-time, conversational interaction with the agent.
* **Persona Learning:** The agent ingests the user's sent emails to learn their specific writing style, tone, and phrasing. This is achieved through Retrieval-Augmented Generation (RAG) with a ChromaDB vector store.
* **Gmail & Calendar Integration:** Securely connects to Google services using OAuth 2.0 to:
    * Read calendar schedules.
    * Summarize unread emails.
    * Draft emails that mimic the user's persona.
    * Send emails and create calendar events with user confirmation.
* **Proactive Assistance:** A dedicated mode where the agent analyzes the user's current context (new emails and events) to suggest actions, such as scheduling a meeting mentioned in an email.
* **Safety First:** Implements a strict confirmation protocol. The agent will always ask for user permission before taking any write-action (sending an email, creating an event).

## Technical Architecture

* **LLM Framework:** `qwen-agent`
* **Core LLM:** `qwen-max` (or other powerful model) via Alibaba Cloud
* **Vector Database:** ChromaDB for local, persistent persona storage
* **Embeddings:** `sentence-transformers`
* **API Authentication:** Google OAuth 2.0 for secure service access

*Create a simple diagram showing how the Agent, Tools, and Vector DB interact, and add it here.*

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd digital_twin_agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Google Cloud & API Keys:**
    * Follow the Google Cloud setup instructions to enable the Gmail and Calendar APIs and download your `credentials.json` file. Place it in the project root.
    * Create a `.env` file in the project root and add your Model Studio API credentials:
        ```env
        MODEL_STUDIO_URL="your_model_studio_api_endpoint_url_here"
        MODEL_STUDIO_API_KEY="your_model_studio_api_key_here"
        ```

## How to Use the Digital Twin

**Step 1: First-Time Authentication**

Run the `auth.py` script once to authorize the application with your Google account. This will open a browser window for you to log in and consent.

```bash
python -m core.auth
```

**Step 2: Learn Your Persona**

Run the ingestion script once to populate the vector database with your writing style from your 50 most recent sent emails.

```bash
python run_ingestion.py
```

**Step 3: Interact with Your Agent**

Start the interactive chat loop to talk to your assistant.

```bash
python -m core.agent
```

You can ask things like:
* "What's on my schedule for tomorrow?"
* "Any new emails?"
* "Draft an email to my colleague about the project deadline."
* "Send an email to test@example.com..." (will ask for confirmation)

**Step 4: Get Proactive Suggestions**

Run the proactive script to have the agent analyze your current situation and suggest actions.

```bash
python run_proactive_assistant.py
```
