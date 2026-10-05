import argparse
from database import load_all, save_all, archive_item, load_archived
from display import print_tracker
from models import Assignment, Assessment

def find_item(items, name_query):
    """Return first matching item — exact match preferred over partial."""
    for item in items:
        if item.title.lower() == name_query:
            return item
    for item in items:
        if name_query in item.title.lower():
            return item
    return None

def main():
    parser = argparse.ArgumentParser(description="University Task & Study Tracker")
    parser.add_argument('--compact',  action='store_true', help="Show compact view")
    parser.add_argument('--archived', action='store_true', help="Show archived items")
    parser.add_argument('--update',  nargs=2, metavar=('NAME', 'AMOUNT'),
                        help="Update progress (questions for assignments, hours for assessments)")
    parser.add_argument('--archive', metavar='NAME',
                        help="Move a completed item to the archive")
    args = parser.parse_args()

    # ── Archive command ──────────────────────────────────────────────────────
    if args.archive:
        moved = archive_item(args.archive.lower())
        if moved:
            print(f"📦 '{moved.title}' has been archived.")
        else:
            print(f"⚠️  Could not find an active item matching '{args.archive}'.")

    # ── Show archived view ───────────────────────────────────────────────────
    if args.archived:
        archived_items = load_archived()
        if archived_items:
            print_tracker(archived_items, view='compact')
        else:
            print("\n📭 No archived items yet.")
        return

    # ── Load active items ────────────────────────────────────────────────────
    items = load_all()

    # ── Update command ───────────────────────────────────────────────────────
    if args.update:
        name_query = args.update[0].lower()
        try:
            amount = float(args.update[1])
            if amount < 0:
                print("❌ Error: amount must be a positive number.")
                return

            target = find_item(items, name_query)

            if target:
                if isinstance(target, Assignment):
                    target.completed_q = min(
                        target.completed_q + int(amount),
                        target.total_q
                    )
                    print(f"✅ Updated Assignment '{target.title}' by {int(amount)} question(s).")

                elif isinstance(target, Assessment):
                    target.log_session(amount)
                    print(f"✅ Logged {amount} hrs for '{target.title}'.")

                save_all(items)
            else:
                print(f"⚠️  Could not find a task containing '{name_query}'.")

        except ValueError:
            print("❌ Error: The update amount must be a number.")

    # ── Sort and display ─────────────────────────────────────────────────────
    items.sort(key=lambda x: x.get_days_left())
    mode = 'compact' if args.compact else 'detailed'
    print_tracker(items, view=mode)

if __name__ == "__main__":
    main()
