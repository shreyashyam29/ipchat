import socket
import threading
import json
import time
import os
import sys
from plyer import notification
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog, Text, Canvas, Scrollbar

sys.stdout.reconfigure(encoding='utf-8')

PORT = 12345
HOST = "0.0.0.0"

# Load groups
try:
    with open('groups.json', 'r') as f:
        groups = json.load(f)
except:
    groups = {}

# Initialize main app
app = ttk.Window("💬 IPChat", themename="pulse", size=(800, 600))
app.place_window_center()

# GUI Elements
title_label = ttk.Label(app, text="IPChat", font=("Segoe UI", 20, "bold"))
title_label.pack(pady=(10, 0))

chat_frame = ttk.Frame(app)
chat_frame.pack(fill='both', expand=True, padx=10, pady=5)

canvas = Canvas(chat_frame)
scrollbar = Scrollbar(chat_frame, command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

input_frame = ttk.Frame(app)
input_frame.pack(fill='x', padx=10, pady=(5, 0))

username_entry = ttk.Entry(input_frame, width=15)
username_entry.insert(0, "Anonymous")
username_entry.grid(row=0, column=1, padx=5)
ttk.Label(input_frame, text="Your Name:").grid(row=0, column=0)

target_entry = ttk.Entry(input_frame, width=25)
target_entry.grid(row=0, column=3, padx=5)
ttk.Label(input_frame, text="Send To (IP or group:name):").grid(row=0, column=2)

# Resizable Text input
message_entry = Text(input_frame, height=3, wrap='word')
message_entry.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

button_frame = ttk.Frame(app)
button_frame.pack(pady=5)

send_btn = ttk.Button(button_frame, text="🚀 Send", bootstyle="success-outline")
send_btn.pack(side='left', padx=5)

file_btn = ttk.Button(button_frame, text="📎 Send File (.txt)", bootstyle="info-outline")
file_btn.pack(side='left', padx=5)

# Core Functions
def log_message(msg, sender="system"):
    timestamp = time.strftime("%H:%M:%S")
    bg, anchor = ("#e0e0e0", "center")

    if sender == "you":
        bg, anchor = "#d1e7dd", "e"
    elif sender == "other":
        bg, anchor = "#cfe2ff", "w"

    frame = ttk.Frame(scrollable_frame)
    label = ttk.Label(frame, text=f"{msg}  [{timestamp}]", background=bg, wraplength=500, anchor=anchor, justify='left')
    label.pack(anchor=anchor, padx=10, pady=2, fill='x')
    frame.pack(fill='x')

    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    # Save log
    with open("chat.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

    with open("chat_history.json", "a") as f:
        json.dump({"timestamp": timestamp, "message": msg}, f)
        f.write("\n")

    # Show notification if app is minimized
    if not app.winfo_viewable():
        notification.notify(title="📩 New Message", message=msg, timeout=3)

def is_online(ip):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((ip, PORT))
        s.close()
        return True
    except:
        return False

def send_message(ip, msg, username):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, PORT))
        s.sendall(msg.encode('utf-8'))

        try:
            ack = s.recv(1024).decode('utf-8')
            if ack == "ACK":
                log_message(f"✓ Delivered to {ip}", sender="system")
            else:
                log_message(f"✗ No ACK from {ip}", sender="system")
        except:
            log_message(f"✗ No ACK from {ip}", sender="system")

        s.close()
        log_message(f"You to {ip}: {msg}", sender="you")

    except Exception as e:
        log_message(f"[SEND ERROR to {ip}] {e}", sender="system")
        messagebox.showerror("Send Error", f"Failed to send to {ip}: {e}")

def send_to_group(group_name, msg, username):
    if group_name in groups:
        for ip in groups[group_name]:
            if is_online(ip):
                send_message(ip, msg, username)
            else:
                log_message(f"[OFFLINE] {ip} not reachable.", sender="system")
    else:
        messagebox.showwarning("Group Not Found", f"Group '{group_name}' not found.")

def send_text_file(ip, file_path, username):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        msg = f"{username} (file: {os.path.basename(file_path)}):\n{content}"
        send_message(ip, msg, username)
    except Exception as e:
        log_message(f"[FILE ERROR] {e}", sender="system")
        messagebox.showerror("File Send Error", f"Could not send file: {e}")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return
    ip = target_entry.get().strip()
    username = username_entry.get().strip() or "Anonymous"

    if ip.startswith("group:"):
        group = ip.split(":", 1)[1]
        for member in groups.get(group, []):
            if is_online(member):
                send_text_file(member, file_path, username)
            else:
                log_message(f"[OFFLINE] {member} not reachable.", sender="system")
    else:
        if is_online(ip):
            send_text_file(ip, file_path, username)
        else:
            messagebox.showwarning("Offline", f"{ip} appears offline.")

def send_button_clicked():
    target = target_entry.get().strip()
    msg = message_entry.get("1.0", "end").strip()
    username = username_entry.get().strip() or "Anonymous"
    message_entry.delete("1.0", "end")

    if not target or not msg:
        messagebox.showinfo("Missing Info", "Please fill in all fields.")
        return

    full_msg = f"{username}: {msg}"

    if target.startswith("group:"):
        group = target.split(":", 1)[1]
        send_to_group(group, full_msg, username)
    else:
        if not is_online(target):
            messagebox.showwarning("Offline", f"{target} appears to be offline.")
            return
        send_message(target, full_msg, username)

def receiver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        data = conn.recv(4096).decode('utf-8')
        msg = f"{addr[0]} says: {data}"
        log_message(msg, sender="other")

        try:
            conn.sendall("ACK".encode('utf-8'))
        except:
            pass
        conn.close()

# Bind button
send_btn.config(command=send_button_clicked)
file_btn.config(command=browse_file)

# Start receiver
threading.Thread(target=receiver, daemon=True).start()

# Run app
app.mainloop()
