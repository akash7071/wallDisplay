import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "data" / "media"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

def ensure_media_dir():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def list_media():
    ensure_media_dir()
    media_files = []
    for f in MEDIA_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS:
            media_files.append({
                "filename": f.name,
                "type": "gif" if f.suffix.lower() == ".gif" else "image"
            })
    return media_files

def get_random_media():
    files = list_media()
    if not files:
        return None
    return random.choice(files)["filename"]

def delete_media(filename):
    file_path = MEDIA_DIR / filename
    if file_path.exists() and file_path.parent == MEDIA_DIR:
        file_path.unlink()
        return True
    return False

def save_media(file_storage, filename):
    ensure_media_dir()
    path = MEDIA_DIR / filename
    file_storage.save(path)
    return filename
