import json
import os
from models import Assignment, Assessment

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "assignments.json")

# ── Persistence structure ────────────────────────────────────────────────────
# The JSON file now has two top-level keys:
#   "active"   – items shown in the normal tracker
#   "archived" – items moved there by --archive

def _default_items():
    return [
        Assessment("Information Systems",  "2026-05-04", target_hours=15),
        Assessment("Machine Learning",     "2026-05-08", target_hours=20),
        Assessment("Programming",          "2026-05-13", target_hours=25),
        Assessment("Big Data & IOT",       "2026-05-19", target_hours=15),
        Assessment("Stats for Data Science","2026-05-26", target_hours=20),

        Assignment("IS",    "2026-04-10", 3, completed_q=3),
        Assignment("BD",    "2026-04-24", 4, completed_q=4),
        Assignment("PROG",  "2026-04-24", 7, completed_q=0),
        Assignment("STATS", "2026-05-28", 3, completed_q=0),
        Assignment("ML",    "2026-05-28", 6, completed_q=0),
    ]

def _item_from_dict(d):
    if d.get("type") == "assessment":
        return Assessment(
            d["title"],
            d["date_str"],
            d.get("target_hours", 10),
            d.get("hours_studied", 0),
            sessions=d.get("sessions", []),
            archived=d.get("archived", False),
        )
    else:
        return Assignment(
            d["title"],
            d["date_str"],
            d["total_q"],
            d.get("completed_q", 0),
            archived=d.get("archived", False),
        )

def _load_raw():
    """Return (active_list, archived_list) from disk, or defaults if missing."""
    if not os.path.exists(DATA_FILE):
        return _default_items(), []

    with open(DATA_FILE, "r") as f:
        raw = json.load(f)

    # Support old flat-list format transparently
    if isinstance(raw, list):
        return [_item_from_dict(d) for d in raw], []

    active   = [_item_from_dict(d) for d in raw.get("active",   [])]
    archived = [_item_from_dict(d) for d in raw.get("archived", [])]
    return active, archived

def _save_raw(active, archived):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(DATA_FILE, "w") as f:
        json.dump(
            {
                "active":   [i.to_dict() for i in active],
                "archived": [i.to_dict() for i in archived],
            },
            f, indent=4
        )

# ── Public API ───────────────────────────────────────────────────────────────

def load_all():
    active, _ = _load_raw()
    return active

def load_archived():
    _, archived = _load_raw()
    return archived

def save_all(items):
    _, archived = _load_raw()
    _save_raw(items, archived)

def archive_item(name_query):
    """
    Move the first active item matching name_query into the archive.
    Returns the archived item on success, or None if not found.
    """
    active, archived = _load_raw()
    target = None

    # Exact match first
    for item in active:
        if item.title.lower() == name_query:
            target = item
            break
    # Partial match fallback
    if not target:
        for item in active:
            if name_query in item.title.lower():
                target = item
                break

    if target:
        active.remove(target)
        target.archived = True
        archived.append(target)
        _save_raw(active, archived)

    return target