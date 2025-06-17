# digital_twin_agent/tools/calendar_tools.py

import datetime
import dateutil.parser
from googleapiclient.discovery import build

# Import our custom authentication function
from core.auth import get_google_credentials
# Import the base class for creating tools
from qwen_agent.tools.base import BaseTool

class GoogleCalendarTool(BaseTool):
    """
    A tool for interacting with the Google Calendar API.
    """
    # A descriptive name for the tool.
    name = 'google_calendar_reader'
    
    # A detailed description for the LLM. This is VERY important.
    # It tells the LLM what this tool can do, when to use it, and what kind of
    # questions it can answer. The more descriptive, the better the agent's reasoning.
    description = (
        'Retrieves Google Calendar events for a specified date to answer questions about '
        'schedules, appointments, meetings, and plans. If no date is mentioned, '
        'it defaults to today.'
    )
    
    # Defines the input parameters for the tool's `call` method.
    # The LLM will use this schema to structure its function call.
    parameters = [{
        'name': 'date',
        'type': 'string',
        'description': 'The date to retrieve events for, in YYYY-MM-DD format. Defaults to today if not provided.',
        'required': False
    }]

    def __init__(self, cfg=None):
        """
        Initializes the tool by getting authenticated credentials and building
        the Google Calendar API service client.
        """
        super().__init__(cfg)
        # Get authenticated credentials using our auth module
        creds = get_google_credentials()
        # Build the Google Calendar API service
        self.service = build('calendar', 'v3', credentials=creds)
        print("Google Calendar tool initialized successfully.")

    def call(self, params: str, **kwargs) -> str:
        """
        The main method that gets executed when the tool is called by the agent.
        
        **kwargs is added to accept any extra arguments passed by the agent framework,
        preventing a TypeError.
        """
        try:
            # The qwen-agent framework passes params as a string, so we parse it.
            params_dict = self._parse_params(params)
            date_str = params_dict.get('date')

            if date_str:
                # If a date is provided, parse it.
                target_date = dateutil.parser.isoparse(date_str).date()
            else:
                # Otherwise, default to today.
                target_date = datetime.date.today()

            # Define the time range for the entire day (from start to end in UTC)
            time_min = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + 'Z'
            time_max = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + 'Z'

            print(f"Tool Action: Fetching calendar events for {target_date.strftime('%Y-%m-%d')}...")

            # Call the Calendar API to get the event list
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=time_min,
                timeMax=time_max,
                maxResults=20, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if not events:
                return f'{{"events": "No upcoming events found on {target_date.strftime("%Y-%m-%d")}."}}'

            # Format the events into a clean string for the LLM to summarize
            event_list = []
            for event in events:
                start_time_data = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = dateutil.parser.isoparse(start_time_data)
                
                # Format time for readability, handle all-day events
                start_formatted = start_dt.strftime('%I:%M %p') if start_dt.time() else 'All-day'
                
                summary = event.get('summary', 'No Title')
                event_list.append(f"- {start_formatted}: {summary}")

            # Return a structured string result
            return f'{{"events": "{len(event_list)} events scheduled", "schedule": "{"; ".join(event_list)}"}}'

        except Exception as e:
            print(f"[Error in GoogleCalendarTool]: {e}")
            return f'{{"error": "An error occurred while accessing the Google Calendar API: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        """A simple helper to parse the string-based parameters."""
        try:
            # Assumes params like '{"date": "2023-10-27"}'
            import json
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            # If params are not a valid JSON string, return an empty dict
            return {}