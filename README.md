# Wall Display

## Dashboard setup (Phase 1)

The dashboard is read-only in this phase. It shows the current time, quote,
cached weather, display mode, brightness, and configured schedule. It is
currently open to devices on your local network; password protection can be
added later, before display controls are introduced.

1. Install dependencies: `python -m pip install -r requirements.txt`
2. Copy any desired existing settings from `.env.example` into a new `.env`
   file.
3. Start the display as usual: `python main.py`
4. From a device on the same Wi-Fi/LAN, open `https://<display-ip>:8000`.

The bundled certificate is self-signed, so your browser will show a one-time
certificate warning. Only continue when using the address of your own display
on your trusted local network.

On Windows, run `ipconfig` on the display computer and use its IPv4 address,
for example `https://192.168.1.50:8000`.
