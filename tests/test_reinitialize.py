import unittest
from unittest.mock import Mock, call, patch

import google_calendar
import pokemon_go


class DeleteAllEventsTests(unittest.TestCase):
    def test_deletes_events_across_all_pages(self):
        service = Mock()
        events_api = service.events.return_value
        events_api.list.side_effect = [
            Mock(
                execute=Mock(
                    return_value={
                        "items": [
                            {"id": "event-1"},
                            {"id": "event-2"},
                        ],
                        "nextPageToken": "next-page",
                    }
                )
            ),
            Mock(
                execute=Mock(
                    return_value={
                        "items": [{"id": "event-3"}],
                    }
                )
            ),
        ]

        with patch.object(
            google_calendar,
            "get_calendar_service",
            return_value=service,
        ):
            deleted_count = google_calendar.delete_all_events()

        self.assertEqual(deleted_count, 3)
        self.assertEqual(
            events_api.list.call_args_list,
            [
                call(
                    calendarId=google_calendar.CALENDAR_ID,
                    maxResults=2500,
                    pageToken=None,
                ),
                call(
                    calendarId=google_calendar.CALENDAR_ID,
                    maxResults=2500,
                    pageToken="next-page",
                ),
            ],
        )
        self.assertEqual(
            events_api.delete.call_args_list,
            [
                call(
                    calendarId=google_calendar.CALENDAR_ID,
                    eventId="event-1",
                    sendUpdates="all",
                ),
                call(
                    calendarId=google_calendar.CALENDAR_ID,
                    eventId="event-2",
                    sendUpdates="all",
                ),
                call(
                    calendarId=google_calendar.CALENDAR_ID,
                    eventId="event-3",
                    sendUpdates="all",
                ),
            ],
        )


class ReinitializeTests(unittest.TestCase):
    @patch.object(pokemon_go, "save_state")
    @patch.object(pokemon_go, "delete_all_events", return_value=4)
    def test_deletes_calendar_events_before_clearing_state(
        self,
        delete_all_events,
        save_state,
    ):
        pokemon_go.reinitialize_calendar_and_state()

        delete_all_events.assert_called_once_with()
        save_state.assert_called_once_with(
            {
                "articles": {},
                "events": {},
            }
        )

    @patch.object(pokemon_go, "save_state")
    @patch.object(
        pokemon_go,
        "delete_all_events",
        side_effect=RuntimeError("calendar unavailable"),
    )
    def test_keeps_state_when_calendar_deletion_fails(
        self,
        delete_all_events,
        save_state,
    ):
        with self.assertRaisesRegex(
            RuntimeError,
            "calendar unavailable",
        ):
            pokemon_go.reinitialize_calendar_and_state()

        delete_all_events.assert_called_once_with()
        save_state.assert_not_called()


if __name__ == "__main__":
    unittest.main()
