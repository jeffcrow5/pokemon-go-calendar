from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = "3d4083e870efbb515d143e0a71219f9ef309354e689aa529b185235a14f587a8@group.calendar.google.com"


def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("calendar", "v3", credentials=creds)


def main():
    service = get_calendar_service()

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=1)

    event = {
        "summary": "🧪 TEST — Pokémon GO Calendar Automation",
        "description": "This is a test event created by the Pokémon GO calendar automation.",
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "UTC",
        },
    }

    created = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
    ).execute()

    print("Successfully created test event!")
    print(f"Event ID: {created['id']}")
    print(f"Link: {created.get('htmlLink')}")


if __name__ == "__main__":
    main()