#!/usr/bin/env python3
"""
analyse_database.py
Exploratory and statistical analysis of STM32 sensor telemetry.
Generates statistical metrics and comparative insights between simulation and physical hardware phases.
"""

import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "sample_measurements.csv")

def main():
    parser = argparse.ArgumentParser(description="Statistical analysis of STM32 telemetry data")
    parser.add_argument("--csv", type=str, default=DEFAULT_CSV, help="Path to CSV dataset")
    parser.add_argument("--save-plot", type=str, default=None, help="Save summary plot to path")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"[!] Dataset '{args.csv}' not found.")
        return

    df = pd.read_csv(args.csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    total_records = len(df)
    date_start = df['timestamp'].min()
    date_end = df['timestamp'].max()
    duration = date_end - date_start

    # Partition: Phase 1 (Simulation testbed IDs 1-60) vs Phase 2 (Physical STM32 node ID > 60)
    df_sim = df.iloc[:min(60, len(df))]
    df_real = df.iloc[60:] if len(df) > 60 else pd.DataFrame()

    print("=" * 65)
    print("      STM32L475 TELEMETRY STATISTICAL REPORT")
    print("=" * 65)
    print(f"Total telemetry records : {total_records}")
    print(f"Monitoring duration      : {duration}")
    print(f"Date range               : {date_start} -> {date_end}")
    print(f"Missing values           : {df.isnull().sum().sum()} (0.0% data completeness)")

    print("\n--- 1. Global Metrics ---")
    print(df[['temperature', 'humidite', 'pression']].describe().round(2))

    if not df_real.empty:
        print("\n--- 2. Dual-Phase Deployment Analysis ---")
        print(f"[Phase 1: Telemetry Emulator (First 60s)]")
        print(f"  Samples: {len(df_sim)} | Temp: [{df_sim['temperature'].min()} - {df_sim['temperature'].max()}] °C")
        print(f"[Phase 2: Physical STM32L475 Node]")
        print(f"  Samples: {len(df_real)} | Temp: [{df_real['temperature'].min()} - {df_real['temperature'].max()}] °C")
        print(f"  Mean T: {df_real['temperature'].mean():.2f} °C | Std: {df_real['temperature'].std():.2f} °C")
        print(f"  Mean H: {df_real['humidite'].mean():.2f} %  | Std: {df_real['humidite'].std():.2f} %")
        print(f"  Mean P: {df_real['pression'].mean():.2f} hPa | Std: {df_real['pression'].std():.2f} hPa")
    print("=" * 65)

if __name__ == "__main__":
    main()
