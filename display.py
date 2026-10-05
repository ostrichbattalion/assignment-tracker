from models import Assignment, Assessment

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"

def print_tracker(items, view='detailed'):
    print(f"\n{'= UNIVERSITY TRACKER =':^60}")

    for item in items:
        days = item.get_days_left()

        # 1. Title truncation
        MAX_TITLE = 25
        display_title = item.title
        if len(display_title) > MAX_TITLE:
            display_title = display_title[:MAX_TITLE-3] + "..."

        # 2. Percentage
        if isinstance(item, Assignment):
            percent = int((item.completed_q / item.total_q) * 100) if item.total_q > 0 else 100
        elif isinstance(item, Assessment):
            percent = int((item.hours_studied / item.target_hours) * 100) if item.target_hours > 0 else 100

        display_percent = min(percent, 100)

        # 3. Priority / status
        if percent >= 100:
            status_text  = f"{GREEN}COMPLETED{RESET}"
            compact_time = f"{GREEN}DONE{RESET}"
            time_color   = GREEN
        elif days < 0 and isinstance(item, Assessment):
            status_text  = f"{GREEN}WRITTEN{RESET}"
            compact_time = f"{GREEN}DONE{RESET}"
            time_color   = GREEN
        elif days < 0:
            status_text  = f"{RED}OVERDUE by {abs(days)}d{RESET}"
            compact_time = f"{RED}{days}d{RESET}"
            time_color   = RED
        elif days <= 3:
            status_text  = f"{days} days left"
            compact_time = f"{YELLOW}{days}d{RESET}"
            time_color   = YELLOW
        else:
            status_text  = f"{days} days left"
            compact_time = f"{days}d"
            time_color   = RESET

        # 4. Render
        if isinstance(item, Assignment):
            bar_color   = GREEN if percent >= 100 else time_color
            bar_content = "█" * (display_percent // 5)
            bar         = f"{bar_color}{bar_content.ljust(20, '-')}{RESET}"

            if view == 'compact':
                print(f"[Assign] {display_title:<25} | [{bar}] {display_percent:>3}% | {compact_time}")
            else:
                print(f"\n{bar_color}▶ {item.title.upper()} (Assignment){RESET}")
                print(f"  Progress: [{bar}] {display_percent}% ({item.completed_q}/{item.total_q} Qs)")
                print(f"  Due:      {item.due_date.strftime('%b %d')} ({status_text})")

        elif isinstance(item, Assessment):
            bar_color   = PURPLE if percent >= 100 else (GREEN if days < 0 else BLUE)
            bar_content = "█" * (display_percent // 5)
            bar         = f"{bar_color}{bar_content.ljust(20, '-')}{RESET}"

            if view == 'compact':
                print(f"[Assess] {display_title:<25} | [{bar}] {display_percent:>3}% | {compact_time}")
            else:
                print(f"\n{BLUE}▶ {item.title.upper()} (Assessment){RESET}")
                print(f"  Study:    [{bar}] {display_percent}% ({item.hours_studied}/{item.target_hours} Hrs)")
                print(f"  Date:     {item.due_date.strftime('%b %d')} ({status_text})")

                # ── Burn-down nudge ──────────────────────────────────────────
                if days > 0 and percent < 100:
                    rec = item.recommended_daily_hours()
                    if rec is not None and rec > 0:
                        print(f"  Today:    ⚡ {rec} hrs recommended")

                # ── Last studied / neglect warning ───────────────────────────
                days_ago = item.last_studied_days_ago()
                if days_ago is None:
                    if days > 0:
                        print(f"  {YELLOW}⚠ No sessions logged yet{RESET}")
                else:
                    neglect = item.neglect_level()
                    if neglect == "alert":
                        label = f"{RED}⚠ Last studied {days_ago}d ago — overdue for a session!{RESET}"
                    elif neglect == "warn":
                        label = f"{YELLOW}⚠ Last studied {days_ago}d ago{RESET}"
                    else:
                        label = f"Last studied {days_ago}d ago"
                    print(f"  {label}")