# Architecture Système & Persistance Locale SQLite

## Système de Télémétrie IoT STM32L475 / MQTT / Node-RED / SQLite
**Auteur :** Eya Badri

---

### 1. Vue d'Ensemble de la Chaîne IoT

```
┌────────────────────────┐         ┌────────────────────────┐
│ Carte STM32L475        │         │ PC Superviseur         │
│  - HTS221 (Temp/Hum)   │  Wi-Fi  │  - Broker Mosquitto    │
│  - LPS22HB (Pression)  ├────────>│    (Port 1883)         │
│  - Module ISM43362     │  MQTT   │                        │
└────────────────────────┘         └───────────┬────────────┘
                                               │
                                               ▼
                                   ┌────────────────────────┐
                                   │ Node-RED               │
                                   │  - Dashboard /ui       │
                                   │  - Traitement & Fusion │
                                   └───────────┬────────────┘
                                               │
                                               ▼
                                   ┌────────────────────────┐
                                   │ Base SQLite Locale     │
                                   │  sensors.db            │
                                   └───────────┬────────────┘
                                               │
                                               ▼
                                   ┌────────────────────────┐
                                   │ Scripts d'Analyse      │
                                   │  - check_db.py         │
                                   │  - plot_sensors.py     │
                                   └────────────────────────┘
```

---

### 2. Base de Données SQLite (`sensors.db`)

- **Emplacement** : racine du projet ou dossier utilisateur (`sensors.db`).
- **Moteur** : SQLite 3 (base relationnelle légère embarquée, zéro-configuration, sans service serveur externe).
- **Mode d'ouverture par Node-RED** : `RWC` (Read-Write-Create).

#### Schéma SQL de la table `measurements` :
```sql
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    temperature REAL,
    humidite REAL,
    pression REAL
);
CREATE INDEX IF NOT EXISTS idx_measurements_ts ON measurements(timestamp);
```

| Champ | Type | Description |
|-------|------|-------------|
| `id` | `INTEGER` | Clé primaire auto-incrémentée identifiant chaque enregistrement |
| `timestamp` | `TEXT` | Horodatage local format ISO (`YYYY-MM-DD HH:MM:SS`) |
| `temperature` | `REAL` | Mesure physique du capteur HTS221 en degrés Celsius (°C) |
| `humidite` | `REAL` | Mesure physique du capteur HTS221 en pourcentage d'humidité relative (%) |
| `pression` | `REAL` | Mesure physique du capteur LPS22HB en hectopascals (hPa) |

---

### 3. Pipeline d'Acquisition & Enregistrement dans Node-RED

1. **Réception MQTT** : 3 nœuds d'écoute souscrivent aux topics `sensors/temperature`, `sensors/humidity`, et `sensors/pressure`.
2. **Nœud "Merge + Timestamp"** : Regroupe les mesures asynchrones pour former un échantillon complet et horodaté.
3. **Nœud "Préparer INSERT"** : Formate la requête SQL paramétrée pour une insertion sécurisée :
   ```javascript
   var d = msg.payload;
   msg.topic = "INSERT INTO measurements (timestamp, temperature, humidite, pression) VALUES ($ts, $temp, $hum, $pres)";
   msg.payload = [d.timestamp, d.temperature, d.humidite, d.pression];
   return msg;
   ```
4. **Nœud SQLite INSERT** : Exécute l'insertion immédiate sur disque.
5. **Nœud SQLite SELECT** : Extrait l'historique récent pour alimenter les courbes et tableaux du Dashboard web (`http://localhost:1880/ui`).

---

### 4. Vérification et Exploitation des Données

- **Audit en console (`check_db.py`)** :
  ```powershell
  python tools/check_db.py
  ```
  Affiche le nombre total d'entrées et les dernières mesures physiques.

- **Visualisation graphique (`plot_sensors.py`)** :
  ```powershell
  python tools/plot_sensors.py --last 5
  ```
  Génère les 3 courbes synchronisées (Température, Humidité, Pression) via Matplotlib.
