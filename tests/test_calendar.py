from google_calendar import create_event, delete_event


TEST_CLASSIFICATION = {
    "event_name": "Pokémon GO Calendar Test",
    "primary_subject": "Calendar integration test",
    "start": "2026-10-10T10:00:00",
    "end": "2026-10-10T11:00:00",
    "locations": [],
}


def main():
    print("Creating test Calendar event...")

    event_id = create_event(TEST_CLASSIFICATION)

    print()
    print(f"Created event: {event_id}")
    print()
    print("The test event should now appear on your Pokémon GO Events calendar.")
    print()
    print("Delete the test event?")

    answer = input("Enter Y to delete it, or anything else to keep it: ")

    if answer.strip().lower() == "y":
        delete_event(event_id)
        print("Test event deleted.")
    else:
        print(f"Test event left in Calendar: {event_id}")


if __name__ == "__main__":
    main()