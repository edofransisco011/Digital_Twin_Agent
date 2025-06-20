# digital_twin_agent/tools/email_tools.py

import base64
import re
from googleapiclient.discovery import build

from core.auth import get_google_credentials
from qwen_agent.tools.base import BaseTool
from core.vector_store_manager import VectorStoreManager

class GmailTool(BaseTool):
    """A synchronous tool for reading from the Gmail API."""
    name = 'gmail_reader'
    description = 'Retrieves the sender and subject of recent unread emails.'
    parameters = []

    def __init__(self, cfg=None):
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
        self.vector_store = VectorStoreManager()
        print("Gmail tool initialized successfully.")

    def call(self, params: str = None, **kwargs) -> str:
        """The main synchronous method executed by the agent."""
        try:
            print("Tool Action: Fetching unread emails...")
            results = self.service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
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
            return f'{{"error": "An error occurred: {str(e)}"}}'

    # The ingestion logic remains synchronous as it's a one-off script
    def ingest_sent_emails(self, max_emails=50):
        print(f"Starting ingestion of up to {max_emails} sent emails...")
        try:
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
                    body_data = self._find_plain_text_part(payload['parts'])
                    if body_data:
                        text = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        cleaned_text = self._clean_email_text(text)
                        
                        if cleaned_text and len(cleaned_text.split()) > 10:
                            documents_to_add.append(cleaned_text)
                            ids_to_add.append(msg['id'])
                
                print(f"Processed email {i+1}/{len(messages)}...")

            self.vector_store.add_documents(documents=documents_to_add, ids=ids_to_add)
            print(f"Ingestion complete. Added {len(documents_to_add)} emails to the knowledge base.")

        except Exception as e:
            print(f"An error occurred during email ingestion: {e}")
    
    def _find_plain_text_part(self, parts):
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                return part['body']['data']
            if 'parts' in part:
                result = self._find_plain_text_part(part['parts'])
                if result:
                    return result
        return None

    def _clean_email_text(self, text: str) -> str:
        text = re.split(r'\n>|On .* wrote:', text)[0]
        text = text.split('-- \n')[0]
        return text.strip()
