# digital_twin_agent/tools/email_tools.py

from googleapiclient.discovery import build

# Import our custom authentication function and the base tool class
from core.auth import get_google_credentials
from qwen_agent.tools.base import BaseTool

class GmailTool(BaseTool):
    """
    A tool for interacting with the Gmail API.
    """
    name = 'gmail_reader'
    description = (
        'Retrieves the sender and subject of recent unread emails to provide a summary of the inbox.'
    )
    # This tool doesn't require any input parameters from the LLM.
    parameters = []

    def __init__(self, cfg=None):
        """
        Initializes the tool by getting authenticated credentials and building
        the Gmail API service client.
        """
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
        print("Gmail tool initialized successfully.")

    def call(self, params: str = None, **kwargs) -> str:
        """
        The main method executed when the tool is called.
        Fetches a list of recent unread emails.
        """
        try:
            print("Tool Action: Fetching unread emails...")
            # Get a list of unread message IDs. 'is:unread' is a Gmail query.
            # We limit to 10 results for a concise summary.
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
                
                # Extract subject and sender from the email headers
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Format the sender's name for readability
                sender_name = sender.split('<')[0].strip()
                
                email_summaries.append(f"From: {sender_name}, Subject: {subject}")

            return f'{{"status": "{len(email_summaries)} unread emails found.", "summary": "{"; ".join(email_summaries)}"}}'

        except Exception as e:
            print(f"[Error in GmailTool]: {e}")
            return f'{{"error": "An error occurred while accessing the Gmail API: {str(e)}"}}'
