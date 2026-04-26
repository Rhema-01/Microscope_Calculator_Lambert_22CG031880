"""
Phase C: Python-Based GUI
Extends Phase B with a full Tkinter GUI.
CSC 442 - Project 1
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
from PIL import Image, ImageTk

# ── Constants (same as Phase A) ───────────────────────────────────────────────

MICROSCOPE_TYPES = {
    "Light Microscope (Low Power)":            40,
    "Light Microscope (Medium Power)":        100,
    "Light Microscope (High Power)":          400,
    "Light Microscope (Oil Immersion)":      1000,
    "Stereo / Dissecting Microscope":          20,
    "Scanning Electron Microscope (SEM)":   10000,
    "Transmission Electron Microscope (TEM)": 50000,
    "Confocal Microscope":                    600,
}

UNIT_CONVERSIONS = {
    "nm":  1_000_000,
    "µm":  1_000,
    "mm":  1,
    "cm":  0.1,
    "m":   0.001,
}

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "calculations.db")

# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_record(username, microscope_name, magnification,
                measured_mm, real_size_mm, unit_name, real_size_disp):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO calculations
            (username, microscope_type, magnification,
             measured_size, real_size_mm, output_unit, real_size_disp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, microscope_name, magnification,
          measured_mm, real_size_mm, unit_name, real_size_disp))
    conn.commit()
    conn.close()

def fetch_all_records():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT id, username, microscope_type, measured_size,
               real_size_disp, output_unit, timestamp
        FROM calculations ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return rows

def delete_record_db(record_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# ── Main App ──────────────────────────────────────────────────────────────────

class MicroscopeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Microscope Specimen Size Calculator — Phase C")
        self.geometry("850x680")
        self.resizable(True, True)
        self.configure(bg="#f0f4f8")
        init_db()
        self._build_ui()

    # ── UI Builder ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1a3c5e", pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔬  Microscope Specimen Size Calculator",
                 font=("Helvetica", 16, "bold"), bg="#1a3c5e", fg="white").pack()
        tk.Label(header, text="CSC 442 — Computational Biology  |  Phase C",
                 font=("Helvetica", 9), bg="#1a3c5e", fg="#aecde8").pack()

        # Notebook (tabs)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        self._build_calc_tab()
        self._build_history_tab()

    def _build_calc_tab(self):
        tab = ttk.Frame(self.nb, padding=16)
        self.nb.add(tab, text="  Calculator  ")

        # --- Username ---
        row0 = tk.Frame(tab, bg="#f0f4f8"); row0.pack(fill=tk.X, pady=4)
        tk.Label(row0, text="Username:", width=18, anchor="w", bg="#f0f4f8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.username_var = tk.StringVar()
        tk.Entry(row0, textvariable=self.username_var, font=("Helvetica", 10),
                 width=28).pack(side=tk.LEFT, padx=4)

        # --- Image upload ---
        row1 = tk.Frame(tab, bg="#f0f4f8"); row1.pack(fill=tk.X, pady=4)
        tk.Label(row1, text="Specimen Image:", width=18, anchor="w", bg="#f0f4f8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.img_path_var = tk.StringVar(value="No image selected")
        tk.Label(row1, textvariable=self.img_path_var, fg="#555",
                 font=("Helvetica", 9), bg="#f0f4f8", width=40,
                 anchor="w").pack(side=tk.LEFT, padx=4)
        tk.Button(row1, text="Browse…", command=self._browse_image,
                  bg="#1a3c5e", fg="white", font=("Helvetica", 9)).pack(side=tk.LEFT)

        # Image preview
        self.img_label = tk.Label(tab, bg="#e0e8f0", width=60, height=10,
                                  relief=tk.SUNKEN, text="Image preview will appear here",
                                  font=("Helvetica", 9), fg="#888")
        self.img_label.pack(pady=6, fill=tk.X)

        # --- Measured size ---
        row2 = tk.Frame(tab, bg="#f0f4f8"); row2.pack(fill=tk.X, pady=4)
        tk.Label(row2, text="Measured Size (mm):", width=18, anchor="w", bg="#f0f4f8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.size_var = tk.StringVar()
        tk.Entry(row2, textvariable=self.size_var, font=("Helvetica", 10),
                 width=14).pack(side=tk.LEFT, padx=4)

        # --- Microscope type ---
        row3 = tk.Frame(tab, bg="#f0f4f8"); row3.pack(fill=tk.X, pady=4)
        tk.Label(row3, text="Microscope Type:", width=18, anchor="w", bg="#f0f4f8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.mic_var = tk.StringVar()
        mic_cb = ttk.Combobox(row3, textvariable=self.mic_var,
                              values=list(MICROSCOPE_TYPES.keys()),
                              state="readonly", width=40)
        mic_cb.pack(side=tk.LEFT, padx=4)
        mic_cb.current(0)

        # --- Output unit ---
        row4 = tk.Frame(tab, bg="#f0f4f8"); row4.pack(fill=tk.X, pady=4)
        tk.Label(row4, text="Output Unit:", width=18, anchor="w", bg="#f0f4f8",
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.unit_var = tk.StringVar()
        unit_cb = ttk.Combobox(row4, textvariable=self.unit_var,
                               values=list(UNIT_CONVERSIONS.keys()),
                               state="readonly", width=10)
        unit_cb.pack(side=tk.LEFT, padx=4)
        unit_cb.current(1)  # default µm

        # --- Calculate button ---
        tk.Button(tab, text="⚗  Calculate Real Size", command=self._calculate,
                  bg="#27ae60", fg="white", font=("Helvetica", 11, "bold"),
                  pady=8, relief=tk.FLAT).pack(fill=tk.X, pady=10)

        # --- Result display ---
        tk.Label(tab, text="Result & Breakdown:", font=("Helvetica", 10, "bold"),
                 bg="#f0f4f8", anchor="w").pack(fill=tk.X)
        self.result_text = tk.Text(tab, height=8, font=("Courier", 10),
                                   bg="#1e2d3d", fg="#00ff99",
                                   relief=tk.SUNKEN, padx=8, pady=6,
                                   state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=4)

    def _build_history_tab(self):
        tab = ttk.Frame(self.nb, padding=12)
        self.nb.add(tab, text="  History & Records  ")

        top = tk.Frame(tab); top.pack(fill=tk.X, pady=4)
        tk.Button(top, text="↻ Refresh", command=self._refresh_history,
                  bg="#1a3c5e", fg="white", font=("Helvetica", 9)).pack(side=tk.LEFT)
        tk.Button(top, text="🗑 Delete Selected", command=self._delete_selected,
                  bg="#c0392b", fg="white", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=8)

        cols = ("ID", "Username", "Microscope", "Measured (mm)", "Real Size", "Unit", "Timestamp")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")
        widths = [40, 100, 240, 110, 110, 60, 160]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=4)

        sb = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_history()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title="Select Specimen Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                       ("All files", "*.*")]
        )
        if not path:
            return
        self.img_path_var.set(os.path.basename(path))
        try:
            img = Image.open(path)
            img.thumbnail((600, 200))
            self._tk_img = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self._tk_img, text="")
        except Exception as e:
            messagebox.showwarning("Image Error", f"Could not preview image:\n{e}")

    def _calculate(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Input Error", "Please enter a username.")
            return

        try:
            measured_mm = float(self.size_var.get().strip())
            if measured_mm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number for size.")
            return

        mic_name   = self.mic_var.get()
        unit_name  = self.unit_var.get()
        magnification = MICROSCOPE_TYPES[mic_name]
        unit_factor   = UNIT_CONVERSIONS[unit_name]

        real_size_mm   = measured_mm / magnification
        real_size_disp = real_size_mm * unit_factor

        result_text = (
            f"  Microscope Type  : {mic_name}\n"
            f"  Magnification    : ×{magnification:,}\n"
            f"  Measured Size    : {measured_mm} mm\n"
            f"  Formula          : Real Size = Measured Size ÷ Magnification\n"
            f"  Calculation      : {measured_mm} ÷ {magnification:,} = {real_size_mm:.8f} mm\n"
            f"  ─────────────────────────────────────────────────\n"
            f"  ✓ REAL SIZE      : {real_size_disp:.6f} {unit_name}\n"
        )

        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result_text)
        self.result_text.configure(state=tk.DISABLED)

        save_record(username, mic_name, magnification,
                    measured_mm, real_size_mm, unit_name, real_size_disp)
        self._refresh_history()
        messagebox.showinfo("Saved", "Calculation saved to database.")

    def _refresh_history(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in fetch_all_records():
            self.tree.insert("", tk.END, values=rec)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Please select a record to delete.")
            return
        rid = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete record ID {rid}?"):
            delete_record_db(rid)
            self._refresh_history()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MicroscopeApp()
    app.mainloop()
