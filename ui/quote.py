from services.quote_service import get_and_save_random_quote
from utils.scheduler import schedule_next_update

def update_quote(root, label):
    quote = get_and_save_random_quote()
    label.config(text=quote)
    schedule_next_update(root, 9, lambda: update_quote(root, label))


def apply_quote_text(label, text):
    label.config(text=text)