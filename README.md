# ADB Lite Desktop

<p align="center">
  <b>Русский</b> | <a href="README_EN.md">English</a>
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

## Навигация

- [О проекте](#о-проекте)
- [Возможности](#возможности)
- [Платформы](#платформы)
- [Быстрый старт](#быстрый-старт)
- [Сборка из исходников](#сборка-из-исходников)
  - [Требования](#требования)
  - [Шаг 1 — Получите код](#шаг-1--получите-код)
  - [Шаг 2 — Окружение](#шаг-2--окружение)
  - [Шаг 3 — Установите зависимости](#шаг-3--установите-зависимости)
  - [Шаг 4 — Скомпилируйте](#шаг-4--скомпилируйте)
- [Техническая информация](#техническая-информация)
  - [Дерево файлов](#дерево-файлов)
  - [Конфиг и логи](#конфиг-и-логи)
  - [Протокол общения с плагином](#протокол-общения-с-плагином)
    - [Поиск устройств — mDNS](#1-поиск-устройств--mdns)
    - [POST /connect — подключение](#2-post-connect--подключение)
    - [POST /check — проверка соединения](#3-post-check--проверка-соединения)
    - [GET /test — информация об устройстве](#4-get-test--информация-об-устройстве)
    - [POST /install — установка плагина](#5-post-install--установка-плагина)
- [Обратная связь](#обратная-связь)
- [Лицензия](#лицензия)

---

## О проекте

**ADB Lite Desktop** — компаньон для плагина **ADB Lite**, который устанавливается в клиенты Telegram **[exteraGram](https://t.me/exteraGram)** и **[AyuGram](https://t.me/AyuGramReleases)** на Android.

Плагин позволяет мгновенно устанавливать плагины с компьютера на телефон без ADB, root-прав и интернета — напрямую по локальной сети.

---

## Возможности

*   **Поиск по mDNS** — автоматический поиск телефонов в локальной сети
*   **Автообновления** — проверка новой версии при запуске и автообновление для Windows
*   **Ярлык в меню «Пуск»** — автоматически добавляется на Windows
*   **Портативность** — не требует установки, достаточно запустить файл из любой папки
*   **Поддержка обычных плагинов и Elyx**
*   **Установка при изменении** — автоматическая переустановка при сохранении файла
*   **Открытый код** — единственный сетевой запрос — проверка обновлений, больше ничего никуда не передается
*   **Мультиязычность** — поддерживаются русский и английский, язык определяется автоматически

---

## Платформы

Приложение написано на Python и скомпилировано через PyInstaller.

| Платформа | Статус |
| :--- | :--- |
| **Windows 10/11** | Готовая сборка в [Releases](https://github.com/mr-Vestr/adb-lite-desktop/releases) |
| **Linux** | Готовая сборка в [Releases](https://github.com/mr-Vestr/adb-lite-desktop/releases) |
| **macOS** | Требует самостоятельной сборки. У меня нет Mac :( |

> ⚠️ На Windows для запуска достаточно дважды кликнуть по файлу. На Linux запустите файл через терминал, указав путь к нему.

---

## Быстрый старт

1. Установите плагин `ADB Lite` для exteraGram или AyuGram с [GitHub](https://github.com/mr-Vestr/plugins) или [канала](https://t.me/I_am_Vestr) и во вкладке «Управление ADB Lite» включите сервер.

2. Скачайте с [релизов](https://github.com/mr-Vestr/adb-lite-desktop/releases) или [соберите самостоятельно](#сборка-из-исходников) приложение `ADB Lite Desktop` под Вашу ОС.

3. Далее следуйте инструкциям в приложении для сопряжения устройств.

> ⚠️ Телефон и компьютер должны находиться в одной Wi-Fi сети.
> Если у Вас возникнут проблемы с подключением, обращайтесь к [@mr_Vestr](https://t.me/mr_Vestr).

---

## Сборка из исходников

### Требования

*   Python 3.11+
*   Git

### Шаг 1 — Получите код

```bash
git clone https://github.com/mr-Vestr/adb-lite-desktop.git
```
Или скачайте ZIP-архив с GitHub и распакуйте.

```bash
cd adb-lite-desktop/ADB_Lite_Desktop
```

### Шаг 2 — Окружение

На Linux и macOS рекомендуется создать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

На Windows при необходимости:

```bash
python -m venv venv
venv\Scripts\activate
```

### Шаг 3 — Установите зависимости

```bash
pip install requests zeroconf keyboard pyinstaller
```

### Шаг 4 — Скомпилируйте

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

Готовый исполняемый файл будет в папке `dist/`.

---

## Техническая информация

### Дерево файлов

```
ADB_Lite_Desktop/
├── main.py                 # Точка входа
├── langs/
│   ├── ru.json             # Переводы на русский
│   └── en.json             # Переводы на английский
├── res/
│   ├── icon.ico            # Иконка приложения
│   └── config.py           # Константы приложения
└── src/
    ├── main.py             # Основной цикл, логгер и проверка обновлений
    ├── device/
    │   ├── search.py       # Поиск устройств по mDNS
    │   └── connect.py      # Подключение к устройству
    ├── actions/
    │   └── install.py      # Установка плагинов
    ├── menus/
    │   ├── home.py         # Главное меню
    │   ├── plugin.py       # Выбор пути к плагину
    │   ├── device.py       # Выбор устройства и ручной ввод адреса
    │   ├── lang.py         # Выбор языка
    │   └── config.py       # Открытие файлов конфигурации и логов
    └── other/
        ├── config.py       # Управление настройками
        ├── updater.py      # Обновление приложения
        ├── shortcut.py     # Ярлык в меню «Пуск»
        ├── watcher.py      # Отслеживание изменений файла
        └── utils.py        # Утилиты и оформление консоли
```

Горячие клавиши в приложении: `Ctrl+Q` — открыть лог, `Ctrl+W` — открыть конфиг.

### Конфиг и логи

Файл конфигурации создается автоматически при первом запуске:

```
Windows:  %APPDATA%\ADBLite\config.json
Linux:    ~/.config/ADBLite/config.json
macOS:    ~/Library/Application Support/ADBLite/config.json
```

Пример `config.json`:

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
    "language": "ru",
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

*   `plugin_path` — путь к последнему выбранному файлу плагина
*   `language` — язык приложения
*   `devices` — история подключенных устройств
*   `last_device` — последнее устройство для автоподключения
*   `device_token` — токен для авторизации на телефоне (генерируется один раз)
*   `install_on_change` — включена ли установка при изменении

Рядом с конфигом находится `log.txt` с логами работы приложения.

### Протокол общения с плагином

Все общение идет по HTTP внутри локальной сети, телефон выступает сервером.

#### 1. Поиск устройств — mDNS

Сервис: `_adblite._tcp.local.`

Ответ от телефона:

```json
{
    "name": "Pixel 7",                    // модель устройства
    "manufacturer": "Google",             // производитель устройства
    "version": "1.0",                     // версия плагина
    "ip": "192.168.1.10",                 // IP-адрес телефона
    "port": 12345,                        // порт сервера на телефоне
    "link": "http://192.168.1.10:12345",  // полный адрес для подключения
    "client": "exteraGram",               // клиент Telegram (exteraGram / AyuGram)
    "key": ""                             // ключ устройства
}
```

#### 2. POST /connect — подключение

```http
POST http://<ip>:<port>/connect

adb_lite_s
<hostname>        // имя компьютера
<system>          // операционная система (Windows/Linux/Darwin)
<device_token>    // токен из config.json
<pc_ip>           // локальный IP компьютера
1                 // флаг поддержки, проверка совместимости версий
```

Ответ `yes` — подключение подтверждено, `no` — отклонено.

#### 3. POST /check — проверка соединения

```http
POST http://<ip>:<port>/check

<device_token>
<device_name>
```

Ответ `yes` — соединение активно, `no` — отклонено.

#### 4. GET /test — информация об устройстве

```http
GET http://<ip>:<port>/test
```

Ответ:

```json
{
    "device": "Pixel 7",
    "app": "exteraGram"
}
```

#### 5. POST /install — установка плагина

```http
POST http://<ip>:<port>/install
X-Filename: my_plugin.py
X-Device-Token: <device_token>
Content-Type: application/octet-stream

<содержимое файла>
```

Ответ `yes` — успешно, `error: ...` — ошибка установки.

---

## Обратная связь

*   Буду благодарен, если Вы отметите репозиторий звездой.
*   Если Вы нашли ошибку или у Вас есть предложение, пожалуйста, создайте Issue.
*   Канал автора: https://t.me/I_am_Vestr
*   Личные сообщения: https://t.me/mr_Vestr

---

## Лицензия

Проект распространяется под лицензией GNU General Public License v3.0 — см. файл [LICENSE](LICENSE).

---

<p align="center">
  Сделано с ❤️ для сообщества exteraGram и AyuGram
</p>
