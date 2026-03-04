import json
from pathlib import Path
from auth.keep_client import get_random_quote

BASE_DIR = Path(__file__).resolve().parent.parent
QUOTE_FILE = BASE_DIR / "data" / "current_quote.json"

def save_current_quote(quote):
    """Save the currently displayed quote"""
    QUOTE_FILE.parent.mkdir(exist_ok=True)
    with open(QUOTE_FILE, "w") as f:
        json.dump({"quote": quote}, f)

def get_current_quote():
    """Get the currently displayed quote, or fetch a new one if not found"""
    if QUOTE_FILE.exists():
        try:
            with open(QUOTE_FILE, "r") as f:
                data = json.load(f)
                return data.get("quote", get_random_quote())
        except:
            return get_random_quote()
    return get_random_quote()

def get_and_save_random_quote():
    """Fetch a random quote and save it as current"""
    quote = get_random_quote()
    save_current_quote(quote)
    return quote
