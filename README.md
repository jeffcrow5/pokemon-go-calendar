# Pokemon GO Calendar Automation

Automatically monitors official Pokemon GO announcements, classifies them with a local Ollama LLM, and synchronizes relevant events to a Google Calendar.

The automation is designed to run unattended on a Windows PC and periodically checks for new Pokemon GO announcements. It uses local AI rather than a paid cloud AI API.

## Features

* Monitors the official Pokemon GO news feed.
* Extracts article content automatically.
* Uses a local Ollama/Qwen model to classify announcements.
* Applies configurable calendar rules from `calendar_rules.json`.
* Creates, updates, and deletes Google Calendar events.
* Supports multiple distinct event periods for a single announcement.
* Includes the official article URL in calendar event descriptions.
* Handles event updates, reschedules, and cancellations.
* Filters nearby regional and City Safari events by distance from a configured home location.
* Derives Saturday events automatically.
* Calculates Twitch Drops event end times from cumulative watch requirements.
* Skips articles for events that have already ended.
* Uses GPU VRAM, GPU utilization, and CPU utilization checks before starting an automation run.
* Runs automatically through Windows Task Scheduler.
* Uses a hidden Windows Script Host launcher so no terminal window remains open during scheduled runs.
* Uses rotating logs to prevent the log file from growing indefinitely.

## Requirements

### Operating system

The current automation is designed for:

* Windows 10 or Windows 11
* A machine that can remain powered on while the automation runs

### Python

Python 3.14 or a compatible recent Python version is recommended.

Verify Python:

```powershell
py --version
```

### Ollama

Install Ollama and make sure it is running locally.

The automation currently uses:

```text
qwen3.5:9b
```

Pull the model with:

```powershell
ollama pull qwen3.5:9b
```

Verify that it is available:

```powershell
ollama list
```

The application expects Ollama's local API at:

```text
http://localhost:11434/api/chat
```

No cloud LLM account or API key is required.

### NVIDIA GPU

The resource guard uses `nvidia-smi` to determine:

* Free GPU VRAM
* GPU utilization

An NVIDIA GPU with sufficient VRAM is therefore required for the current configuration.

The default resource thresholds are:

```text
Minimum free VRAM: 6,200 MiB
Maximum CPU usage: 50%
Maximum GPU usage: 30%
```

These values can be changed in `gpu_guard.py`.

The purpose of these checks is primarily to avoid starting the LLM while the computer is being used for something GPU-intensive, such as gaming.

If the checks fail, the automation exits without processing anything. The next scheduled run will try again.

## Installation

Clone the repository:

```powershell
git clone https://github.com/YOUR_USERNAME/pokemon-go-calendar.git
cd pokemon-go-calendar
```

Install Python dependencies:

```powershell
py -m pip install -r requirements.txt
```

## Google Calendar Setup

The automation uses the Google Calendar API to create and update calendar events.

### 1. Create a Google Cloud project

Go to the Google Cloud Console:

https://console.cloud.google.com/

Create a new project for the automation.

### 2. Enable Google Calendar API

In the Google Cloud Console:

1. Open **APIs & Services**.
2. Open **Library**.
3. Search for **Google Calendar API**.
4. Enable it.

### 3. Configure OAuth consent

Configure the OAuth consent screen for the application.

A desktop application is appropriate for this project because the automation uses Google's installed-application OAuth flow.

### 4. Create OAuth credentials

Create an OAuth client ID with application type:

```text
Desktop app
```

Download the resulting credentials file.

Rename it:

```text
credentials.json
```

Place it in the project directory:

```text
PokemonGoCalendar/
    credentials.json
```

**Do not commit this file to Git.**

The repository's `.gitignore` should exclude it.

### 5. First authentication

Run the application manually:

```powershell
py pokemon_go.py
```

The first run should open a browser for Google authorization.

After authorization, Google OAuth credentials will be saved locally as:

```text
token.json
```

**Do not commit `token.json` to Git.**

Future automated runs use the saved token.

### 6. Calendar configuration

The Google Calendar ID is configured in:

```text
google_calendar.py
```

Change `CALENDAR_ID` to the calendar where events should be created.

The default implementation also uses:

```text
America/Denver
```

as the calendar timezone.

If your calendar uses another timezone, change `CALENDAR_TIMEZONE`.

## Calendar Rules

The calendar behavior is controlled by:

```text
calendar_rules.json
```

This file is the source of truth for which event types are invited and which are ignored.

Each event type has one of the following actions:

```text
invite
ignore
```

For example:

```json
{
  "raid_day": "invite",
  "community_day": "invite",
  "spotlight_hour": "invite",
  "season": "ignore"
}
```

### Important

The Python code should not contain duplicate lists of invite/ignore rules.

When deciding whether an event belongs on the calendar, the application should consult `calendar_rules.json`.

This makes it possible to change calendar behavior without modifying the program.

### Current rule defaults

The current `calendar_rules.json` invites every supported event type except
`monthly_go_pass`, which is ignored. In particular:

* `weekly_go_pass` is invited for short, themed passes such as **Harvest
  Festival GO Pass**.
* `monthly_go_pass` is ignored for month-long passes, usually named for a
  calendar month (such as **GO Pass: October**).
* `city_safari` and `regional_event` are invited only when a location can be
  identified within the configured distance of `home_location`.

The classifier distinguishes weekly from monthly passes using the title and
announced dates/duration. A mention of GO Pass as a reward or feature in a
different announcement does not make that announcement a GO Pass event.
Events that have already ended are also skipped independently of these rules.

These are editable defaults, not fixed behavior. If you clone the project,
change `calendar_rules.json` on your copy to choose which event types you want
invited; no Python changes are needed. You can also adjust the location and
distance settings there.

### Location settings

The rules file also contains:

```json
"settings": {
  "home_location": {
    "city": "Example City",
    "state": "Example State",
    "country": "United States"
  },
  "regional_event_max_distance_miles": 100,
  "city_safari_max_distance_miles": 100
}
```

The application geocodes the configured home location and uses the configured distance limits for regional events and City Safari events.

For a public repository, use generic/example values in the committed configuration.

Keep your personal `calendar_rules.json` local if it contains personal location information.

## Recommended Configuration Files

A public repository should contain:

```text
calendar_rules.example.json
```

and your actual local configuration should be:

```text
calendar_rules.json
```

with the latter excluded by `.gitignore`.

Copy the example when setting up a new installation:

```powershell
Copy-Item calendar_rules.example.json calendar_rules.json
```

Then edit `calendar_rules.json` with your preferred rules and location.

## Running Manually

Run a synchronization manually with:

```powershell
py pokemon_go.py
```

To print the run's log messages to the console while debugging, add `--verbose`
or its shorthand `-v`:

```powershell
py pokemon_go.py --verbose
```

The automation continues to write logs to `automation.log` as usual.

The application will:

1. Check CPU usage.
2. Check GPU utilization.
3. Check available GPU VRAM.
4. Exit immediately if the system is too busy.
5. Download the official Pokemon GO news page.
6. Identify new articles.
7. Extract article content.
8. Use the lightweight local LLM pass to determine whether an event has already ended.
9. Classify new articles with the full local LLM.
10. Apply calendar rules.
11. Create, update, or delete Google Calendar events as appropriate.
12. Save persistent state.

### Reprocess all news

To remove **every event** from the configured Google Calendar and clear the
processed-article state, then immediately run a normal sync, run:

```powershell
py pokemon_go.py --reinitialize
```

This is destructive: it deletes all events in that configured calendar, not
only events created by this automation. The state is cleared only after the
calendar events have been deleted successfully. If the sync is skipped by the
resource guard, the reset still completes and the next scheduled run will
process the articles again.

## Resource Guard

The resource guard is implemented in:

```text
gpu_guard.py
```

Before an automation run begins, the application requires:

```text
Free VRAM >= 6,200 MiB
CPU usage < 50%
GPU utilization < 30%
```

If any condition fails, the run is skipped.

For example:

```text
SKIPPING SYNC: GPU usage is 85%; maximum allowed is below 30%. Refusing to start the LLM.
```

This is intentional. The automation should not interfere with normal computer use, particularly gaming.

### Why the checks only happen at startup

Once the automation starts Ollama, the Qwen model itself occupies GPU VRAM.

Therefore, the resource check is performed before the LLM starts, not repeatedly during the run.

A subsequent check would incorrectly interpret Ollama's own VRAM allocation as another application consuming the GPU.

## Persistent State

The application stores processing state in:

```text
state.json
```

This tracks:

* Previously processed articles
* Event identities
* Relationships between articles and events
* Google Calendar event IDs
* Current classifications

`state.json` should not be committed to Git because it contains machine-specific runtime state.

If the state file is deleted, previously processed articles may be processed again.

## Logging

Logs are written to:

```text
automation.log
```

The logger uses rotation:

```text
automation.log
automation.log.1
automation.log.2
automation.log.3
```

The active log is limited to approximately 2 MB, with three backup files retained.

Logs should not be committed to Git.

## Windows Task Scheduler

The recommended configuration is to run the automation automatically every 15 minutes.

### Launcher

The repository includes:

```text
run_calendar.vbs
```

The script starts Python through Windows Script Host without opening a visible terminal window.

The launcher contains the paths to:

* Python
* `pokemon_go.py`

If Python or the project is installed somewhere else, update those paths.

### Create the scheduled task

Open:

```text
Task Scheduler
```

Create a task named:

```text
Pokemon GO Calendar Automation
```

Configure a trigger to:

* Start at system startup
* Repeat every 15 minutes

Recommended additional settings:

* **Start the task as soon as possible after a scheduled start is missed**
* **Do not start a new instance if an existing instance is already running**

The action should run:

```text
wscript.exe
```

with the argument:

```text
"C:\Path\To\PokemonGoCalendar\run_calendar.vbs"
```

The exact path should match the location of the project on the machine.

### Why Task Scheduler is used

This allows the automation to:

* Start automatically after reboot
* Continue running without an open terminal
* Retry every 15 minutes
* Skip runs when the computer is busy
* Avoid requiring a terminal window to remain open

## Project Structure

A typical installation looks like:

```text
PokemonGoCalendar/
├── pokemon_go.py
├── news.py
├── classifier.py
├── classifier_prompt.py
├── rules.py
├── state.py
├── event_filter.py
├── google_calendar.py
├── gpu_guard.py
├── calendar_rules.json
├── calendar_rules.example.json
├── credentials.json
├── token.json
├── state.json
├── run_calendar.vbs
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    ├── test_state.py
    ├── test_live.py
    ├── test_rules.py
    ├── test_calendar.py
    └── test_event_filter.py
```

The following files should remain local and should **not** be committed:

```text
credentials.json
token.json
state.json
automation.log
automation.log.*
```

## Security

Never commit:

* Google OAuth credentials
* OAuth access/refresh tokens
* API keys
* Passwords
* Personal secrets
* Personal runtime state that should remain private

Before the first Git commit, check:

```powershell
git status
```

You can also verify that sensitive files are ignored:

```powershell
git check-ignore -v credentials.json token.json state.json automation.log
```

If credentials are accidentally committed, simply deleting the file in a later commit is **not sufficient** because the secret can remain in Git history.

Revoke or rotate the affected credentials and remove the secret from the repository history.

## Testing

The project contains several tests:

```powershell
py -m unittest discover
```

Individual tests can also be run directly, for example:

```powershell
py test_rules.py
```

Some tests may require access to local services or Google authentication depending on their implementation.

## Troubleshooting

### Ollama is not responding

Check that Ollama is running:

```powershell
ollama list
```

Then verify that the model exists:

```powershell
ollama list
```

If necessary:

```powershell
ollama pull qwen3.5:9b
```

### The automation keeps skipping because of GPU usage

Check current GPU status:

```powershell
nvidia-smi
```

The default GPU utilization threshold is 30%.

Gaming or other GPU-intensive applications will normally cause the automation to skip.

### The automation keeps skipping because of CPU usage

The default CPU threshold is 50%.

Check Windows Task Manager to determine what is consuming CPU resources.

The threshold can be changed in:

```text
gpu_guard.py
```

### The automation keeps skipping because of VRAM

Check:

```powershell
nvidia-smi
```

The default requirement is 6,200 MiB of free VRAM.

If another application is using GPU memory, the automation will intentionally wait for a later run.

### Google authentication fails

Delete the local token:

```text
token.json
```

Then run the application manually again:

```powershell
py pokemon_go.py
```

A new Google authorization flow should occur.

Do not delete or publish `credentials.json` unless you are intentionally replacing the OAuth client configuration.

### Events are not being created

Check:

```text
calendar_rules.json
```

and verify that the relevant event type is set to:

```text
"invite"
```

Then inspect:

```text
automation.log
```

for classification and calendar errors.

### An event is incorrectly being ignored

The first place to check is:

```text
calendar_rules.json
```

The second place is:

```text
classifier_prompt.py
```

The classifier determines the event type; the rules file determines whether that type should be placed on the calendar.

## Design Philosophy

The project intentionally separates responsibilities:

```text
Official Pokemon GO news
        ↓
     news.py
        ↓
  Article extraction
        ↓
    classifier.py
        ↓
 Local Ollama/Qwen
        ↓
 Structured classification
        ↓
     rules.py
        ↓
 calendar_rules.json
        ↓
 Google Calendar
```

The LLM is responsible for understanding the announcement.

The rules file is responsible for deciding what the user actually wants on the calendar.

This separation makes calendar preferences deterministic and easy to change.

## License

Add a license appropriate for your intended use before publishing the repository publicly.

If this project is only for personal use, keeping the repository private is also a perfectly reasonable choice.
