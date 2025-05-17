
````markdown
# IPChat

**IPChat** is a lightweight, peer-to-peer LAN messaging application built with Python. It provides a simple graphical interface for real-time communication between devices on the same network. The application supports one-to-one and group messaging, text file sharing, and maintains message history locally.

> This project is intended for educational and experimental purposes only.

---

## Features

- Peer-to-peer communication over IP (no central server required)
- Group messaging using configurable IP lists
- Send `.txt` files to individual IPs or groups
- Simple, responsive graphical interface using `tkinter` and `ttkbootstrap`
- Desktop notifications for incoming messages
- Auto-saving of chat logs and message history

---

## Technologies Used

- Python 3
- `socket` — for TCP networking
- `tkinter` with `ttkbootstrap` — for the GUI
- `plyer` — for desktop notifications
- `json` — for managing groups and history

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/shreyashyam29/ipchat.git
cd ipchat
````

### 2. Install dependencies

Make sure you have Python 3 installed. Then install the required libraries:

```bash
pip install plyer ttkbootstrap
```

### 3. Run the application

```bash
python ipchat.py
```

---

## File Overview

* `ipchat.py` — Main application script
* `groups.json` — Stores named groups of IPs
* `chat.log` — Appends a plain text log of all messages
* `chat_history.json` — Stores structured message history for later processing

---

## Usage

1. Launch the application on two or more devices connected to the same network.
2. Enter the recipient's IP address or use a group (e.g., `group:team1`) if defined.
3. Type your message or attach a `.txt` file to send.
4. Messages and logs are saved automatically.

---

## Example `groups.json`

```json
{
  "team1": ["192.168.1.10", "192.168.1.11"],
  "classmates": ["192.168.1.20", "192.168.1.21"]
}
```

---

## License

This project is not licensed and is provided strictly for educational and experimental use.

