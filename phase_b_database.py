"""
Phase B: Database Integration
Extends Phase A with SQLite database for storing calculations.
CSC 442 - Project 1
"""

import sqlite3
import os
from phase_a_calculator import (
    MICROSCOPE_TYPES, UNIT_CONVERSIONS,
    get_measured_size, get_microscope_choice, get_unit_choice,
    calculate_real_size, display_result
)

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "calculations.db")


# ── Database helpers ──────────────────────────────────────────────────────────

def init_db():
    """Create the calculations table if it doesn't exist."""
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
        SELECT id, username, microscope_type, magnification,
               measured_size, real_size_disp, output_unit, timestamp
        FROM calculations
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return rows


def delete_record(record_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ── Display helpers ───────────────────────────────────────────────────────────

def view_records():
    rows = fetch_all_records()
    if not rows:
        print("\n  No records found.")
        return
    print("\n" + "=" * 80)
    print(f"  {'ID':<5} {'Username':<15} {'Microscope':<30} {'Meas.(mm)':<12} {'Real Size':<20} {'Date'}")
    print("=" * 80)
    for row in rows:
        rid, user, mic, mag, meas, real, unit, ts = row
        print(f"  {rid:<5} {user:<15} {mic[:28]:<30} {meas:<12.4f} {real:.6f} {unit:<8} {ts}")
    print("=" * 80)


def manage_records():
    while True:
        print("\n--- Manage Records ---")
        print("  [1] View all records")
        print("  [2] Delete a record by ID")
        print("  [3] Back")
        choice = input("Choice: ").strip()
        if choice == "1":
            view_records()
        elif choice == "2":
            view_records()
            try:
                rid = int(input("Enter record ID to delete: ").strip())
                if delete_record(rid):
                    print(f"  Record {rid} deleted.")
                else:
                    print(f"  No record with ID {rid}.")
            except ValueError:
                print("  Invalid ID.")
        elif choice == "3":
            break
        else:
            print("  Invalid choice.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    init_db()
    print("\n" + "=" * 55)
    print("   MICROSCOPE SPECIMEN SIZE CALCULATOR — Phase B")
    print("=" * 55)

    username = input("\nEnter your username: ").strip()
    while not username:
        print("  Username cannot be empty.")
        username = input("Enter your username: ").strip()

    while True:
        print(f"\nWelcome, {username}!")
        print("  [1] Perform a calculation")
        print("  [2] View / Manage records")
        print("  [3] Change username")
        print("  [4] Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            measured_mm  = get_measured_size()
            mic_choice   = get_microscope_choice()
            unit_choice  = get_unit_choice()

            microscope_name, magnification = MICROSCOPE_TYPES[mic_choice]
            unit_name, unit_factor         = UNIT_CONVERSIONS[unit_choice]

            real_size    = calculate_real_size(measured_mm, magnification, unit_factor)
            real_size_mm = measured_mm / magnification

            display_result(measured_mm, microscope_name, magnification, unit_name, real_size)
            save_record(username, microscope_name, magnification,
                        measured_mm, real_size_mm, unit_name, real_size)
            print("  ✓ Record saved to database.")

        elif choice == "2":
            manage_records()

        elif choice == "3":
            username = input("\nEnter new username: ").strip()

        elif choice == "4":
            print("\nGoodbye!\n")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    run()
