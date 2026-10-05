from datetime import datetime

NEGLECT_WARN_DAYS  = 4   # yellow warning after this many days without study
NEGLECT_ALERT_DAYS = 7   # red alert after this many days without study

class AcademicItem:
    def __init__(self, title, date_str, item_type):
        self.title = title
        self.date_str = date_str
        self.item_type = item_type
        self.archived = False
        try:
            self.due_date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            self.due_date = datetime.now()

    def get_days_left(self):
        delta = self.due_date - datetime.now()
        return delta.days

class Assignment(AcademicItem):
    def __init__(self, title, due_date_str, total_q, completed_q=0, archived=False):
        super().__init__(title, due_date_str, "assignment")
        self.total_q = total_q
        self.completed_q = int(completed_q)
        self.archived = archived

    def to_dict(self):
        return {
            "type": self.item_type,
            "title": self.title,
            "date_str": self.date_str,
            "total_q": self.total_q,
            "completed_q": self.completed_q,
            "archived": self.archived
        }

class Assessment(AcademicItem):
    def __init__(self, title, test_date_str, target_hours=10, hours_studied=0,
                 sessions=None, archived=False):
        super().__init__(title, test_date_str, "assessment")
        self.target_hours  = float(target_hours)
        self.hours_studied = float(hours_studied)
        # sessions: list of {"date": "YYYY-MM-DD", "hours": float}
        self.sessions = sessions if sessions is not None else []
        self.archived = archived

    # ── Derived helpers ──────────────────────────────────────────────────────

    def last_studied_days_ago(self):
        """Return how many days ago the last session was, or None if no sessions."""
        if not self.sessions:
            return None
        latest = max(datetime.strptime(s["date"], "%Y-%m-%d") for s in self.sessions)
        return (datetime.now() - latest).days

    def neglect_level(self):
        """Return 'alert', 'warn', or None based on days since last session."""
        days_ago = self.last_studied_days_ago()
        if days_ago is None:
            return None
        if days_ago >= NEGLECT_ALERT_DAYS:
            return "alert"
        if days_ago >= NEGLECT_WARN_DAYS:
            return "warn"
        return None

    def recommended_daily_hours(self):
        """Hours per day needed to hit target before the exam."""
        days_left = self.get_days_left()
        if days_left <= 0:
            return None
        remaining = self.target_hours - self.hours_studied
        if remaining <= 0:
            return 0.0
        return round(remaining / days_left, 1)

    def log_session(self, hours):
        """Add a study session for today and update hours_studied."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.sessions.append({"date": today, "hours": float(hours)})
        self.hours_studied += float(hours)

    def to_dict(self):
        return {
            "type": self.item_type,
            "title": self.title,
            "date_str": self.date_str,
            "target_hours": self.target_hours,
            "hours_studied": self.hours_studied,
            "sessions": self.sessions,
            "archived": self.archived
        }
