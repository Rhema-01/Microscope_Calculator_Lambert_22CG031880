# Microscope Specimen Size Calculator
**CSC 442 — Project 1**  
Department of Computer Science | Faculty of Physical Sciences | 2024/2025

---

## Project Structure

```
microscope_project/
├── phase_a_calculator.py   ← Phase A: Command-line core calculator
├── phase_b_database.py     ← Phase B: CLI + SQLite database
├── phase_c_gui.py          ← Phase C: Python Tkinter GUI
├── app.py                  ← Phase D/E: Flask web application
├── wsgi.py                 ← Production WSGI entry point
├── requirements.txt        ← Python dependencies
├── Procfile                ← For Render/Railway hosting
├── instance/
│   └── calculations.db     ← SQLite database (auto-created)
├── templates/
│   ├── index.html          ← Main calculator page
│   └── history.html        ← Records/history page
└── static/
    ├── css/style.css       ← Stylesheet
    ├── js/main.js          ← Frontend JavaScript
    └── uploads/            ← Uploaded specimen images
```

---

## Running Each Phase

### Phase A — Command-Line Calculator
```bash
python phase_a_calculator.py
```
- Enter measured size in mm
- Choose microscope type from numbered menu
- Choose output unit from numbered menu
- Result and full breakdown are displayed

---

### Phase B — CLI with Database
```bash
python phase_b_database.py
```
- Enter username first
- Menu-driven: calculate, view history, delete records
- Saves all calculations to `instance/calculations.db`

---

### Phase C — Python GUI (Tkinter)
```bash
# Install dependency first:
pip install pillow

python phase_c_gui.py
```
- Full graphical interface
- Browse and preview specimen images
- Dropdown selectors for microscope type and unit
- Calculator and History tabs

---

### Phase D/E — Web Application (Flask)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run locally:**
```bash
python app.py
```
Then open your browser to: **http://127.0.0.1:5000**

---

## Hosting on the Internet (Phase E)

### Option 1: Render (Recommended — Free)
1. Push your project folder to a GitHub repository
2. Go to https://render.com and sign up
3. Click **New → Web Service**
4. Connect your GitHub repo
5. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
6. Click **Create Web Service**
7. Your public URL will be shown once deployed (e.g. `https://yourapp.onrender.com`)

### Option 2: Railway
1. Go to https://railway.app and sign up
2. Click **New Project → Deploy from GitHub**
3. Connect your repo — Railway auto-detects `Procfile`
4. Your URL appears in the dashboard

---

## Scientific Formula

```
Real Size = Measured Size (mm) ÷ Magnification Factor
```

| Microscope Type                      | Magnification |
|--------------------------------------|---------------|
| Stereo / Dissecting Microscope       | ×20           |
| Light Microscope (Low Power)         | ×40           |
| Light Microscope (Medium Power)      | ×100          |
| Light Microscope (High Power)        | ×400          |
| Confocal Microscope                  | ×600          |
| Light Microscope (Oil Immersion)     | ×1,000        |
| Scanning Electron Microscope (SEM)   | ×10,000       |
| Transmission Electron Microscope (TEM) | ×50,000     |

---

## Marking Scheme Coverage

| Component | Marks | What's implemented |
|-----------|-------|--------------------|
| (a) Core Calculation | 20 | `phase_a_calculator.py` — formula, dropdown selection, unit conversion, breakdown display, input validation |
| (b) Database | 15 | `phase_b_database.py` — SQLite, stores username/measured/real size, view and delete records |
| (c) Python GUI | 20 | `phase_c_gui.py` — Tkinter with all required fields, image upload+preview, dropdowns, result display, history tab |
| (d) Web GUI | 25 | `app.py` + templates — full Flask web app replicating all GUI functionality |
| (e) Hosting | 15 | `Procfile` + `wsgi.py` — deploy to Render or Railway via GitHub |
| Code Quality | 5 | Commented, logical structure, clean UX |
| **Total** | **100** | |
