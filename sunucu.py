import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import re
import shutil
import urllib.request
import json
from datetime import datetime

# --- GOOGLE DRIVE WEBHOOK AYARI ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzmcMPl84QRcRxhmumoQcH4mujwJd8eeGqW4o7tVQ1gEu8_JURBP2X5IyND8FmWrgz6/exec"

folder_path = ""
public_url = ""
server_process = None
tunnel_process = None


def update_drive_json(new_url):
    """Üretilen linki Google Apps Script üzerinden Drive'daki JSON'a yazar."""
    try:
        content = {
            "url": new_url,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Veriyi JSON formatına çevir
        data = json.dumps(content).encode('utf-8')
        
        # Google Script'e POST isteği at
        req = urllib.request.Request(WEB_APP_URL, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"Drive Güncelleme Sonucu: {result}") # Terminalde başarılı yazısını görebilirsin
            
    except Exception as e:
        print(f"Hata: Link Drive'a gönderilemedi: {e}")


def check_cloudflared():
    if shutil.which("cloudflared") is None:
        status_var.set("Cloudflared bulunamadı. Kuruluyor...")
        try:
            subprocess.run(
                ["winget", "install", "--id", "Cloudflare.cloudflared", "-e"],
                check=True
            )
            status_var.set("Cloudflared kuruldu.")
        except:
            messagebox.showerror("Hata", "Cloudflared kurulamadı!")
            return False
    return True


def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    folder_var.set(folder_path)


def start_server():
    if not folder_path:
        messagebox.showwarning("Uyarı", "Önce klasör seçin")
        return

    update_ui("starting")
    threading.Thread(target=run_server).start()


def run_server():
    global server_process, tunnel_process, public_url

    if not check_cloudflared():
        return

    server_process = subprocess.Popen(
        ["python", "-m", "http.server", "8000"],
        cwd=folder_path
    )

    tunnel_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8000", "--protocol", "http2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in tunnel_process.stdout:
        match = re.search(r"https://[-a-zA-Z0-9]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            link_var.set(public_url)
            update_ui("running")
            
            # --- LİNK BULUNDUĞUNDA DRIVE'I GÜNCELLE ---
            threading.Thread(target=update_drive_json, args=(public_url,)).start()
            # ------------------------------------------
            break


def stop_server():
    global server_process, tunnel_process

    if server_process:
        server_process.terminate()

    if tunnel_process:
        tunnel_process.terminate()

    link_var.set("")
    update_ui("stopped")


def toggle_server():
    if server_process and server_process.poll() is None:
        stop_server()
    else:
        start_server()


def copy_link():
    root.clipboard_clear()
    root.clipboard_append(link_var.get())


# GUI
root = tk.Tk()
root.title("Cloud Dosya Sunucusu")
root.geometry("520x300")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Klasör Seç:").pack(anchor="w", pady=5)
folder_var = tk.StringVar()
folder_entry = ttk.Entry(frame, textvariable=folder_var, width=60, state="readonly")
folder_entry.pack(pady=5)
select_button = ttk.Button(frame, text="Seç", command=select_folder)
select_button.pack(pady=5)

ttk.Separator(frame).pack(fill="x", pady=10)

ttk.Label(frame, text="Public Link:").pack(anchor="w", pady=5)
link_var = tk.StringVar()
link_entry = ttk.Entry(frame, textvariable=link_var, width=60, state="readonly")
link_entry.pack(pady=5)
copy_button = ttk.Button(frame, text="Kopyala", command=copy_link, state="disabled")
copy_button.pack(pady=5)

toggle_button = ttk.Button(frame, text="Başlat", command=toggle_server)
toggle_button.pack(pady=10)

status_var = tk.StringVar(value="Hazır [STANDBY]")
status_label = ttk.Label(frame, textvariable=status_var, foreground="orange", font=("Courier New", 10, "bold"))
status_label.pack(pady=15)


def update_ui(state):
    if state == "running":
        toggle_button.config(text="Durdur", state="normal")
        copy_button.config(state="normal")
        status_var.set("Sunucu aktif []")
        status_label.config(foreground="green")
    elif state == "stopped":
        toggle_button.config(text="Başlat", state="normal")
        copy_button.config(state="disabled")
        status_var.set("Sunucu durduruldu [OFFLINE]")
        status_label.config(foreground="red")
    elif state == "starting":
        toggle_button.config(text="Başlatılıyor...", state="disabled")
        copy_button.config(state="disabled")
        status_var.set("Sunucu başlatılıyor... [MATRİX AKTİF]")
        status_label.config(foreground="yellow")
    else:  # ready
        toggle_button.config(text="Başlat", state="normal")
        copy_button.config(state="disabled")
        status_var.set("Hazır [STANDBY]")
        status_label.config(foreground="orange")


update_ui("ready")

root.mainloop()
