#!/usr/bin/env python3
"""
plot_sensors.py - SQLite telemetry reader and multi-axis visualizer for STM32L475 sensors.

Usage:
    python plot_sensors.py                     # Plot all data in sensors.db
    python plot_sensors.py --last 60           # Last 60 minutes
    python plot_sensors.py --from "2026-09-24 15:00" --to "2026-09-24 16:00"
    python plot_sensors.py --table             # Text table output only
    python plot_sensors.py --db path/to/db     # Specify custom database path
"""
import sqlite3
import argparse
import os
from datetime import datetime, timedelta

try:
    import matplotlib
    matplotlib.use('TkAgg')
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "sensors.db")
FALLBACK_DB = r"C:\Users\ayaba\sensors.db"

def resolve_db_path(custom_path=None):
    if custom_path and os.path.exists(custom_path):
        return custom_path
    if os.path.exists("sensors.db"):
        return "sensors.db"
    if os.path.exists(DEFAULT_DB):
        return DEFAULT_DB
    if os.path.exists(FALLBACK_DB):
        return FALLBACK_DB
    return "sensors.db"

def fetch_data(db_path, last_minutes=None, dt_from=None, dt_to=None):
    if not os.path.exists(db_path):
        print(f"[!] Database file '{db_path}' not found.")
        print("    Run the Node-RED flow or simulate telemetry first.")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        if last_minutes:
            since = (datetime.now() - timedelta(minutes=last_minutes)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "SELECT timestamp, temperature, humidite, pression "
                "FROM measurements WHERE timestamp >= ? ORDER BY timestamp",
                (since,)
            )
        elif dt_from and dt_to:
            cursor.execute(
                "SELECT timestamp, temperature, humidite, pression "
                "FROM measurements WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp",
                (dt_from, dt_to)
            )
        else:
            cursor.execute(
                "SELECT timestamp, temperature, humidite, pression "
                "FROM measurements ORDER BY timestamp"
            )

        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"[!] SQLite query error: {e}")
        rows = []
    finally:
        conn.close()
    return rows

def plot(rows):
    if not rows:
        print("No telemetry records found to plot.")
        return

    timestamps = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S") for r in rows]
    temp = [r[1] for r in rows]
    hum  = [r[2] for r in rows]
    pres = [r[3] for r in rows]

    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(
        f"STM32L475 IoT Node Telemetry - {len(rows)} Samples\n"
        f"Interval: {timestamps[0].strftime('%Y-%m-%d %H:%M:%S')} -> {timestamps[-1].strftime('%H:%M:%S')}",
        fontsize=13, fontweight='bold'
    )

    # Temperature
    axes[0].plot(timestamps, temp, color='#e74c3c', linewidth=1.5, label="Temperature (HTS221)")
    axes[0].set_ylabel("Temperature (°C)", fontweight='bold')
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].fill_between(timestamps, temp, alpha=0.15, color='#e74c3c')
    axes[0].legend(loc="upper right")

    # Humidity
    axes[1].plot(timestamps, hum, color='#3498db', linewidth=1.5, label="Relative Humidity (HTS221)")
    axes[1].set_ylabel("Humidity (%)", fontweight='bold')
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].fill_between(timestamps, hum, alpha=0.15, color='#3498db')
    axes[1].legend(loc="upper right")

    # Pressure
    axes[2].plot(timestamps, pres, color='#2ecc71', linewidth=1.5, label="Barometric Pressure (LPS22HB)")
    axes[2].set_ylabel("Pressure (hPa)", fontweight='bold')
    axes[2].grid(True, linestyle="--", alpha=0.5)
    axes[2].fill_between(timestamps, pres, alpha=0.15, color='#2ecc71')
    axes[2].legend(loc="upper right")

    # Time axis formatting
    axes[2].set_xlabel("Time (UTC)", fontweight='bold')
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate(rotation=30)

    plt.tight_layout()
    plt.show()

def print_table(rows, limit=20):
    print(f"\n{'#':>5}  {'Timestamp':>20}  {'T (°C)':>8}  {'H (%)':>8}  {'P (hPa)':>10}")
    print("-" * 60)
    for i, r in enumerate(rows[-limit:], start=max(1, len(rows) - limit + 1)):
        print(f"{i:>5}  {r[0]:>20}  {r[1]:>8.2f}  {r[2]:>8.2f}  {r[3]:>10.1f}")
    print(f"\nTotal: {len(rows)} records stored in SQLite database.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize STM32 sensor measurements from SQLite")
    parser.add_argument("--db", type=str, default=None, help="Path to SQLite database file")
    parser.add_argument("--last", type=int, help="Fetch last N minutes")
    parser.add_argument("--from", dest="dt_from", help="Start time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--to", dest="dt_to", help="End time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--table", action="store_true", help="Print table in terminal only")
    args = parser.parse_args()

    db_target = resolve_db_path(args.db)
    print(f"[*] Accessing database: {db_target}")
    rows = fetch_data(db_target, args.last, args.dt_from, args.dt_to)

    if rows:
        print_table(rows)
        if not args.table:
            plot(rows)
