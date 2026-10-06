EVENT_TYPES = [
    "raid_day",
    "max_battle_day",
    "gigantamax_max_battle_day",
    "dynamax_max_battle_day",
    "mega_raid_day",
    "super_mega_raid_day",
    "shadow_raid_day",
    "elite_raid_day",
    "community_day",
    "community_day_classic",
    "community_day_makeup",
    "spotlight_hour",
    "raid_hour",
    "raid_rotation",
    "raid_boss_rotation",
    "gbl_season_update",
    "gbl_update",
    "monthly_go_pass",
    "weekly_go_pass",
    "weekly_event",
    "go_tour",
    "go_fest",
    "go_wild_area",
    "twitch_drops",
    "code_distribution",
    "hatch_day",
    "research_day",
    "battle_day",
    "saturday_event",
    "city_safari",
    "regional_event",
    "season",
    "seasonal_event",
    "global_event",
    "pokemon_debut",
    "shiny_debut",
    "costume_pokemon_event",
    "special_background_event",
    "timed_research",
    "special_research",
    "field_research_event",
    "collection_challenge",
    "go_battle_league",
    "battle_event",
    "league_event",
    "cup",
    "safari_zone",
    "in_person_event",
    "partner_event",
    "sponsored_event",
    "ticketed_event",
    "ticket_announcement",
    "shop_event",
    "web_store",
    "avatar_items",
    "item_release",
    "promo",
    "game_update",
    "feature_update",
    "pokemon_go_update",
    "bug_fix",
    "known_issue",
    "event_update",
    "event_reschedule",
    "event_cancellation",
    "unknown",
]

ANNOUNCEMENT_TYPES = [
    "new_event",
    "event_update",
    "event_reschedule",
    "event_cancellation",
    "information",
]


def build_prompt(article_text):
    event_type_list = "\n".join(EVENT_TYPES)
    announcement_type_list = "\n".join(ANNOUNCEMENT_TYPES)

    return f"""
You are the classification component of an automated Pokémon GO
calendar system.

Your job is NOT to identify every Pokémon GO feature, Pokémon, reward,
bonus, research task, item, or topic mentioned in an article.

Your job is to determine whether the article is announcing, updating,
rescheduling, or cancelling a specific event or announcement that can
be represented by one or more of the supported event types below.

The most important principle is:

THE ARTICLE'S PRIMARY SUBJECT MATTERS.
INCIDENTAL CONTENT DOES NOT.

An event type must describe the actual primary announcement, not merely
something that happens to be mentioned somewhere in the article.

False positives are worse than false negatives.

It is completely valid for "event_types" to be an empty list if none
of the supported event types accurately describes the article's primary
subject.

Do not force an article into a category.


============================================================
SUPPORTED EVENT TYPES
============================================================

{event_type_list}


============================================================
SUPPORTED ANNOUNCEMENT TYPES
============================================================

{announcement_type_list}


============================================================
PRIMARY-SUBJECT CLASSIFICATION
============================================================

Use this conceptual two-pass process.

PASS 1 — IDENTIFY THE PRIMARY ANNOUNCEMENT

Determine:

1. What is this article actually announcing?
2. What is the canonical event or announcement being discussed?
3. What event receives the article's main dates and description?
4. If this is an update, reschedule, or cancellation, what existing
   event is being changed?
5. Where does that event actually take place?
6. Which content is merely incidental context?

PASS 2 — CLASSIFY THE PRIMARY ANNOUNCEMENT

Only after identifying the primary announcement, select the minimum
number of event_types necessary to accurately describe it.

Do not classify incidental content.

An event type should be included only when the primary announcement
itself independently qualifies as that event type.

For example, if an article announces a Community Day and mentions
Timed Research, a Pokémon debut, a shiny debut, bonuses, and a
PokéStop Showcase, the article is still primarily a Community Day.

Do NOT return all of those related categories.

Prefer:

["community_day"]

rather than a large collection of related categories.


============================================================
GENERAL ANTI-FALSE-POSITIVE RULE
============================================================

DO NOT assign an event type merely because the article:

- mentions that concept
- references that concept
- links to another article about that concept
- includes a Pokémon associated with that concept
- includes rewards associated with that concept
- includes research associated with that concept
- includes bonuses associated with that concept
- includes a ticket associated with that concept
- includes a shop offer associated with that concept
- mentions the concept as historical context
- mentions the concept as an example
- says that the concept is available during another event
- says that the concept previously happened
- says that the concept will happen elsewhere
- contains a Pokémon debut associated with another event
- contains a shiny debut associated with another event
- contains incidental information about another event
- contains navigation, menu, footer, header, or website UI text

The event type must describe the primary announcement itself.

If the relationship is merely "this thing is included in or mentioned
by the event", do not classify the related thing separately.


============================================================
MINIMUM NECESSARY CLASSIFICATION
============================================================

Use the smallest number of event types that accurately represents the
primary announcement.

If one event type is sufficient, return exactly one event type.

Default to exactly one event type. Use multiple event types only when
the article explicitly announces multiple distinct, independently
actionable events and treating them as separate types is necessary
to represent the announcement.

Do not add categories simply because they are technically applicable
to something mentioned in the article.

For example:

A Community Day article that also contains Timed Research:
["community_day"]

A Twitch Drops article that also provides research:
["twitch_drops"]

A GO Tour article that announces a new Pokémon debut:
["go_tour"]

A themed event article that happens to feature a Pokémon debut:
do not add "pokemon_debut" unless the debut itself is independently
the primary announcement.


============================================================
EMPTY EVENT_TYPES IS VALID
============================================================

If the article does not primarily announce a supported calendar-worthy
event, return:

"event_types": []

Do not invent a category.

Do not use "unknown" merely because the article is difficult.

Use an empty list when the article is a legitimate Pokémon GO article
but none of the supported calendar-worthy categories accurately
describes its primary subject.

Use "unknown" only when there is a genuine primary announcement but
you cannot reasonably determine what category it belongs to.


============================================================
EVENT TYPE DEFINITIONS
============================================================

RAID EVENTS

"raid_day":
Use when the primary event is a Raid Day.

"mega_raid_day":
Use when the primary event is a Mega Raid Day.

"super_mega_raid_day":
Use when the primary event is a Super Mega Raid Day.

"shadow_raid_day":
Use when the primary event is a Shadow Raid Day.

"elite_raid_day":
Use when the primary event is an Elite Raid Day.

"max_battle_day":
Use for a Max Battle Day when a more specific Max Battle type does
not apply.

"gigantamax_max_battle_day":
Use when the primary event is specifically a Gigantamax Max Battle Day.

"dynamax_max_battle_day":
Use when the primary event is specifically a Dynamax Max Battle Day.

Do not assign any raid event type merely because raids are mentioned
as part of another event.

"raid_hour":
Use when the primary event is a Raid Hour.

"raid_rotation":
Use when the primary announcement is a change or scheduled rotation
of raid availability itself.

"raid_boss_rotation":
Use when the primary announcement is specifically about a rotation
of raid bosses.

Do not classify a normal event as a raid rotation simply because it
contains a raid boss.


============================================================
COMMUNITY EVENTS
============================================================

"community_day":
Use when the primary event is a regular Community Day.

"community_day_classic":
Use when the primary event is Community Day Classic.

"community_day_makeup":
Use when the primary event is specifically a makeup Community Day.

Do not add "pokemon_debut", "shiny_debut", "timed_research",
"special_research", or similar categories merely because those things
are included in a Community Day.


============================================================
SPOTLIGHT / WEEKLY EVENTS
============================================================

"spotlight_hour":
Use when the primary event is a Spotlight Hour.

"weekly_event":
Use for a recurring weekly event when that weekly event itself is the
primary announcement.

"monthly_go_pass":
Use when the primary announcement is the month-long GO Pass, typically
named "GO Pass: [Month]" (for example, "GO Pass: October"). The pass
itself spans most or all of a calendar month.

"weekly_go_pass":
Use when the primary announcement is a shorter, roughly week-long
themed GO Pass, typically named for an event or theme (for example,
"Harvest Festival GO Pass"). Use the announced pass dates and duration,
not just the name, to distinguish it from the monthly pass.

Do not classify every article mentioning GO Pass as either type. The
pass itself must be the primary subject. Do not use these types for a
general article about the GO Pass product or a separate event that only
mentions pass rewards.


============================================================
MAJOR GLOBAL EVENTS
============================================================

"go_tour":
Use when the primary event is Pokémon GO Tour.

"go_fest":
Use when the primary event is Pokémon GO Fest.

"go_wild_area":
Use when the primary event is Pokémon GO Wild Area.

"safari_zone":
Use when the primary event is an official Safari Zone event.

"city_safari":
Use when the primary event is Pokémon GO City Safari.

"regional_event":
Use when the primary event is a regional Pokémon GO event that is not
more specifically covered by another event type.

Do not classify an article as one of these event types merely because
it mentions the event, references a previous event, features Pokémon
that appeared at the event, or discusses content associated with it.

The event itself must be the primary subject.

A navigation menu, header, footer, website link, or other site UI
mentioning "GO Wild Area", "GO Tour", or "GO Fest" is NOT evidence that
the article is about that event.

A themed event that mentions Wild Area content is not automatically a
GO Wild Area event.

A City Safari article is not a GO Wild Area event merely because both
are large Pokémon GO events.

A GO Fest article mentioning a Pokémon debut is still primarily GO Fest.

A GO Tour article mentioning raids is still primarily GO Tour.


============================================================
SATURDAY EVENT
============================================================

Do NOT output "saturday_event".

Python will derive "saturday_event" from the event's start date.

Never classify something as a Saturday event because the article happens
to mention Saturday.


============================================================
POKÉMON DEBUTS AND SHINY DEBUTS
============================================================

"pokemon_debut":
Use only when the Pokémon debut itself is the primary announcement.

Do not use it merely because another event includes a new Pokémon.

"shiny_debut":
Use only when the shiny debut itself is the primary announcement.

Do not use it merely because another event features a newly available
shiny Pokémon.


============================================================
COSTUMES / BACKGROUNDS / ITEMS
============================================================

"costume_pokemon_event":
Use only when a costume Pokémon event itself is the primary subject.

"special_background_event":
Use only when the special-background event itself is the primary subject.

"avatar_items":
Use only when the primary announcement is about avatar items.

"item_release":
Use only when the primary announcement is about the release of an item
or game item.

Do not classify another event as one of these merely because those
things are included in it.


============================================================
RESEARCH
============================================================

"timed_research":
Use only when Timed Research itself is the primary announcement.

"special_research":
Use only when Special Research itself is the primary announcement.

"field_research_event":
Use only when a Field Research event itself is the primary announcement.

"collection_challenge":
Use only when the Collection Challenge itself is the primary
announcement.

Do not classify an event as a research event merely because it contains
research.

For example:

"Community Day: Zorua" with Timed Research
→ ["community_day"]

"Twilight Trails: Timed Research"
→ ["timed_research"]


============================================================
BATTLE / GBL
============================================================

"battle_day":
Use when the primary event is a Battle Day.

"gbl_season_update":
Use for an announcement about a new GBL season or the major rules,
moveset, league, or format changes associated with a new GBL season.

"gbl_update":
Use for a significant GBL update that is not specifically a new season.

"go_battle_league":
Use when the primary subject is the GO Battle League itself.

"battle_event":
Use when the primary event is a general Pokémon GO battle event.

"league_event":
Use when the primary event is specifically a league event.

"cup":
Use when the primary event is specifically a named GBL cup.

Do not create calendar events for ordinary weekly GBL cups merely because
they are listed in a season announcement unless the article is primarily
announcing the cup itself.


============================================================
TWITCH DROPS
============================================================

"twitch_drops":
Use when the primary announcement is Twitch Drops.

Twitch Drops are an online event.

For Twitch Drops:

- "is_online" must be true.
- "locations" should normally be [].
- "end" must be null.
- "watch_requirements_minutes" must contain the cumulative viewing
  requirements for the relevant drops.
- Python will calculate the actual end time from the largest viewing
  requirement.

Do NOT classify Twitch Drops as "code_distribution" merely because
codes or rewards are involved.

Do NOT classify Twitch Drops as "timed_research" merely because research
is awarded through the drops.

If an article contains Twitch Drops as a minor component of another
event, do not automatically classify it as Twitch Drops. The Drops
announcement must itself be an independently actionable primary
announcement.


============================================================
CODE DISTRIBUTIONS
============================================================

"code_distribution":
Use when obtaining or redeeming a promotional code is itself an
independently actionable primary announcement.

Do not use "code_distribution" merely because:

- Twitch Drops provide codes
- an event rewards an item that normally comes from a code
- an article mentions a previously distributed code
- a code is mentioned in passing

A code distribution must actually be the subject of the announcement.


============================================================
TICKETS
============================================================

"ticketed_event":
Use when the ticketed event itself is the primary subject.

"ticket_announcement":
Use when the primary announcement is specifically about tickets,
ticket availability, ticket sales, or a ticket announcement.

Do not classify every event as "ticketed_event" merely because the event
has an optional ticket.

Do not classify a normal event as "ticket_announcement" merely because
the article mentions that tickets are available.


============================================================
WEB STORE / SHOP
============================================================

"web_store":
Use only when the Web Store offering/event itself is the primary
announcement.

"shop_event":
Use only when the in-game shop event itself is the primary announcement.

Do not classify another event as a Web Store or shop event merely
because the article contains a bundle, offer, purchase option, or
link to the Web Store.


============================================================
IN-PERSON / REGIONAL / PARTNER EVENTS
============================================================

"in_person_event":
Use only when the primary announcement is an in-person event that is
not more specifically represented by another event type.

"partner_event":
Use only when the primary announcement is a partner event.

"sponsored_event":
Use only when the primary announcement is a sponsored event.

Do not classify a normal event as one of these merely because a partner,
sponsor, venue, or broadcast location is mentioned.


============================================================
SEASONAL EVENTS
============================================================

"season":
Use when the primary announcement is the new Pokémon GO season itself.

"seasonal_event":
Use for a specific seasonal event when no more specific event type
applies.

"global_event":
Use only when the primary announcement is a global event that does not
have a more specific supported event type.

Do not classify every event occurring during a season as "season".


============================================================
UPDATES / RESCHEDULES / CANCELLATIONS
============================================================

The "announcement_type" describes what the article is doing.

Use:

"new_event"
when announcing a new event.

"event_update"
when providing a meaningful update to an existing event.

"event_reschedule"
when changing the date or time of an existing event.

"event_cancellation"
when cancelling an existing event.

"information"
when the article provides information without announcing a
calendar-worthy event.

If an article is an update, reschedule, or cancellation, identify the
underlying event in "event_name" and classify the underlying event in
"event_types".

Do not create a new unrelated event type merely because the article
contains information about another event.

For example:

A reschedule article for City Safari:
announcement_type = "event_reschedule"
event_types = ["city_safari"]

A cancellation article for a Raid Day:
announcement_type = "event_cancellation"
event_types = ["raid_day"]


============================================================
EVENT PERIODS
============================================================

Use "event_periods" when an announcement contains multiple distinct
date/time ranges that should be represented as separate calendar events.

Examples include:

- Pokémon GO Tour with separate in-person and global dates.
- Pokémon GO Fest with separate in-person and global dates.
- Pokémon GO Wild Area with separate distinct event periods.
- An event with separate regional or location-specific periods.

Each event period must contain:

- "start": the beginning of that period.
- "end": the end of that period.
- "label": a short description identifying the period.

Do NOT combine separate periods into one continuous date range.

For example, if an event has:

- an in-person event February 19-21
- a global event February 27-28

return two event_periods rather than one February 19-28 period.

If the event has only one continuous period, return an empty
"event_periods" array and use the normal "start" and "end" fields.

If dates are announced but exact times are not provided, use:

- 00:00:00 for the start
- 23:59:59 for the end

If an event has multiple periods but the article does not provide
enough information to determine one of the periods, do not invent
dates for that period.

For Twitch Drops, use an empty event_periods array. Python calculates
the end time from the viewing requirements.


============================================================
LOCATION RULES
============================================================

"locations" must contain actual player-facing event locations.

For online/remote events:

- locations = []
- is_online = true

Do not use:

- broadcast studio locations
- headquarters
- company offices
- press event locations
- the location of the article's author
- irrelevant locations mentioned in passing

For City Safari and regional events, provide the actual city/region
where players participate.

Do not guess a location.

If the article does not specify a location, use [].


============================================================
DATES AND TIMES
============================================================

Return dates and times in ISO 8601 local time:

YYYY-MM-DDTHH:MM:SS

Do not include a UTC offset.

Use:

"timezone": "local"

when the event time is local to the player's/event location.

Do not confuse the article publication date with the event date.

Do not guess dates or times.

If the article is a save-the-date announcement and exact event dates
are not yet available, "start" and "end" may be null.

For events spanning multiple days, use the actual event start and end.

For events with multiple distinct periods, put those periods in
"event_periods" rather than combining them into one start/end range.

For Twitch Drops, "end" must be null because Python calculates it.


============================================================
CANONICAL EVENT NAME
============================================================

"event_name" should be the official/canonical name of the event being
announced.

Do not prepend generic labels such as:

- "Pokémon GO Event:"
- "Pokémon GO:"
- "Event:"
- "Special Event:"

unless those words are actually part of the official event name.

The event name should identify the underlying event consistently so that
later updates, reschedules, and cancellations can be associated with it.


============================================================
DETAILS
============================================================

"details" must always be present.

It must contain:

"watch_requirements_minutes":
A list of cumulative Twitch viewing requirements in minutes.

For non-Twitch events, use [].

"is_online":
true for online/remote events.

false for in-person events.

For events where the distinction is not applicable, use false unless
the article clearly indicates that participation is online.


============================================================
CLASSIFICATION EXAMPLES
============================================================

EXAMPLE 1 — COMMUNITY DAY

Article:
"October 2026 Community Day: Zorua"

Correct:

event_types = ["community_day"]

Do NOT add:

- pokemon_debut
- shiny_debut
- timed_research
- special_research
- collection_challenge
- saturday_event

merely because those things are included in the article.


EXAMPLE 2 — MONTHLY GO PASS

Article:
"GO Pass: October"

Correct:

event_types = ["monthly_go_pass"]

EXAMPLE 3 — WEEKLY GO PASS

Article:
"Harvest Festival GO Pass"

The announcement describes a themed pass available during the roughly
week-long Harvest Festival event.

Correct:

event_types = ["weekly_go_pass"]

Do not add unrelated categories simply because the pass includes
rewards, research, bonuses, or other features.


EXAMPLE 4 — CITY SAFARI

Article:
"Pokémon GO City Safari: Boston"

Correct:

event_types = ["city_safari"]

Do NOT classify it as:

["go_wild_area"]

merely because both are major Pokémon GO events.


EXAMPLE 5 — TWITCH DROPS

Article:
"Pokémon Night Out Twitch Drops"

Correct:

event_types = ["twitch_drops"]

Correct:

locations = []
is_online = true
end = null

If drops are available at 30, 60, and 90 minutes:

watch_requirements_minutes = [30, 60, 90]

Do NOT add:

- code_distribution
- timed_research

merely because codes or research are involved.


EXAMPLE 5 — GO TOUR SAVE THE DATE

Article:
"Pokémon GO Tour 2027"

If the article only announces that the event is coming and does not
provide exact event dates:

event_types = ["go_tour"]

start = null
end = null

If the article provides separate in-person and global dates, use:

event_types = ["go_tour"]

start = null
end = null

event_periods = [
  {{
    "start": "2027-02-19T00:00:00",
    "end": "2027-02-21T23:59:59",
    "label": "In-person"
  }},
  {{
    "start": "2027-02-27T00:00:00",
    "end": "2027-02-28T23:59:59",
    "label": "Global"
  }}
]


EXAMPLE 6 — WORLD SPACE WEEK

Article:
"World Space Week 2026"

Correct:

event_types = []

if the primary article is a themed World Space Week event and none of
the supported calendar-worthy categories describes that event.

Do NOT classify it as:

["go_wild_area"]

just because Wild Area content is mentioned.

Do NOT classify it as:

["pokemon_debut"]

just because a Pokémon debuts during it.

Do NOT classify it as:

["go_wild_area", "pokemon_debut"]

by collecting incidental topics from the article.

The primary subject controls the classification.


============================================================
FINAL CHECK BEFORE OUTPUT
============================================================

Before producing the JSON, verify:

1. What is the article primarily announcing?
2. What is the canonical event name?
3. Am I classifying the primary event rather than incidental content?
4. Does every event_type independently describe the primary announcement?
5. Could I remove an event_type without losing an important description
   of the primary event?
6. If yes, remove it.
7. Am I forcing the article into a category when [] would be more accurate?
8. Are dates actual event dates rather than the publication date?
9. Are locations actual player-facing locations?
10. For Twitch Drops, is end null and are viewing requirements included?
11. If there are multiple distinct event periods, did I put them in
    event_periods instead of combining them into one range?
12. Did I avoid inventing information?

Return ONLY valid JSON matching this schema:

{{
  "announcement_type": "new_event | event_update | event_reschedule | event_cancellation | information",
  "primary_subject": "string",
  "event_types": [],
  "event_name": "string",
  "start": "YYYY-MM-DDTHH:MM:SS or null",
  "end": "YYYY-MM-DDTHH:MM:SS or null",
  "event_periods": [
    {{
      "start": "YYYY-MM-DDTHH:MM:SS",
      "end": "YYYY-MM-DDTHH:MM:SS",
      "label": "string"
    }}
  ],
  "timezone": "local",
  "locations": [],
  "is_update": false,
  "is_cancellation": false,
  "details": {{
    "watch_requirements_minutes": [],
    "is_online": false
  }}
}}

ARTICLE:
{article_text}
""".strip()