import random
import gkeepapi
from config import KEEP_USER, MASTER_TOKEN

keep = gkeepapi.Keep()
keep.authenticate(KEEP_USER, MASTER_TOKEN)

def parse_keep_quote_text(text):
    return [q.strip() for q in text.split("\n\n") if q.strip()]

def get_keep_quotes(note_title="Wisdom"):
    for note in keep.all():
        if note.title == note_title:
            return parse_keep_quote_text(note.text)
    return []

def get_random_quote(note_title="Wisdom"):
    quotes = get_keep_quotes(note_title)
    return random.choice(quotes) if quotes else "No quotes found."
