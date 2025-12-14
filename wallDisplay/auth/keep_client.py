import random
import gkeepapi
from config import KEEP_USER, MASTER_TOKEN

keep = gkeepapi.Keep()
keep.authenticate(KEEP_USER, MASTER_TOKEN)

def get_random_quote(note_title="Wisdom"):
    for note in keep.all():
        if note.title == note_title:
            quotes = [q.strip() for q in note.text.split("\n\n") if q.strip()]
            return random.choice(quotes) if quotes else "No quotes found."
    return "Note not found."
