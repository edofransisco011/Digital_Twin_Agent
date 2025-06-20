# digital_twin_agent/tools/calendar_tools.py

import datetime
import dateutil.parser
from googleapiclient.discovery import build

from core.auth import get_google_credentials
from qwen_agent.tools.base import BaseTool

class GoogleCalendarTool(BaseTool):
    name = 'google_calendar_reader'
    description = (
        'Retrieves Google Calendar events for a specified date to answer questions about '
        'schedules, appointments, meetings, and plans. If no date is mentioned, '
        'it defaults to today.'
    )
    parameters = [{
        'name': 'date',
        'type': 'string',
        'description': 'The date to retrieve events for, in YYYY-MM-DD format.',
        'required': False
    }]

    def __init__(self, cfg=None):
        super().__init__(cfg)
        creds = get_google_credentials()
        self.service = build('calendar', 'v3', credentials=creds)

    def call(self, params: str, **kwargs) -> str:
        try:
            params_dict = self._parse_params(params)
            date_str = params_dict.get('date')
            target_date = dateutil.parser.isoparse(date_str).date() if date_str else datetime.date.today()
            time_min = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + 'Z'
            time_max = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId='primary', timeMin=time_min, timeMax=time_max,
                maxResults=20, singleEvents=True, orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return f'{{"events": "No upcoming events found on {target_date.strftime("%Y-%m-%d")}."}}'

            event_list = [f"- {dateutil.parser.isoparse(event['start'].get('dateTime', event['start'].get('date'))).strftime('%I:%M %p' if event['start'].get('dateTime') else 'All-day')}: {event.get('summary', 'No Title')}" for event in events]
            return f'{{"events": "{len(event_list)} events scheduled", "schedule": "{"; ".join(event_list)}"}}'
        except Exception as e:
            return f'{{"error": "An error occurred: {str(e)}"}}'

    def _parse_params(self, params: str) -> dict:
        import json
        try:
            return json.loads(params)
        except (json.JSONDecodeError, TypeError):
            return {}
