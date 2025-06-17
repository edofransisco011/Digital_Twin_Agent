# digital_twin_agent/tools/writer_tools.py

import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build

from core.auth import get_google_credentials
from qwen_agent.tools.base import BaseTool

class GmailSenderTool(BaseTool):
    """A tool to send emails using the Gmail API."""
    name = 'gmail_sender'
    description = "Sends an email to a specified recipient with a subject and body."
    parameters = [
        {'name': 'to', 'type': 'string', 'description': 'The email address of the recipient.', 'required': True},
        {'name': 'subject', 'type': 'string', 'description': 'The subject of the email.', 'required': True},
        {'name': 'body', 'type': 'string', 'description': 'The main content/body of the email.', 'required': True}
    ]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
        print("Gmail Sender tool initialized successfully.")

    def call(self, params: str, **kwargs) -> str:
        try:
            params_dict = self._parse_params(params)
            to = params_dict.get('to')
            subject = params_dict.get('subject')
            body = params_dict.get('body')

            if not all([to, subject, body]):
                return '{"error": "Missing required parameters: to, subject, or body."}'

            print(f"Tool Action: Sending email to {to}...")

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {'raw': encoded_message}
            send_message = self.service.users().messages().send(userId="me", body=create_message).execute()
            
            return f'{{"status": "success", "message_id": "{send_message["id"]}"}}'

        except Exception as e:
            print(f"[Error in GmailSenderTool]: {e}")
            return f'{{"error": "An error occurred while sending the email: {str(e)}"}}'
    
    def _parse_params(self, params: str) -> dict:
        import json
        try:
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}


class CalendarCreatorTool(BaseTool):
    """A tool to create events in Google Calendar."""
    name = 'calendar_event_creator'
    description = "Creates a new event in the user's Google Calendar."
    parameters = [
        {'name': 'summary', 'type': 'string', 'description': 'The title or summary of the event.', 'required': True},
        {'name': 'start_time', 'type': 'string', 'description': 'The event start time in ISO 8601 format (e.g., 2025-06-18T10:00:00).', 'required': True},
        {'name': 'end_time', 'type': 'string', 'description': 'The event end time in ISO 8601 format (e.g., 2025-06-18T11:00:00).', 'required': True},
        {'name': 'description', 'type': 'string', 'description': 'A description for the event.', 'required': False}
    ]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('calendar', 'v3', credentials=creds)
        print("Calendar Creator tool initialized successfully.")

    def call(self, params: str, **kwargs) -> str:
        try:
            params_dict = self._parse_params(params)
            event = {
                'summary': params_dict.get('summary'),
                'start': {'dateTime': params_dict.get('start_time'), 'timeZone': 'UTC'},
                'end': {'dateTime': params_dict.get('end_time'), 'timeZone': 'UTC'},
                'description': params_dict.get('description', ''),
            }

            if not all([event['summary'], event['start']['dateTime'], event['end']['dateTime']]):
                 return '{"error": "Missing required parameters: summary, start_time, or end_time."}'

            print(f"Tool Action: Creating calendar event '{event['summary']}'...")
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return f'{{"status": "success", "event_link": "{created_event.get("htmlLink")}"}}'

        except Exception as e:
            print(f"[Error in CalendarCreatorTool]: {e}")
            return f'{{"error": "An error occurred while creating the calendar event: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        import json
        try:
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}