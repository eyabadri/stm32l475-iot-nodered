#!/usr/bin/env python3
"""
Vérification rapide de la base SQLite sensors.db.
Usage: python check_db.py
"""
import sqlite3
import os

DB_PATH = r"C:\Users\ayaba\sensors.db"

if not os.path.exists(DB_PATH):
    print(f"[!] La base {DB_PATH} n'existe pas encore.")
    print("    Elle sera créée automatiquement par Node-RED au premier INSERT.")
    exit(0)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM measurements")
count = c.fetchone()[0]
print(f"Nombre de mesures : {count}")

if count > 0:
    print(f"\n{'id':>5}  {'timestamp':>20}  {'T (°C)':>8}  {'H (%)':>8}  {'P (hPa)':>10}")
    print("─" * 60)
    c.execute("SELECT * FROM measurements ORDER BY id DESC LIMIT 5")
    for row in c.fetchall():
        print(f"{row[0]:>5}  {row[1]:>20}  {row[2]:>8.2f}  {row[3]:>8.2f}  {row[4]:>10.1f}")
else:
    print("La base est vide — en attente de données du STM32 ou du simulateur.")

conn.close()
