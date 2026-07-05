import json
from pathlib import Path
from auth.keep_client import get_random_quote, get_keep_quotes

BASE_DIR = Path(__file__).resolve().parent.parent
QUOTE_FILE = BASE_DIR / "data" / "current_quote.json"
DEBUG_QUOTE_LIST_FILE = BASE_DIR / "data" / "keep_quotes.txt"

def save_current_quote(quote):
    """Save the currently displayed quote"""
    QUOTE_FILE.parent.mkdir(exist_ok=True)
    with open(QUOTE_FILE, "w", encoding="utf-8") as f:
        json.dump({"quote": quote}, f)

def get_current_quote():
    """Get the currently displayed quote, or fetch a new one if not found"""
    if QUOTE_FILE.exists():
        try:
            with open(QUOTE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("quote", get_random_quote())
        except:
            return get_random_quote()
    return get_random_quote()

def get_keep_quote_list():
    """Return all quotes parsed from the Keep note."""
    return get_keep_quotes()

def save_keep_quote_list(output_file=None):
    """Save the full list of quotes parsed from the Keep note."""
    quotes = get_keep_quotes()
    output_path = Path(output_file) if output_file else DEBUG_QUOTE_LIST_FILE
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        if not quotes:
            f.write("No quotes found or note not found.\n")
        else:
            for index, quote in enumerate(quotes, start=1):
                f.write(f"{index}. {quote}\n\n")
    return str(output_path.resolve())

def get_and_save_random_quote():
    """Fetch a random quote and save it as current"""
    quote = get_random_quote()
    save_current_quote(quote)
    return quote
