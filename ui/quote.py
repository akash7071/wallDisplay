from auth.keep_client import get_random_quote
from utils.scheduler import schedule_next_update

def update_quote(root, label):
    label.config(text=get_random_quote())
    schedule_next_update(root, 9, lambda: update_quote(root, label))
