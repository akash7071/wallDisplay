# Wall Display & Control Panel

A smart ambient wall display kiosk built with Python (**Tkinter**) paired with a local HTTPS web-based control panel (**Flask**). It shows real-time time/date, daily inspirational quotes synced from Google Keep, live weather conditions, dynamic footer schedules, and provides full hardware display controls via DDC/CI (`ddcutil`).

---

## 📋 Feature Status & Roadmap Checklist

This checklist tracks current implementation status and serves as a handoff guide for future development.

### 1. Dashboard (Overview & Telemetry)
| Feature | Status | Location / Implementation Details |
| :--- | :---: | :--- |
| **Current Time & Date** | ✅ Completed | Displayed live in Web Dashboard via `/api/dashboard/status` (`server_time`) and on the Tkinter screen. |
| **Current Quote** | ✅ Completed | Live quote shown on dashboard, standalone `/quote` web page, and desktop screen. |
| **Weather Status** | ✅ Completed | Temperature, condition icons, and timestamp fetched from OpenWeather API cache. |
| **Display Status** | ✅ Completed | Shows operational status (`active` / `sleeping`) and physical screen power state (`on` / `off`). |
| **Brightness Readout** | ✅ Completed | Real-time percentage display of current brightness level. |
| **Current Mode** | ✅ Completed | Displays current mode (`day`, `dim`, or `sleep`). |

---

### 2. Display Controls & Scheduling
| Feature | Status | Location / Implementation Details |
| :--- | :---: | :--- |
| **Brightness Slider** | ✅ Completed | Interactive `0–100%` slider in dashboard (`POST /api/dashboard/display/brightness`) dispatching to `ddcutil`. |
| **Display Power (On/Off)** | ✅ Completed | Power On/Off buttons (`POST /api/dashboard/display/power`) sending DDC VCP commands (`0x01` / `0x04`). |
| **Sleep / Wake Modes** | ✅ Completed | Manual "Wake" and "Sleep" buttons (`POST /api/dashboard/display/mode`) with screen recoloring. |
| **Wake / Sleep Schedule** | ✅ Completed | Web UI schedule pickers persisted to `data/dashboard_settings.json` and dynamically managed by `DisplayScheduleManager`. |
| **Dim Schedule** | ✅ Completed | Evening dim transition time configurable via dashboard schedule inputs. |
| **Automation Toggle** | ✅ Completed | Master toggle to enable/disable automated schedule transitions. |

---

### 3. Widgets
| Feature | Status | Location / Implementation Details |
| :--- | :---: | :--- |
| **Enable/Disable Clock** | ✅ Completed | Toggle in web dashboard (`POST /api/dashboard/widgets/clock`); dynamically packs/unpacks Tkinter clock widget. |
| **Enable/Disable Quote** | ✅ Completed | Toggle in web dashboard (`POST /api/dashboard/widgets/quote`); packs/unpacks center quote widget. |
| **Enable/Disable Weather** | ✅ Completed | Toggle in web dashboard (`POST /api/dashboard/widgets/weather`); shows/hides weather container. |
| **Enable/Disable Counters** | ⏸️ Deprecated | Counter widget toggling is implemented but feature is deprioritized (see Counters section). |
| **Configure Widget Order** | 📋 Planned | Currently widget layout is fixed (Weather: NW, Clock: NE, Quote: Center, Footer: SE). Need drag-and-drop or position selector in UI + layout engine in `ui/app.py`. |

---

### 4. Quotes
| Feature | Status | Location / Implementation Details |
| :--- | :---: | :--- |
| **View Active Quote** | ✅ Completed | Shown on web dashboard, `/quote`, and Tkinter UI. |
| **Browser Push Notifications** | ✅ Completed | Web notification support implemented on `/quote` with hourly refresh options. |
| **View All Quotes Library** | ⚠️ Partial | CLI export supported via `python main.py quote_list=true` (`save_keep_quote_list()`). Web browsing page/modal for quote collection is not yet built. |
| **Add / Delete Quotes** | 📋 Planned | Quotes are currently read-only via Google Keep note ("Wisdom"). Needs web UI forms to add/remove quotes directly or via Google Keep API. |
| **Google Keep Configuration UI** | 📋 Planned | `KEEP_USER` and `MASTER_TOKEN` are loaded from `.env`. Needs a secure settings form in the web UI. |

---

### 5. Counters & Habit Tracker (Out of Scope)
> [!NOTE]
> Counter features are marked as **Out of Scope / Deprecated** and do not need further implementation.

| Feature | Status | Notes |
| :--- | :---: | :--- |
| **View Counters** | ⏸️ Deprecated | Basic UI exists at `/counters` and in desktop widget. |
| **Reset / Mark Done** | ⏸️ Deprecated | Working on `/counters` and via `/mark_done` webhook. |
| **Add / Remove Counters** | ⏸️ Deprecated | Out of scope. |
| **View History Log** | ⏸️ Deprecated | Logged to `data/history.json`; frontend view not needed. |

---

### 6. Settings & Configuration
| Feature | Status | Location / Implementation Details |
| :--- | :---: | :--- |
| **Weather Unit (Imperial / Metric)** | ✅ Completed | Switchable between Fahrenheit (°F) and Celsius (°C) in web dashboard. |
| **Sleep / Wake / Dim Schedule** | ✅ Completed | Configurable directly in the dashboard UI. |
| **City & Country Settings** | 📋 Planned | Statically defined in `.env` (`CITY_NAME`, `COUNTRY_CODE`). Needs web UI input fields with auto-reload. |
| **OpenWeather API Key** | 📋 Planned | Configured in `.env` (`OPENWEATHER_API_KEY`). Needs web configuration field. |
| **Preset Brightness Levels** | 📋 Planned | Day/Dim/Sleep presets (`BRIGHTNESS_DAY`, `BRIGHTNESS_EVENING`, `BRIGHTNESS_SLEEP`) hardcoded in `config.py`. |
| **Footer Text Customization** | 📋 Planned | Alternating bi-weekly footer text (`FOOTER_TEXT_LINE1/2`) hardcoded in `.env`/`config.py`. |

---

## 🏗️ Architecture & Project Structure

The project uses a hybrid architecture:
1. **Tkinter Desktop App (`main.py`)**: Runs on the primary display thread in fullscreen kiosk mode.
2. **Flask HTTPS Server (`web_logger.py`)**: Runs in a background daemon thread on port `8000`.
3. **Thread-Safe Inter-Process Communication**: The web server pushes commands onto `display.web_commands.command_queue`. Tkinter periodically drains this queue on its main thread via `apply_dashboard_commands()` every 150ms.
4. **Persistent Settings**: Dashboard state (widgets, schedules, weather units, automation) is saved in `data/dashboard_settings.json`.

```
wallDisplay/
├── auth/
│   └── keep_client.py         # Google Keep API connection (gkeepapi)
├── data/                      # Persistent state and cache files
│   ├── current_quote.json
│   ├── dashboard_settings.json
│   ├── counters.json
│   └── history.json
├── display/
│   ├── brightness.py          # DDC/CI brightness control (ddcutil)
│   ├── modes.py               # Day, Dim, and Sleep UI modes and coloring
│   ├── power.py               # DDC/CI monitor power control (DPMS/VCP)
│   ├── runtime_state.py       # In-memory display state tracker
│   ├── schedule_manager.py    # Auto-schedule timer manager
│   └── web_commands.py        # Thread-safe queue between Flask & Tkinter
├── services/
│   ├── dashboard_settings.py  # Read/write for dashboard_settings.json
│   ├── quote_service.py       # Quote caching and extraction
│   └── weather_service.py     # OpenWeatherMap API fetcher
├── templates/
│   ├── dashboard.html         # Main Web Control Panel
│   ├── quote.html             # Quote & notification web interface
│   └── counters.html          # Legacy counters page
├── ui/
│   ├── app.py                 # Main Tkinter root window and layout
│   ├── clock.py               # Time and date display
│   ├── quote.py               # Center quote widget
│   ├── weather.py             # Weather icon and forecast renderer
│   └── counters_widget.py     # Desktop counters widget
├── utils/
│   └── scheduler.py           # Tkinter .after() scheduling helper
├── config.py                  # Environment variable loader and defaults
├── main.py                    # Application entrypoint
├── web_logger.py              # Flask app & API routing
├── cert.pem / key.pem         # Self-signed TLS certificate for HTTPS
├── requirements.txt           # Python dependencies
└── .env.example               # Example environment configuration
```

---

## 🔌 Web API Endpoints

The Flask server (`https://<ip>:8000`) exposes the following endpoints:

### Status & Telemetry
- `GET /api/dashboard/status`: Returns current server time, quote, weather, display power/brightness/mode, schedules, and widget visibility.
- `GET /api/send_quote_notification`: JSON endpoint returning active quote for browser push notifications.

### Display Controls
- `POST /api/dashboard/display/brightness`: Body: `{"brightness": 0-100}`
- `POST /api/dashboard/display/power`: Body: `{"power": "on" | "off"}`
- `POST /api/dashboard/display/mode`: Body: `{"mode": "wake" | "sleep"}`

### Schedules & Automation
- `POST /api/dashboard/schedule`: Body: `{"schedule": {"wake": "HH:MM", "dim": "HH:MM", "sleep": "HH:MM"}}`
- `POST /api/dashboard/automation`: Body: `{"enabled": true | false}`

### Widgets & Preferences
- `POST /api/dashboard/widgets/<clock|quote|weather|counters>`: Body: `{"enabled": true | false}`
- `POST /api/dashboard/weather/units`: Body: `{"units": "imperial" | "metric"}`

---

## 🚀 Setup & Development

### 1. Requirements
- Python 3.9+
- Linux with `ddcutil` (for Raspberry Pi / Linux wall kiosks) or Windows/macOS for development.

### 2. Installation
```bash
# Clone the repository and enter directory
cd wallDisplay

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (based on `.env.example`):
```env
# Weather (OpenWeatherMap API)
OPENWEATHER_API_KEY=your_openweather_api_key
CITY_NAME=YourCity
COUNTRY_CODE=US

# Google Keep (Quotes)
KEEP_USER=your_google_email@gmail.com
MASTER_TOKEN=your_oauth_master_token

# Optional Footer Text
FOOTER_TEXT_LINE1="A Ba T"
FOOTER_TEXT_LINE2="S Bi C"
```

### 4. Running the Display
```bash
python main.py
```
- The **Tkinter Display** will launch in full screen. (Press `Esc` to exit).
- The **Web Control Panel** will start on `https://<device-ip>:8000`.

---

## 💡 Guide for Future Contributors

When picking up development on the remaining roadmap items:

1. **Quote Management (Web UI)**:
   - Add routes in `web_logger.py` to list all quotes from `keep_client.get_keep_quotes()` and add/delete entries.
   - Add a "Quotes" tab/modal in `templates/dashboard.html`.

2. **Widget Reordering**:
   - Store layout slots in `data/dashboard_settings.json` (e.g. `{"slots": {"top_left": "weather", "top_right": "clock", ...}}`).
   - Update `ui/app.py` to place widgets dynamically based on the configured slot mapping rather than fixed coordinates.

3. **Web Settings Panel (`.env` Editor)**:
   - Create an endpoint `POST /api/dashboard/settings` to update `CITY_NAME`, `COUNTRY_CODE`, `OPENWEATHER_API_KEY`, etc.
   - Trigger a reload in `services/weather_service.py` when weather location changes.
