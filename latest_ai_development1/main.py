from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Define the Google Calendar Tool that schedules events
class GoogleCalendarTool(BaseTool):
    name: str = "Google Calendar"
    description: str = "Creates events in Google Calendar"

    def _run(self) -> str:
        # OAuth 2.0 flow: Obtain credentials (refresh if necessary)
        creds = None
        if os.path.exists('token.json'):  # Check if the token already exists
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])

        # If no valid credentials are available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # Refresh the credentials using Request()
                    print("Token refreshed successfully.")
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    return "Failed to refresh token. Please authenticate again."
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'latest_ai_development/src/latest_ai_development/credentials/credentials.json',  # This is where you specify your 'credentials.json' file
                        ['https://www.googleapis.com/auth/calendar']
                    )
                    creds = flow.run_local_server(port=0)  # Run local server for authentication
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return "Authentication failed. Please check your credentials."

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        # Ask user for event details
        summary = input("Enter event summary (title): ")
        location = input("Enter event location: ")
        description = input("Enter event description: ")
        start_date = input("Enter event start date (YYYY-MM-DD): ")
        start_time = input("Enter event start time (HH:MM, 24-hour format): ")
        end_date = input("Enter event end date (YYYY-MM-DD): ")
        end_time = input("Enter event end time (HH:MM, 24-hour format): ")
        attendee_email = input("Enter attendee's email address: ")

        # Format the start and end datetime
        start_datetime = f"{start_date}T{start_time}:00"
        end_datetime = f"{end_date}T{end_time}:00"

        # Create the event dictionary based on user input
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/Los_Angeles',
            },
            'attendees': [
                {'email': attendee_email}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # Reminder 24 hours before event
                    {'method': 'popup', 'minutes': 10},       # Popup reminder 10 minutes before event
                ],
            },
        }

        # Initialize the Google Calendar API client
        try:
            service = build('calendar', 'v3', credentials=creds)

            # Insert the event into the Google Calendar
            created_event = service.events().insert(calendarId='primary', body=event).execute()

            # Return the link to the created event
            return f"Event created: {created_event['htmlLink']}"
        except Exception as e:
            print(f"Error creating event: {e}")
            return "An error occurred while creating the event."

# Define the Calendar Agent
calendar_agent = Agent(
    role='Calendar Manager',
    goal='Schedule appointments in Google Calendar',
    backstory="You are an efficient calendar manager, responsible for scheduling appointments.",
    tools=[GoogleCalendarTool()],
    verbose=True
)

# Define the task for scheduling an appointment
schedule_task = Task(
    description="Schedule an appointment in Google Calendar using user input for event details.",
    agent=calendar_agent,
    expected_output="The event link will be returned after creating the event."
)

# Define the Crew instance that will manage the task and agents
crew = Crew(
    agents=[calendar_agent],
    tasks=[schedule_task],
    verbose=True
)

# Run the task to kickoff the appointment scheduling
result = crew.kickoff()
print(result)  # Output the result from the crew's execution

