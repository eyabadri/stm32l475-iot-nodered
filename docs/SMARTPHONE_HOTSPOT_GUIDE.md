# Démonstration sur Point d'Accès Mobile (Smartphone)

## Système IoT STM32L475 / MQTT / Node-RED / SQLite
**Auteur :** Eya Badri

---

### 🎯 Objectif : Démonstration 100% Autonome

Lors d'une présentation ou soutenance :
1. **Les réseaux d'entreprise ou d'université bloquent souvent l'IoT** : présence d'un portail captif, d'authentification WPA2-Enterprise (802.1X non supportée par le module Wi-Fi de la carte), ou d'isolation des clients (AP Isolation empêchant la carte de contacter le PC sur le port 1883).
2. **Autonomie totale** : en transformant un smartphone en routeur Wi-Fi de poche, le PC et la carte STM32 communiquent sur un réseau local privé et stable, n'importe où, sans dépendre d'une box internet.
3. **Supervision mobile** : le Dashboard Node-RED peut être ouvert directement sur le navigateur du smartphone.

---

### 🌐 Architecture Réseau Cible

```
                      ┌───────────────────────────────────────┐
                      │         SMARTPHONE (Point d'Accès)     │
                      │  • Routeur Wi-Fi 2.4 GHz + Serveur DHCP│
                      │  • IP Passerelle : ex. 192.168.43.1   │
                      └──────────────────┬────────────────────┘
                                         │
                 ┌───────────────────────┴────────────────────────┐
                 ▼ (Wi-Fi)                                        ▼ (Wi-Fi)
   ┌───────────────────────────┐                    ┌───────────────────────────┐
   │       CARTE STM32L475     │                    │        PC WINDOWS         │
   │  • Module ISM43362        │                    │  • Broker Mosquitto :1883 │
   │  • Client MQTT Publisher  │                    │  • Node-RED Server :1880  │
   │  • IP : ex. 192.168.43.15 │ ─── MQTT :1883 ──► │  • Base SQLite sensors.db │
   └───────────────────────────┘                    │  • IP : ex. 192.168.43.20 │
                                                    └─────────────┬─────────────┘
                                                                  │
                                                Naviguer vers     │
                                             http://192.168.43.20:1880/ui
                                                                  │
                                                    ┌─────────────▼─────────────┐
                                                    │ Navigateur du SMARTPHONE  │
                                                    │  (Dashboard en direct !)  │
                                                    └───────────────────────────┘
```

---

### 📋 Procédure Pas-à-Pas

#### Étape 1 : Configuration du Point d'Accès sur le Smartphone
> **Règle essentielle pour la STM32L475** : Le module Wi-Fi Inventek ISM43362 ne supporte que la bande **2.4 GHz**.
- Activer le partage de connexion / Point d'accès mobile sur le smartphone.
- Régler la bande de fréquence sur **2.4 GHz** (sur Android : *Paramètres > Point d'accès > Bande 2.4 GHz* ; sur iPhone : activer *« Maximiser la compatibilité »*).
- Définir un mot de passe WPA2 simple.

#### Étape 2 : Connexion du PC et Identification de l'IP
1. Connecter le PC Windows au réseau Wi-Fi du smartphone.
2. Ouvrir PowerShell et taper : `ipconfig`
3. Noter l'adresse IPv4 sous la carte réseau sans fil (ex: `192.168.43.20`).
4. Vérifier que Mosquitto et Node-RED sont démarrés.

#### Étape 3 : Configuration du Firmware et Flashage
1. Dans `wifi_credentials.h` :
   - Sélectionner le profil 3 : `#define WIFI_PROFILE 3`
   - Définir le SSID et mot de passe du hotspot.
2. Dans `main.c` :
   - Mettre à jour l'adresse IP du broker avec l'IP du PC relevée à l'étape 2 :
     ```c
     uint8_t broker_ip[4] = { 192, 168, 43, 20 };
     ```
3. Compiler et flasher la carte dans STM32CubeIDE.

#### Étape 4 : Consultation du Dashboard sur Smartphone
1. Ouvrir Chrome ou Safari sur le smartphone.
2. Naviguer vers : `http://<IP_DU_PC>:1880/ui` (ex: `http://192.168.43.20:1880/ui`).
3. Le tableau de bord affiche les jauges et courbes en temps réel.

> **Consommation 4G/5G :** Le trafic MQTT et HTTP s'effectue **100% en réseau local (LAN)**. Aucune donnée mobile n'est consommée.

---

### ⚠️ Tableau de Dépannage Rapide

| Symptôme | Cause Probable | Solution |
| :--- | :--- | :--- |
| `WIFI_Connect Error` | Hotspot configuré en 5 GHz | Forcer la fréquence 2.4 GHz sur le smartphone. |
| `TCP Connect Error` | L'IP du PC a changé via DHCP | Refaire `ipconfig` et mettre à jour `broker_ip` dans `main.c`. |
| Dashboard inaccessible sur mobile | Port 1880 bloqué par pare-feu | Autoriser Node-RED dans le Pare-feu Windows Defender. |
