"""Thread-safe commands submitted by the dashboard and consumed by Tk."""

from queue import Queue

command_queue = Queue()
