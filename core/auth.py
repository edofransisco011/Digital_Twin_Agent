# digital_twin_agent/core/auth.py

import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the SCOPES. If you modify them, delete the token.json file.
# These grant full access to calendar and mail.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.modify']

# --- File Paths ---
# Path to the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.pickle') # Changed to .pickle for clarity

def get_google_credentials():
    """
    Handles the user authentication flow for Google APIs.
    - Checks for existing, valid credentials in token.pickle.
    - If credentials are not found or are invalid, it initiates the
      OAuth 2.0 flow, prompting the user for consent via their browser.
    - Saves the new credentials to token.pickle for future runs.
    
    Returns:
        google.oauth2.credentials.Credentials: The authorized credentials object.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("Initiating new user authentication...")
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    "Error: `credentials.json` not found. "
                    "Please download it from the Google Cloud Console and place it in the project's root directory."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            print("Saving credentials to token.pickle...")
            pickle.dump(creds, token)
            
    print("Google API credentials obtained successfully.")
    return creds

if __name__ == '__main__':
    # This block is for testing the authentication flow directly.
    # Running this script will trigger the Google login process if needed.
    print("Running authentication test...")
    get_google_credentials()
    print("Authentication test completed successfully.")
