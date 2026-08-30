import json
import random
from pathlib import Path
from auth.keep_client import (
    get_keep_quotes,
    add_keep_quote,
    delete_keep_quote,
    is_authenticated,
    sync_keep,
)

BASE_DIR = Path(__file__).resolve().parent.parent
CURRENT_QUOTE_FILE = BASE_DIR / "data" / "current_quote.json"
QUOTES_LIBRARY_FILE = BASE_DIR / "data" / "quotes.json"
DEBUG_QUOTE_LIST_FILE = BASE_DIR / "data" / "keep_quotes.txt"

DEFAULT_SEED_QUOTES = [
    "World belongs to those who can predict second order effects. - Kunal Shah",
    "The impediment to action advances action. What stands in the way becomes the way. - Marcus Aurelius",
    "Simplicity is prerequisite for reliability. - Edsger W. Dijkstra",
    "We suffer more often in imagination than in reality. - Seneca",
    "Focus is a muscle. The more you practice eliminating distraction, the stronger it gets.",
]


def load_local_quotes():
    """Load quotes from local storage, initializing if necessary."""
    if not QUOTES_LIBRARY_FILE.exists():
        QUOTES_LIBRARY_FILE.parent.mkdir(exist_ok=True)
        quotes = []
        if is_authenticated():
            quotes = get_keep_quotes()
        if not quotes:
            # Check if current_quote.json has a quote to preserve
            if CURRENT_QUOTE_FILE.exists():
                try:
                    with open(CURRENT_QUOTE_FILE, "r", encoding="utf-8") as f:
                        saved = json.load(f).get("quote")
                        if saved:
                            quotes.append(saved)
                except Exception:
                    pass
            for seed in DEFAULT_SEED_QUOTES:
                if seed not in quotes:
                    quotes.append(seed)
        save_local_quotes(quotes)
        return quotes

    try:
        with open(QUOTES_LIBRARY_FILE, "r", encoding="utf-8") as f:
            quotes = json.load(f)
            if isinstance(quotes, list) and quotes:
                return quotes
    except Exception as e:
        print(f"Error reading quotes library: {e}")

    return list(DEFAULT_SEED_QUOTES)


def save_local_quotes(quotes):
    """Save quote list safely to local json storage."""
    QUOTES_LIBRARY_FILE.parent.mkdir(exist_ok=True)
    with open(QUOTES_LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)


def get_all_quotes():
    """Return all quotes from local library, syncing with Keep if available."""
    local_quotes = load_local_quotes()
    return local_quotes


def save_current_quote(quote):
    """Save the currently displayed quote to data/current_quote.json."""
    CURRENT_QUOTE_FILE.parent.mkdir(exist_ok=True)
    with open(CURRENT_QUOTE_FILE, "w", encoding="utf-8") as f:
        json.dump({"quote": quote}, f, indent=2, ensure_ascii=False)


def set_current_quote(quote):
    """Set the active quote and ensure it is also in the library."""
    quote = quote.strip()
    if not quote:
        return False
    quotes = load_local_quotes()
    if quote not in quotes:
        quotes.append(quote)
        save_local_quotes(quotes)
    save_current_quote(quote)
    return True


def get_current_quote():
    """Get the currently displayed quote, or pick a random one if not found."""
    if CURRENT_QUOTE_FILE.exists():
        try:
            with open(CURRENT_QUOTE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                val = data.get("quote")
                if val:
                    return val
        except Exception:
            pass
    return get_and_save_random_quote()


def get_and_save_random_quote():
    """Fetch a random quote from Keep or local library and save it as current."""
    quotes = []
    if is_authenticated():
        keep_quotes = get_keep_quotes()
        if keep_quotes:
            # Sync local library with keep
            quotes = keep_quotes
            save_local_quotes(quotes)

    if not quotes:
        quotes = load_local_quotes()

    if not quotes:
        quotes = list(DEFAULT_SEED_QUOTES)

    quote = random.choice(quotes)
    save_current_quote(quote)
    return quote


def add_quote(quote_text, sync_keep_flag=True):
    """Add a new quote to local storage and Google Keep if connected."""
    quote_text = quote_text.strip()
    if not quote_text:
        return False, "Quote cannot be empty."

    quotes = load_local_quotes()
    if quote_text in quotes:
        return False, "Quote already exists in the library."

    quotes.append(quote_text)
    save_local_quotes(quotes)

    keep_synced = False
    if sync_keep_flag and is_authenticated():
        keep_synced = add_keep_quote(quote_text)

    return True, {"quote": quote_text, "keep_synced": keep_synced}


def delete_quote(quote_text, sync_keep_flag=True):
    """Delete a quote from local storage and Google Keep if connected."""
    quote_text = quote_text.strip()
    quotes = load_local_quotes()

    if quote_text not in quotes:
        return False, "Quote not found in library."

    quotes = [q for q in quotes if q != quote_text]
    save_local_quotes(quotes)

    keep_deleted = False
    if sync_keep_flag and is_authenticated():
        keep_deleted = delete_keep_quote(quote_text)

    # If current quote was deleted, rotate to another quote
    current = None
    if CURRENT_QUOTE_FILE.exists():
        try:
            with open(CURRENT_QUOTE_FILE, "r", encoding="utf-8") as f:
                current = json.load(f).get("quote")
        except Exception:
            pass

    if current == quote_text:
        get_and_save_random_quote()

    return True, {"quote": quote_text, "keep_deleted": keep_deleted}


def sync_with_google_keep():
    """Bidirectionally sync quotes with Google Keep."""
    if not is_authenticated():
        return False, "Google Keep is not configured or unauthenticated."

    try:
        sync_keep()
        keep_quotes = get_keep_quotes()
        local_quotes = load_local_quotes()

        # Merge keep quotes into local quotes
        merged = list(local_quotes)
        for kq in keep_quotes:
            if kq not in merged:
                merged.append(kq)

        save_local_quotes(merged)
        return True, {"count": len(merged), "keep_count": len(keep_quotes)}
    except Exception as e:
        return False, f"Sync error: {e}"


def get_keep_quote_list():
    """Return all quotes parsed from the Keep note."""
    if is_authenticated():
        return get_keep_quotes()
    return load_local_quotes()


def save_keep_quote_list(output_file=None):
    """Save the full list of quotes parsed from Keep/local to a text file."""
    quotes = get_keep_quote_list()
    output_path = Path(output_file) if output_file else DEBUG_QUOTE_LIST_FILE
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        if not quotes:
            f.write("No quotes found.\n")
        else:
            for index, quote in enumerate(quotes, start=1):
                f.write(f"{index}. {quote}\n\n")
    return str(output_path.resolve())
