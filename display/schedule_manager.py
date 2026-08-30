"""One authoritative set of automatic display-transition jobs."""

from services.dashboard_settings import load_settings
from utils.scheduler import schedule_next_update


class DisplayScheduleManager:
    def __init__(self, root, wake, dim, sleep):
        self.root = root
        self.wake = wake
        self.dim = dim
        self.sleep = sleep
        self._jobs = []

    def rebuild(self):
        self.cancel()
        settings = load_settings()
        if not settings["automation_enabled"]:
            return
        schedule = settings["schedule"]
        self._jobs = [
            schedule_next_update(self.root, schedule["wake"], self._run(self.wake)),
            schedule_next_update(self.root, schedule["dim"], self._run(self.dim)),
            schedule_next_update(self.root, schedule["sleep"], self._run(self.sleep)),
        ]

    def cancel(self):
        for job in self._jobs:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        self._jobs = []

    def _run(self, action):
        def callback():
            action()
            self.rebuild()
        return callback
