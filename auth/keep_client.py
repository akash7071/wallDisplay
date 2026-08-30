import random
from config import KEEP_USER, MASTER_TOKEN

try:
    import gkeepapi
except ImportError:
    gkeepapi = None

_keep = None
_authenticated = False


def get_keep():
    global _keep, _authenticated
    if gkeepapi is None:
        return None
    if _keep is None:
        try:
            _keep = gkeepapi.Keep()
        except Exception as e:
            print(f"Error initializing gkeepapi: {e}")
            return None
    if not _authenticated and KEEP_USER and MASTER_TOKEN:
        try:
            _keep.authenticate(KEEP_USER, MASTER_TOKEN)
            _authenticated = True
            print("Google Keep authenticated successfully.")
        except Exception as e:
            print(f"Google Keep authentication error: {e}")
            _authenticated = False
    return _keep


def is_authenticated():
    global _authenticated
    if gkeepapi is None:
        return False
    if not _authenticated and KEEP_USER and MASTER_TOKEN:
        get_keep()
    return _authenticated


def parse_keep_quote_text(text):
    if not text:
        return []
    return [q.strip() for q in text.split("\n\n") if q.strip()]


def get_keep_note(note_title="Wisdom"):
    if not is_authenticated():
        return None
    try:
        keep = get_keep()
        if not keep:
            return None
        for note in keep.all():
            if note.title == note_title and not note.trashed:
                return note
    except Exception as e:
        print(f"Error fetching Google Keep note: {e}")
    return None


def get_keep_quotes(note_title="Wisdom"):
    if not is_authenticated():
        return []
    try:
        note = get_keep_note(note_title)
        if note:
            return parse_keep_quote_text(note.text)
    except Exception as e:
        print(f"Error reading Keep quotes: {e}")
    return []


def get_random_quote(note_title="Wisdom"):
    quotes = get_keep_quotes(note_title)
    return random.choice(quotes) if quotes else None


def add_keep_quote(quote_text, note_title="Wisdom"):
    if not is_authenticated():
        return False
    try:
        keep = get_keep()
        if not keep:
            return False
        note = get_keep_note(note_title)
        quote_text = quote_text.strip()
        if not quote_text:
            return False

        if note is None:
            note = keep.createNote(note_title, quote_text)
        else:
            current_quotes = parse_keep_quote_text(note.text)
            if quote_text not in current_quotes:
                current_quotes.append(quote_text)
                note.text = "\n\n".join(current_quotes)
        keep.sync()
        return True
    except Exception as e:
        print(f"Error adding quote to Google Keep: {e}")
        return False


def delete_keep_quote(quote_text, note_title="Wisdom"):
    if not is_authenticated():
        return False
    try:
        keep = get_keep()
        if not keep:
            return False
        note = get_keep_note(note_title)
        if not note:
            return False

        current_quotes = parse_keep_quote_text(note.text)
        quote_text = quote_text.strip()
        updated_quotes = [q for q in current_quotes if q != quote_text]

        if len(updated_quotes) != len(current_quotes):
            note.text = "\n\n".join(updated_quotes)
            keep.sync()
            return True
        return False
    except Exception as e:
        print(f"Error deleting quote from Google Keep: {e}")
        return False


def sync_keep():
    if not is_authenticated():
        return False
    try:
        keep = get_keep()
        if not keep:
            return False
        keep.sync()
        return True
    except Exception as e:
        print(f"Google Keep sync error: {e}")
        return False
