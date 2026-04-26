"""
Phase D & E: Web-Based GUI using Flask
Full web application with all Phase A-B functionality.
CSC 442 - Project 1
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "calculations.db")

MICROSCOPE_TYPES = {
    "Light Microscope (Low Power)":               40,
    "Light Microscope (Medium Power)":           100,
    "Light Microscope (High Power)":             400,
    "Light Microscope (Oil Immersion)":         1000,
    "Stereo / Dissecting Microscope":             20,
    "Scanning Electron Microscope (SEM)":      10000,
    "Transmission Electron Microscope (TEM)": 50000,
    "Confocal Microscope":                       600,
}

UNIT_CONVERSIONS = {
    "nm":  1_000_000,
    "µm":  1_000,
    "mm":  1,
    "cm":  0.1,
    "m":   0.001,
}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}


# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    NOT NULL,
            microscope_type TEXT    NOT NULL,
            magnification   INTEGER NOT NULL,
            measured_size   REAL    NOT NULL,
            real_size_mm    REAL    NOT NULL,
            output_unit     TEXT    NOT NULL,
            real_size_disp  REAL    NOT NULL,
            image_filename  TEXT,
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html",
                           microscopes=list(MICROSCOPE_TYPES.keys()),
                           units=list(UNIT_CONVERSIONS.keys()))


@app.route("/calculate", methods=["POST"])
def calculate():
    username     = request.form.get("username", "").strip()
    measured_str = request.form.get("measured_size", "").strip()
    mic_name     = request.form.get("microscope_type", "")
    unit_name    = request.form.get("output_unit", "")

    errors = []
    if not username:
        errors.append("Username is required.")
    if not measured_str:
        errors.append("Measured size is required.")
    else:
        try:
            measured_mm = float(measured_str)
            if measured_mm <= 0:
                errors.append("Measured size must be a positive number.")
        except ValueError:
            errors.append("Measured size must be a valid number.")
    if mic_name not in MICROSCOPE_TYPES:
        errors.append("Invalid microscope type.")
    if unit_name not in UNIT_CONVERSIONS:
        errors.append("Invalid output unit.")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    measured_mm    = float(measured_str)
    magnification  = MICROSCOPE_TYPES[mic_name]
    unit_factor    = UNIT_CONVERSIONS[unit_name]
    real_size_mm   = measured_mm / magnification
    real_size_disp = real_size_mm * unit_factor

    # Handle image upload
    image_filename = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename and allowed_file(file.filename):
            import uuid
            ext = file.filename.rsplit(".", 1)[1].lower()
            image_filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

    # Save to DB
    conn = get_db()
    conn.execute("""
        INSERT INTO calculations
            (username, microscope_type, magnification, measured_size,
             real_size_mm, output_unit, real_size_disp, image_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, mic_name, magnification, measured_mm,
          real_size_mm, unit_name, real_size_disp, image_filename))
    conn.commit()
    conn.close()

    return jsonify({
        "success":       True,
        "username":      username,
        "mic_name":      mic_name,
        "magnification": magnification,
        "measured_mm":   measured_mm,
        "real_size_mm":  real_size_mm,
        "real_size_disp": real_size_disp,
        "unit_name":     unit_name,
        "image_url":     f"/static/uploads/{image_filename}" if image_filename else None,
    })


@app.route("/history")
def history():
    conn = get_db()
    records = conn.execute("""
        SELECT id, username, microscope_type, magnification,
               measured_size, real_size_disp, output_unit,
               image_filename, timestamp
        FROM calculations ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return render_template("history.html", records=records)


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = get_db()
    row = conn.execute("SELECT image_filename FROM calculations WHERE id = ?",
                       (record_id,)).fetchone()
    if row and row["image_filename"]:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], row["image_filename"])
        if os.path.exists(img_path):
            os.remove(img_path)
    conn.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
