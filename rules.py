import json
import math
from pathlib import Path

import requests


RULES_FILE = Path(__file__).resolve().parent / "calendar_rules.json"

GEOCODING_URL = "https://nominatim.openstreetmap.org/search"
GEOCODING_HEADERS = {
    "User-Agent": "PokemonGoCalendar/1.0"
}


def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def geocode_location(location):
    response = requests.get(
        GEOCODING_URL,
        params={
            "q": location,
            "format": "json",
            "limit": 1,
        },
        headers=GEOCODING_HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return float(results[0]["lat"]), float(results[0]["lon"])


def distance_miles(lat1, lon1, lat2, lon2):
    radius_miles = 3958.8

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return radius_miles * 2 * math.asin(math.sqrt(a))


def get_nearest_location_distance(locations, home_coordinates):
    if not locations:
        return None

    if not home_coordinates:
        return None

    home_lat, home_lon = home_coordinates
    distances = []

    for location in locations:
        coordinates = geocode_location(location)

        if coordinates is None:
            continue

        lat, lon = coordinates

        distances.append(
            distance_miles(
                home_lat,
                home_lon,
                lat,
                lon,
            )
        )

    if not distances:
        return None

    return min(distances)


def add_saturday_event(classification):
    start = classification.get("start")
    if not start:
        return

    try:
        from datetime import datetime

        start_date = datetime.fromisoformat(start)
    except ValueError:
        return

    event_types = classification.setdefault("event_types", [])

    # Don't use the generic Saturday rule for event types that
    # already have their own explicit inclusion/exclusion logic.
    excluded_types = {
        "city_safari",
        "regional_event",
        "monthly_go_pass",
        "go_battle_league",
        "battle_event",
        "league_event",
        "cup",
    }

    if (
        start_date.weekday() == 5
        and not any(event_type in excluded_types for event_type in event_types)
        and "saturday_event" not in event_types
    ):
        event_types.append("saturday_event")


def calculate_twitch_end(classification):
    if "twitch_drops" not in classification.get("event_types", []):
        return

    if classification.get("end") is not None:
        return

    watch_requirements = (
        classification
        .get("details", {})
        .get("watch_requirements_minutes", [])
    )

    if not watch_requirements:
        return

    start = classification.get("start")

    if not start:
        return

    try:
        from datetime import datetime, timedelta

        start_datetime = datetime.fromisoformat(start)
    except ValueError:
        return

    maximum_minutes = max(watch_requirements)

    end_datetime = start_datetime + timedelta(
        minutes=maximum_minutes
    )

    classification["end"] = end_datetime.isoformat()


def apply_derived_fields(classification):
    add_saturday_event(classification)
    calculate_twitch_end(classification)


def evaluate_location_rule(
    event_type,
    classification,
    rules,
    home_coordinates,
):
    settings = rules["settings"]

    if event_type == "city_safari":
        maximum_distance = settings["city_safari_max_distance_miles"]
    elif event_type == "regional_event":
        maximum_distance = settings["regional_event_max_distance_miles"]
    else:
        return True, None

    locations = classification.get("locations", [])

    if not locations:
        return False, (
            f"{event_type} has no identifiable location"
        )

    distance = get_nearest_location_distance(
        locations,
        home_coordinates,
    )

    if distance is None:
        return False, (
            f"could not determine distance to {event_type}"
        )

    if distance > maximum_distance:
        return False, (
            f"{event_type} is {distance:.1f} miles away "
            f"(maximum {maximum_distance} miles)"
        )

    return True, (
        f"{event_type} is {distance:.1f} miles away "
        f"(within {maximum_distance} miles)"
    )


def evaluate_event(classification, rules=None):
    if rules is None:
        rules = load_rules()

    apply_derived_fields(classification)

    from datetime import datetime

    now = datetime.now()

    end = classification.get("end")

    if end:
        try:
            end_datetime = datetime.fromisoformat(end)

            if end_datetime < now:
                return {
                    "action": "ignore",
                    "reason": "event has already ended",
                    "classification": classification,
                }
        except ValueError:
            pass

    if classification.get("is_cancellation"):
        return {
            "action": "cancel",
            "reason": "announcement is an event cancellation",
            "classification": classification,
        }

    event_types = classification.get("event_types", [])

    if not event_types:
        return {
            "action": "ignore",
            "reason": "no applicable invite rule",
            "classification": classification,
        }

    home_location = rules["settings"]["home_location"]

    home_location_string = (
        f"{home_location['city']}, "
        f"{home_location['state']}, "
        f"{home_location['country']}"
    )

    home_coordinates = None

    if any(
        event_type in {"city_safari", "regional_event"}
        for event_type in event_types
    ):
        home_coordinates = geocode_location(
            home_location_string
        )

    for event_type in event_types:
        rule = rules.get(event_type, "ignore")

        if rule != "invite":
            continue

        if event_type in {"city_safari", "regional_event"}:
            allowed, reason = evaluate_location_rule(
                event_type,
                classification,
                rules,
                home_coordinates,
            )

            if not allowed:
                continue

            return {
                "action": "invite",
                "reason": reason,
                "classification": classification,
            }

        return {
            "action": "invite",
            "reason": f"{event_type} = invite",
            "classification": classification,
        }

    return {
        "action": "ignore",
        "reason": "no applicable invite rule",
        "classification": classification,
    }