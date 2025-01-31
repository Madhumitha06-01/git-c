from datetime import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for accessing calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_upcoming_events():
    """Fetches and displays upcoming events from the user's Google Calendar."""
    creds = None

    # Check for existing credentials
    if os.path.exists('src/email_test/credentials/token.json'):
        creds = Credentials.from_authorized_user_file('src/email_test/credentials/token.json', SCOPES)

    # If no valid credentials, prompt for login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'src/email_test/credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for future runs
        os.makedirs('src/email_test/credentials', exist_ok=True)
        with open('src/email_test/credentials/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Google Calendar API
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming events')
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Display upcoming events
        print("\nUpcoming Events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")

    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    get_upcoming_events()
