# digital_twin_agent/tools/email_tools.py

from googleapiclient.discovery import build
import base64
import re

# Import our custom modules and the base tool class
from core.auth import get_google_credentials
from qwen_agent.tools.base import BaseTool
from core.vector_store_manager import VectorStoreManager

class GmailTool(BaseTool):
    """
    A tool for interacting with the Gmail API.
    """
    name = 'gmail_reader'
    description = (
        'Retrieves the sender and subject of recent unread emails to provide a summary of the inbox.'
    )
    parameters = []

    def __init__(self, cfg=None):
        """
        Initializes the tool by getting authenticated credentials, building
        the Gmail API service client, and initializing the vector store manager.
        """
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
        # The tool now needs access to the vector store.
        self.vector_store = VectorStoreManager()
        print("Gmail tool initialized successfully.")

    def call(self, params: str = None, **kwargs) -> str:
        """
        The main method executed when the tool is called.
        Fetches a list of recent unread emails.
        """
        try:
            print("Tool Action: Fetching unread emails...")
            results = self.service.users().messages().list(
                userId='me', 
                q='is:unread', 
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])

            if not messages:
                return '{"status": "No unread emails found."}'

            email_summaries = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
                headers = msg['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                sender_name = sender.split('<')[0].strip()
                
                email_summaries.append(f"From: {sender_name}, Subject: {subject}")

            return f'{{"status": "{len(email_summaries)} unread emails found.", "summary": "{"; ".join(email_summaries)}"}}'

        except Exception as e:
            print(f"[Error in GmailTool]: {e}")
            return f'{{"error": "An error occurred while accessing the Gmail API: {str(e)}"}}'

    def ingest_sent_emails(self, max_emails=50):
        """
        Fetches the user's sent emails, processes them, and adds them
        to the vector database to learn the user's writing style.
        This is a one-time operation.
        """
        print(f"Starting ingestion of up to {max_emails} sent emails...")
        try:
            # Get a list of sent message IDs
            sent_messages = self.service.users().messages().list(userId='me', q='in:sent', maxResults=max_emails).execute()
            messages = sent_messages.get('messages', [])
            
            if not messages:
                print("No sent emails found to ingest.")
                return

            documents_to_add = []
            ids_to_add = []

            for i, message in enumerate(messages):
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload')
                if payload and payload.get('parts'):
                    # Find the plain text part of the email
                    body_data = self._find_plain_text_part(payload['parts'])
                    if body_data:
                        # Decode from base64 and clean the text
                        text = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        cleaned_text = self._clean_email_text(text)
                        
                        # Only add non-trivial emails to the database
                        if cleaned_text and len(cleaned_text.split()) > 10:
                            documents_to_add.append(cleaned_text)
                            ids_to_add.append(msg['id'])
                
                print(f"Processed email {i+1}/{len(messages)}...")

            # Add the collected email bodies to the vector store
            self.vector_store.add_documents(documents=documents_to_add, ids=ids_to_add)
            print(f"Ingestion complete. Added {len(documents_to_add)} emails to the knowledge base.")

        except Exception as e:
            print(f"An error occurred during email ingestion: {e}")

    def _find_plain_text_part(self, parts):
        """Recursively finds the plain text body in email parts."""
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                return part['body']['data']
            if 'parts' in part:
                # Recursive call for nested parts
                result = self._find_plain_text_part(part['parts'])
                if result:
                    return result
        return None

    def _clean_email_text(self, text: str) -> str:
        """Performs basic cleaning of email text."""
        # Remove quoted replies
        text = re.split(r'\n>|On .* wrote:', text)[0]
        # Remove signatures
        text = text.split('-- \n')[0]
        # Remove excess newlines and whitespace
        return text.strip()

