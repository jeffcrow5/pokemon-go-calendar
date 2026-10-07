import argparse
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

from news import get_news_articles

from classifier import (
    fetch_article,
    classify_article,
    validate_result,
)

from event_filter import extract_event_end

from rules import evaluate_event

from state import (
    load_state,
    save_state,
    get_article_id,
    get_event_id,
    is_article_known,
    get_event,
    record_article,
    set_calendar_event_ids,
)

from google_calendar import (
    create_event,
    update_event,
    delete_event,
    delete_all_events,
)

from gpu_guard import (
    require_system_resources,
)


BASE_DIR = __import__("os").path.dirname(
    __import__("os").path.abspath(__file__)
)

LOG_FILE = __import__("os").path.join(
    BASE_DIR,
    "automation.log",
)


def configure_logging(verbose=False):
    logger = logging.getLogger("pokemon_go")
    logger.setLevel(
        logging.DEBUG if verbose else logging.INFO
    )

    if not any(
        isinstance(handler, RotatingFileHandler)
        for handler in logger.handlers
    ):
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if verbose and not any(
        getattr(handler, "pokemon_go_console", False)
        for handler in logger.handlers
    ):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                "%(levelname)s: %(message)s"
            )
        )
        console_handler.pokemon_go_console = True
        logger.addHandler(console_handler)

    return logger


logger = configure_logging()


def get_calendar_periods(
    classification,
):
    event_periods = classification.get(
        "event_periods",
        [],
    )

    if event_periods:
        return event_periods

    if (
        classification.get("start")
        and classification.get("end")
    ):
        return [
            {
                "start": classification["start"],
                "end": classification["end"],
                "label": None,
            }
        ]

    return []


def reinitialize_calendar_and_state():
    deleted_events = delete_all_events()
    save_state(
        {
            "articles": {},
            "events": {},
        }
    )

    logger.info(
        "REINITIALIZED: deleted %d calendar events and cleared processed state.",
        deleted_events,
    )


def main(reinitialize_first=False, verbose=False):
    configure_logging(verbose=verbose)
    sync_started = datetime.now()

    if reinitialize_first:
        try:
            reinitialize_calendar_and_state()
        except Exception:
            logger.exception(
                "FATAL ERROR DURING REINITIALIZATION."
            )
            return

    try:
        require_system_resources()
    except RuntimeError as exc:
        logger.info(
            "SKIPPING SYNC: %s",
            exc,
        )
        return

    logger.info(
        "Starting Pokémon GO calendar sync."
    )

    try:
        state = load_state()
        articles = get_news_articles()

        current_datetime = datetime.now()

        logger.info(
            "Found %d news links.",
            len(articles),
        )

        new_articles = 0
        skipped_articles = 0
        invited_events = 0
        ignored_events = 0
        cancelled_events = 0
        calendar_created = 0
        calendar_updated = 0
        calendar_deleted = 0

        for article in articles:
            article_id = get_article_id(
                article
            )

            if is_article_known(
                state,
                article_id,
            ):
                skipped_articles += 1
                continue

            new_articles += 1

            article_title = article["title"]

            logger.info(
                "NEW ARTICLE: %s",
                article_title,
            )

            try:
                article_text = fetch_article(
                    article["url"]
                )

                event_end = extract_event_end(
                    article_text
                )

                if (
                    event_end is not None
                    and event_end < current_datetime
                ):
                    logger.info(
                        "SKIPPED ENDED EVENT: %s",
                        article_title,
                    )

                    record_article(
                        state,
                        article,
                        article_id,
                        None,
                        None,
                    )

                    continue

                classification = classify_article(
                    article_text
                )

                validate_result(
                    classification
                )

                event_id = get_event_id(
                    classification
                )

                existing_event = get_event(
                    state,
                    event_id,
                )

                decision = evaluate_event(
                    classification
                )

                action = decision["action"]

                event_name = (
                    classification.get(
                        "event_name"
                    )
                    or article_title
                )

                logger.info(
                    "CLASSIFIED: %s → %s",
                    event_name,
                    action.upper(),
                )

                calendar_event_ids = []

                if existing_event:
                    calendar_event_ids = (
                        existing_event.get(
                            "calendar_event_ids",
                            [],
                        )
                    )

                if action == "invite":
                    invited_events += 1

                    calendar_periods = (
                        get_calendar_periods(
                            classification
                        )
                    )

                    if not calendar_periods:
                        logger.info(
                            "INVITE WITHOUT CALENDAR DATES: %s",
                            event_name,
                        )

                    else:
                        new_calendar_event_ids = []

                        for period_index, period in enumerate(
                            calendar_periods
                        ):
                            start = period[
                                "start"
                            ]

                            end = period[
                                "end"
                            ]

                            label = period.get(
                                "label"
                            )

                            existing_calendar_event_id = (
                                None
                            )

                            if period_index < len(
                                calendar_event_ids
                            ):
                                existing_calendar_event_id = (
                                    calendar_event_ids[
                                        period_index
                                    ]
                                )

                            if existing_calendar_event_id:
                                logger.info(
                                    "UPDATING CALENDAR EVENT: %s%s",
                                    event_name,
                                    (
                                        f" ({label})"
                                        if label
                                        else ""
                                    ),
                                )

                                calendar_event_id = (
                                    update_event(
                                        existing_calendar_event_id,
                                        classification,
                                        article_url=article[
                                            "url"
                                        ],
                                        start=start,
                                        end=end,
                                        label=label,
                                    )
                                )

                                calendar_updated += 1

                            else:
                                logger.info(
                                    "CREATING CALENDAR EVENT: %s%s",
                                    event_name,
                                    (
                                        f" ({label})"
                                        if label
                                        else ""
                                    ),
                                )

                                calendar_event_id = (
                                    create_event(
                                        classification,
                                        article_url=article[
                                            "url"
                                        ],
                                        start=start,
                                        end=end,
                                        label=label,
                                    )
                                )

                                calendar_created += 1

                            new_calendar_event_ids.append(
                                calendar_event_id
                            )

                        if len(
                            calendar_event_ids
                        ) > len(
                            new_calendar_event_ids
                        ):
                            for old_calendar_event_id in (
                                calendar_event_ids[
                                    len(
                                        new_calendar_event_ids
                                    ):
                                ]
                            ):
                                logger.info(
                                    "DELETING REMOVED CALENDAR PERIOD: %s",
                                    event_name,
                                )

                                delete_event(
                                    old_calendar_event_id
                                )

                                calendar_deleted += 1

                        calendar_event_ids = (
                            new_calendar_event_ids
                        )

                elif action == "ignore":
                    ignored_events += 1

                    logger.info(
                        "IGNORED: %s",
                        event_name,
                    )

                elif action == "cancel":
                    cancelled_events += 1

                    if calendar_event_ids:
                        for calendar_event_id in (
                            calendar_event_ids
                        ):
                            logger.info(
                                "CANCELLING CALENDAR EVENT: %s",
                                event_name,
                            )

                            delete_event(
                                calendar_event_id
                            )

                            calendar_deleted += 1
                    else:
                        logger.info(
                            "CANCELLATION WITH NO EXISTING CALENDAR EVENT: %s",
                            event_name,
                        )

                    calendar_event_ids = []

                record_article(
                    state,
                    article,
                    article_id,
                    event_id,
                    classification,
                )

                if event_id:
                    set_calendar_event_ids(
                        state,
                        event_id,
                        calendar_event_ids,
                    )

            except Exception:
                logger.exception(
                    "ERROR PROCESSING ARTICLE: %s",
                    article_title,
                )

        save_state(state)

        duration = (
            datetime.now() - sync_started
        ).total_seconds()

        logger.info(
            "SYNC COMPLETE: %d new, %d already processed, "
            "%d invited, %d ignored, %d cancelled.",
            new_articles,
            skipped_articles,
            invited_events,
            ignored_events,
            cancelled_events,
        )

        logger.info(
            "CALENDAR: %d created, %d updated, %d deleted.",
            calendar_created,
            calendar_updated,
            calendar_deleted,
        )

        logger.info(
            "Sync duration: %.1f seconds.",
            duration,
        )

    except Exception:
        logger.exception(
            "FATAL ERROR DURING SYNC."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synchronize Pokémon GO news with Google Calendar."
    )
    parser.add_argument(
        "--reinitialize",
        action="store_true",
        help=(
            "Delete every event in the configured Google Calendar, "
            "clear processed state, then run the sync."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Also print run logs to the console.",
    )
    args = parser.parse_args()
    main(
        reinitialize_first=args.reinitialize,
        verbose=args.verbose,
    )