# ðŸŽ“ University Task & Study Tracker

A lightweight, modular Command Line Interface (CLI) application built in Python to track university assignments and exam study progress.

## ðŸ“‚ Project Structure

This project is broken down into modules for easy maintenance and feature expansion:

* **`main.py`** - The entry point. Handles user commands (CLI arguments) and coordinates the app.
* **`models.py`** - Contains the Data Classes (`Assignment` and `Assessment`). Defines what tasks are and how they calculate time remaining.
* **`database.py`** - Handles saving and loading your tasks to a local JSON file so progress isn't lost.
* **`display.py`** - Handles the terminal User Interface, including progress bars and ANSI color coding.
* **`data/assignments.json`** - Your database file (generated automatically).

## ðŸš€ How to Use

Run the tracker from your terminal:

**View your tasks (Detailed view):**
python main.py

**View your tasks (Compact view):**
python main.py --compact

**Update an Assignment (add completed questions):**
python main.py --update "portfolio" 3

**Update an Assessment (log hours studied):**
python main.py --update "machine learning" 1.5


Update 0.1 claude

**`models.py`**

* `Assessment` now stores a `sessions` list — each entry is `{"date": "YYYY-MM-DD", "hours": float}`
* `log_session(hours)` adds today's session and updates `hours_studied` automatically
* `last_studied_days_ago()` returns how many days since the last session, or `None` if none logged
* `neglect_level()` returns `"warn"` (4+ days) or `"alert"` (7+ days) based on that
* `recommended_daily_hours()` computes the burn-down: `remaining_hours / days_left`
* Both `Assignment` and `Assessment` now have an `archived` flag

**`database.py`**

* JSON is now structured as `{"active": [...], "archived": [...]}` instead of a flat list — old flat files are 
* New `archive_item(name)` function moves an item from active to archived and saves
* New `load_archived()` function for the `--archived` view

**`display.py`**

* Assessments with `days > 0` and `percent < 100` now show `⚡ X hrs recommended`
* Assessments show last-studied info with yellow/red neglect warnings at 4 and 7 days
* OVERDUE on assignments now says `OVERDUE by Xd` for more context

**`main.py`**

* `--archive "name"` moves an item to the archive
* `--archived` shows the archive in compact view
* `--update` on assessments now calls `log_session()` instead of directly adding to `hours_studied`, so sessions are recorded
* Negative amounts are rejected with a clear error
