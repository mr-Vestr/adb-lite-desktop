# ADB Lite Desktop

<p align="center">
  <a href="README.md">Русский</a> | <b>English</b>
</p>

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()
[![PyInstaller](https://img.shields.io/badge/built%20with-PyInstaller-8A2BE2)]()

<pre style="color:#00BFFF; font-weight:bold;">
     █████╗ ██████╗ ██████╗     ██╗     ██╗████████╗███████╗
    ██╔══██╗██╔══██╗██╔══██╗    ██║     ██║╚══██╔══╝██╔════╝
    ███████║██║  ██║██████╔╝    ██║     ██║   ██║   █████╗  
    ██╔══██║██║  ██║██╔══██╗    ██║     ██║   ██║   ██╔══╝  
    ██║  ██║██████╔╝██████╔╝    ███████╗██║   ██║   ███████╗
    ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚══════╝╚═╝   ╚═╝   ╚══════╝
</pre>

## Navigation

- [About](#about)
- [Features](#features)
- [Platforms](#platforms)
- [Quick Start](#quick-start)
- [Build from Source](#build-from-source)
  - [Requirements](#requirements)
  - [Step 1 — Get the Code](#step-1--get-the-code)
  - [Step 2 — Environment](#step-2--environment)
  - [Step 3 — Install Dependencies](#step-3--install-dependencies)
  - [Step 4 — Compile](#step-4--compile)
- [Technical Information](#technical-information)
  - [File Tree](#file-tree)
  - [Config and Logs](#config-and-logs)
  - [Plugin Communication Protocol](#plugin-communication-protocol)
    - [Device Discovery — mDNS](#1-device-discovery--mdns)
    - [POST /connect — Connection](#2-post-connect--connection)
    - [POST /check — Connection Check](#3-post-check--connection-check)
    - [GET /test — Device Info](#4-get-test--device-info)
    - [POST /install — Plugin Installation](#5-post-install--plugin-installation)
- [Feedback](#feedback)
- [License](#license)

---

## About

**ADB Lite Desktop** is a companion app for the **ADB Lite** plugin, which is installed in the Telegram clients **[exteraGram](https://t.me/exteraGram)** and **[AyuGram](https://t.me/AyuGramReleases)** on Android.

The plugin lets you instantly install plugins from your computer to your phone without ADB, root access, or internet — directly over the local network.

---

## Features

*   **mDNS Discovery** — automatic phone discovery on the local network
*   **Auto-updates** — new version check on startup and auto-update for Windows
*   **Start Menu shortcut** — automatically added on Windows
*   **Portable** — no installation required, just run the file from any folder
*   **Support for regular plugins and Elyx**
*   **Install on change** — automatic reinstallation when the file is saved
*   **Open source** — the only network request is the update check, nothing else is sent anywhere
*   **Multilingual** — Russian and English are supported, language is detected automatically

---

## Platforms

The app is written in Python and compiled with PyInstaller.

| Platform | Status |
| :--- | :--- |
| **Windows 10/11** | Pre-built binary in [Releases](https://github.com/mr-Vestr/adb-lite-desktop/releases) |
| **Linux** | Pre-built binary in [Releases](https://github.com/mr-Vestr/adb-lite-desktop/releases) |
| **macOS** | Requires self-build. I don't have a Mac :( |

> ⚠️ On Windows, just double-click the file to launch it. On Linux, run the file via terminal by specifying its path.

---

## Quick Start

1. Install the `ADB Lite` plugin for exteraGram or AyuGram from [GitHub](https://github.com/mr-Vestr/plugins) or the [channel](https://t.me/I_am_Vestr) and enable the server in the "ADB Lite Management" tab.

2. Download from [Releases](https://github.com/mr-Vestr/adb-lite-desktop/releases) or [build it yourself](#build-from-source) the `ADB Lite Desktop` app for your OS.

3. Follow the in-app instructions to pair your devices.

> ⚠️ Your phone and computer must be on the same Wi-Fi network.
> If you have connection issues, please contact [@mr_Vestr](https://t.me/mr_Vestr).

---

## Build from Source

### Requirements

*   Python 3.11+
*   Git

### Step 1 — Get the Code

```bash
git clone https://github.com/mr-Vestr/adb-lite-desktop.git
```
Or download the ZIP archive from GitHub and extract it.

```bash
cd adb-lite-desktop/ADB_Lite_Desktop
```

### Step 2 — Environment

It is recommended to create a virtual environment on Linux and macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows if needed:

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install requests zeroconf keyboard pyinstaller
```

### Step 4 — Compile

Windows:
```bash
python -m PyInstaller --onefile --icon=res/icon.ico --name="ADB_Lite_Desktop" --add-data "langs;langs" --add-data "res;res" --add-data "src;src" main.py
```

Linux:
```bash
python3 -m PyInstaller --onefile --name="ADB_Lite_Desktop" --add-data "langs:langs" --add-data "res:res" --add-data "src:src" main.py
```

macOS:
```bash
python3 -m PyInstaller --onefile --name="ADB_Lite_Desktop" --add-data "langs:langs" --add-data "res:res" --add-data "src:src" main.py
```

The compiled executable will be in the `dist/` folder.

---

## Technical Information

### File Tree

```
ADB_Lite_Desktop/
├── main.py                 # Entry point
├── langs/
│   ├── ru.json             # Russian translations
│   └── en.json             # English translations
├── res/
│   ├── icon.ico            # App icon
│   └── config.py           # App constants
└── src/
    ├── main.py             # Main loop, logger and update check
    ├── device/
    │   ├── search.py       # Device discovery via mDNS
    │   └── connect.py      # Device connection
    ├── actions/
    │   └── install.py      # Plugin installation
    ├── menus/
    │   ├── home.py         # Main menu
    │   ├── plugin.py       # Plugin path selection
    │   ├── device.py       # Device selection and manual address input
    │   ├── lang.py         # Language selection
    │   └── config.py       # Opening config and log files
    └── other/
        ├── config.py       # Settings management
        ├── updater.py      # App updater
        ├── shortcut.py     # Start Menu shortcut
        ├── watcher.py      # File change watcher
        └── utils.py        # Utilities and console styling
```

Hotkeys in the app: `Ctrl+Q` — open log, `Ctrl+W` — open config.

### Config and Logs

The configuration file is created automatically on first launch:

```
Windows:  %APPDATA%\ADBLite\config.json
Linux:    ~/.config/ADBLite/config.json
macOS:    ~/Library/Application Support/ADBLite/config.json
```

Example `config.json`:

```json
{
    "plugin_path": "C:/Users/You/Desktop/my_plugin.py",
    "devices": [
        {
            "link": "http://192.168.1.10:12345",
            "name": "Pixel 7",
            "client": "exteraGram",
            "last_connected": 1700000000.0,
            "key": ""
        }
    ],
    "language": "en",
    "last_device": {
        "link": "http://192.168.1.10:12345",
        "name": "Pixel 7",
        "client": "exteraGram",
        "key": ""
    },
    "device_token": "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5",
    "install_on_change": false
}
```

*   `plugin_path` — path to the last selected plugin file
*   `language` — app language
*   `devices` — history of connected devices
*   `last_device` — last device for auto-connect
*   `device_token` — token for phone authorization (generated once)
*   `install_on_change` — whether install on change is enabled

The `log.txt` file with app logs is located next to the config.

### Plugin Communication Protocol

All communication goes over HTTP within the local network, the phone acts as a server.

#### 1. Device Discovery — mDNS

Service: `_adblite._tcp.local.`

Response from the phone:

```json
{
    "name": "Pixel 7",                    // device model
    "manufacturer": "Google",             // device manufacturer
    "version": "1.0",                     // plugin version
    "ip": "192.168.1.10",                 // phone IP address
    "port": 12345,                        // server port on the phone
    "link": "http://192.168.1.10:12345",  // full connection URL
    "client": "exteraGram",               // Telegram client (exteraGram / AyuGram)
    "key": ""                             // device key
}
```

#### 2. POST /connect — Connection

```http
POST http://<ip>:<port>/connect

adb_lite_s
<hostname>        // computer name
<system>          // operating system (Windows/Linux/Darwin)
<device_token>    // token from config.json
<pc_ip>           // local IP of the computer
1                 // support flag, version compatibility check
```

Response `yes` — connection confirmed, `no` — rejected.

#### 3. POST /check — Connection Check

```http
POST http://<ip>:<port>/check

<device_token>
<device_name>
```

Response `yes` — connection active, `no` — rejected.

#### 4. GET /test — Device Info

```http
GET http://<ip>:<port>/test
```

Response:

```json
{
    "device": "Pixel 7",
    "app": "exteraGram"
}
```

#### 5. POST /install — Plugin Installation

```http
POST http://<ip>:<port>/install
X-Filename: my_plugin.py
X-Device-Token: <device_token>
Content-Type: application/octet-stream

<file content>
```

Response `yes` — success, `error: ...` — installation error.

---

## Feedback

*   I would appreciate it if you star this repository.
*   If you found a bug or have a suggestion, please create an Issue.
*   Author's channel: https://t.me/I_am_Vestr
*   Direct messages: https://t.me/mr_Vestr

---

## License

This project is distributed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file.

---

<p align="center">
  Made with ❤️ for the exteraGram and AyuGram community
</p>
