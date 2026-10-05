import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json",
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "token.json",
)

CALENDAR_ID = (
    "3d4083e870efbb515d143e0a71219f9ef309354e689aa529b185235a14f587a8"
    "@group.calendar.google.com"
)

CALENDAR_TIMEZONE = "America/Denver"


def get_calendar_service():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        credentials = (
            Credentials.from_authorized_user_file(
                TOKEN_FILE,
                SCOPES,
            )
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(
                Request()
            )
        else:
            flow = (
                InstalledAppFlow
                .from_client_secrets_file(
                    CREDENTIALS_FILE,
                    SCOPES,
                )
            )

            credentials = (
                flow.run_local_server(
                    port=0
                )
            )

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8",
        ) as token:
            token.write(
                credentials.to_json()
            )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )


def build_event_body(
    classification,
    article_url=None,
    start=None,
    end=None,
    label=None,
):
    event_name = classification[
        "event_name"
    ]

    if label:
        summary = (
            f"{event_name} — {label}"
        )
    else:
        summary = event_name

    description = classification.get(
        "primary_subject",
        "",
    )

    if article_url:
        description += (
            f"\n\nOfficial Pokémon GO article:\n"
            f"{article_url}"
        )

    event = {
        "summary": summary,
        "start": {
            "dateTime": (
                start
                or classification["start"]
            ),
            "timeZone": CALENDAR_TIMEZONE,
        },
        "end": {
            "dateTime": (
                end
                or classification["end"]
            ),
            "timeZone": CALENDAR_TIMEZONE,
        },
        "description": description,
    }

    locations = classification.get(
        "locations",
        [],
    )

    if locations:
        event["location"] = ", ".join(
            locations
        )

    return event


def create_event(
    classification,
    article_url=None,
    start=None,
    end=None,
    label=None,
):
    service = get_calendar_service()

    event = build_event_body(
        classification,
        article_url=article_url,
        start=start,
        end=end,
        label=label,
    )

    result = (
        service.events()
        .insert(
            calendarId=CALENDAR_ID,
            body=event,
            sendUpdates="all",
        )
        .execute()
    )

    return result["id"]


def update_event(
    calendar_event_id,
    classification,
    article_url=None,
    start=None,
    end=None,
    label=None,
):
    service = get_calendar_service()

    event = build_event_body(
        classification,
        article_url=article_url,
        start=start,
        end=end,
        label=label,
    )

    result = (
        service.events()
        .update(
            calendarId=CALENDAR_ID,
            eventId=calendar_event_id,
            body=event,
            sendUpdates="all",
        )
        .execute()
    )

    return result["id"]


def delete_event(calendar_event_id):
    service = get_calendar_service()

    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=calendar_event_id,
        sendUpdates="all",
    ).execute()


def get_event(calendar_event_id):
    service = get_calendar_service()

    return (
        service.events()
        .get(
            calendarId=CALENDAR_ID,
            eventId=calendar_event_id,
        )
        .execute()
    )