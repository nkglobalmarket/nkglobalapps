import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import os
import subprocess
import threading
import time
from tkinter import messagebox
from PIL import Image
from io import BytesIO

# --- AYARLAR ---
JSON_URL = "https://drive.google.com/uc?export=download&id=1yArm1-y23_62z_xV0pZ2omgkTyu2GKNq"
DOWNLOAD_DIR = r"C:\NK"

if not os.path.exists(DOWNLOAD_DIR):
    try:
        os.makedirs(DOWNLOAD_DIR)
    except Exception as e:
        messagebox.showerror("Yetki Hatası", f"C diskine klasör açılamadı.\nHata: {e}")

# --- YARDIMCI FONKSİYONLAR ---
def format_size(size_in_bytes):
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

# --- AÇILIŞ EKRANI (SPLASH SCREEN) ---
class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Açılış")
        center_window(self, 600, 350)
        self.overrideredirect(True) 
        ctk.set_appearance_mode("dark")
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#1a1a1a", border_width=2, border_color="#3498db")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(self.main_frame, text="NK GLOBAL APPS", font=("Segoe UI Black", 45), text_color="#3498db")
        self.title_label.pack(expand=True, pady=(50, 0))

        self.percent_label = ctk.CTkLabel(self.main_frame, text="%0", font=("Segoe UI", 24, "bold"), text_color="white")
        self.percent_label.pack(pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400, height=12, corner_radius=10, progress_color="#2ecc71")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 10))

        self.info_label = ctk.CTkLabel(self.main_frame, text="Sistem Başlatılıyor...", font=("Segoe UI", 13), text_color="#7f8c8d")
        self.info_label.pack(pady=(0, 30))

        self.warning_label = ctk.CTkLabel(self.main_frame, text="STABİL KURULUM İÇİN VİRUS PROGRAMINI DEVREDIŞI BIRAKIN ", 
                                         font=("Segoe UI", 10, "bold"), text_color="white")
        self.warning_label.place(relx=0.02, rely=0.98, anchor="sw")

        self.credit_label = ctk.CTkLabel(self.main_frame, text="CREATED BY KEMAL ÖZKUL", font=("Segoe UI", 11, "bold"), text_color="white")
        self.credit_label.place(relx=0.98, rely=0.98, anchor="se")

        self.progress = 0
        self.server_ready = False
        self.target_url = None

        threading.Thread(target=self.fetch_server_info).start()
        self.update_progress()

    def fetch_server_info(self):
        try:
            response = requests.get(JSON_URL, timeout=8)
            self.target_url = response.json().get("url")
        except:
            self.target_url = None
        finally:
            self.server_ready = True 

    def update_progress(self):
        if self.progress < 100:
            if self.progress == 99 and not self.server_ready:
                self.after(100, self.update_progress)
                return
            self.progress += 1
            self.progress_bar.set(self.progress / 100)
            self.percent_label.configure(text=f"%{self.progress}")
            self.after(70, self.update_progress) 
        else:
            self.after(600, self.launch_main_app) 

    def launch_main_app(self):
        self.destroy() 
        app = AppInstaller(pre_fetched_url=self.target_url) 
        app.mainloop()

# --- ANA UYGULAMA ---
class AppInstaller(ctk.CTk):
    def __init__(self, pre_fetched_url=None):
        super().__init__()

        self.title("NK GLOBAL APPS")
        center_window(self, 950, 720) 
        ctk.set_appearance_mode("dark")

        self.target_url = pre_fetched_url
        self.download_events = {} # İptal işlemlerini takip etmek için sözlük

        self.header_frame = ctk.CTkFrame(self, height=80, fg_color="#1e1e1e", corner_radius=10)
        self.header_frame.pack(fill="x", padx=20, pady=15)
        
        self.label = ctk.CTkLabel(self.header_frame, text="NK GLOBAL APPS", font=("Segoe UI Black", 28), text_color="#3498db")
        self.label.pack(side="left", padx=20, pady=20)

        self.refresh_btn = ctk.CTkButton(self.header_frame, text="🔄 Yenile", width=80, fg_color="#8e44ad", hover_color="#9b59b6",
                                        command=self.refresh_programs)
        self.refresh_btn.pack(side="right", padx=10)

        self.status_label = ctk.CTkLabel(self.header_frame, text="Sistem Hazır", font=("Segoe UI", 13), text_color="#7f8c8d")
        self.status_label.pack(side="right", padx=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=850, height=450, fg_color="transparent")
        self.scrollable_frame.pack(pady=5, padx=20, fill="both", expand=True)
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.footer_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", side="bottom", padx=20, pady=(5, 40)) 
        
        self.warning_label_main = ctk.CTkLabel(self.footer_frame, text="VİRUS PROGRAMINI DEVREDIŞI BIRAKIN STABİL KURULUM İÇİN", 
                                              font=("Segoe UI", 11, "bold"), text_color="white")
        self.warning_label_main.pack(side="left")

        self.clean_btn = ctk.CTkButton(self.footer_frame, text="🗑️ Temizle", width=110,
                                      fg_color="#c0392b", hover_color="#e74c3c", font=("Segoe UI", 12, "bold"),
                                      command=self.clear_temp_files)
        self.clean_btn.pack(side="right", padx=(10, 0))

        self.open_folder_btn = ctk.CTkButton(self.footer_frame, text="📂 İndirilenler", width=120,
                                            fg_color="#27ae60", hover_color="#2ecc71", font=("Segoe UI", 12, "bold"),
                                            command=self.open_downloads_folder)
        self.open_folder_btn.pack(side="right", padx=10)

        self.credit_label_main = ctk.CTkLabel(self, text="CREATED BY KEMAL ÖZKUL", font=("Segoe UI", 10, "bold"), text_color="#FFF8F8")
        self.credit_label_main.place(relx=0.99, rely=0.995, anchor="se") 

        self.program_count = 0
        self.load_programs()

    def open_downloads_folder(self):
        if os.path.exists(DOWNLOAD_DIR): os.startfile(DOWNLOAD_DIR)

    def get_target_url(self):
        try:
            response = requests.get(JSON_URL, timeout=5)
            return response.json().get("url")
        except: return None

    def refresh_programs(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.program_count = 0
        self.target_url = None 
        threading.Thread(target=self.load_programs).start()

    def load_programs(self):
        if not self.target_url: self.target_url = self.get_target_url()
        if not self.target_url: return
        try:
            response = requests.get(self.target_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.lower().endswith(('.exe', '.cmd', '.bat')):
                    file_url = href if href.startswith('http') else self.target_url.rstrip('/') + '/' + href.lstrip('/')
                    original_filename = href.split('/')[-1]
                    icon_url = file_url.rsplit('.', 1)[0] + '.png'
                    self.create_program_card(original_filename, file_url, icon_url)
                    self.program_count += 1
            self.status_label.configure(text=f"{self.program_count} Program", text_color="#2ecc71")
        except: pass

    def create_program_card(self, original_filename, url, icon_url):
        name_without_ext = original_filename.rsplit('.', 1)[0]
        display_name = (name_without_ext[:12] + '..') if len(name_without_ext) > 12 else name_without_ext
        row, col = self.program_count // 4, self.program_count % 4
        card = ctk.CTkFrame(self.scrollable_frame, width=180, height=220, corner_radius=15, fg_color="#2b2b2b")
        card.grid(row=row, column=col, padx=15, pady=15)
        card.grid_propagate(False)

        avatar_frame = ctk.CTkFrame(card, width=65, height=65, corner_radius=35, fg_color="transparent")
        avatar_frame.pack(pady=(20, 10))
        avatar_frame.pack_propagate(False)
        
        colors = ["#1abc9c", "#3498db", "#9b59b6", "#e67e22", "#e74c3c"]
        avatar_color = colors[self.program_count % len(colors)]
        fallback_label = ctk.CTkLabel(avatar_frame, text=name_without_ext[0].upper(), font=("Segoe UI", 30, "bold"), text_color="white", fg_color=avatar_color, corner_radius=35)
        fallback_label.pack(expand=True, fill="both")

        threading.Thread(target=self.fetch_and_set_icon, args=(icon_url, avatar_frame, fallback_label)).start()
        ctk.CTkLabel(card, text=display_name, font=("Segoe UI", 14, "bold")).pack(pady=(5, 15))

        # Tek bir Kur butonu var
        install_btn = ctk.CTkButton(card, text="Kur", width=130, height=35, corner_radius=8, font=("Segoe UI", 14, "bold"), fg_color="#2980b9")
        install_btn.pack(side="bottom", pady=20)

        # Butona tıklandığında hem kurmayı hem iptal etmeyi yönetecek fonksiyonu bağlıyoruz
        install_btn.configure(command=lambda b=install_btn: self.handle_button_click(url, original_filename, b))

    def fetch_and_set_icon(self, icon_url, parent_frame, fallback_label):
        try:
            response = requests.get(icon_url, timeout=2)
            if response.status_code == 200:
                img_data = Image.open(BytesIO(response.content))
                img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(65, 65))
                fallback_label.destroy()
                ctk.CTkLabel(parent_frame, image=img, text="").pack(expand=True, fill="both")
        except: pass 

    def handle_button_click(self, url, original_filename, btn):
        # Eğer bu dosya şu an iniyorsa (sözlükte varsa) iptal et
        if original_filename in self.download_events:
            self.download_events[original_filename].set()
        else:
            # İnmiyorsa indirmeyi başlat
            threading.Thread(target=self.download_and_install, args=(url, original_filename, btn)).start()

    def download_and_install(self, url, original_filename, btn):
        try:
            # İptal sinyalini hazırlayalım
            cancel_event = threading.Event()
            self.download_events[original_filename] = cancel_event

            file_path = os.path.join(DOWNLOAD_DIR, original_filename)
            
            # DİKKAT: Butonu 'disabled' yapmıyoruz ki iptal etmek için tekrar tıklanabilsin.
            btn.configure(text="Bağlanıyor...", fg_color="#e67e22") 
            
            response = requests.get(url, stream=True, timeout=10)
            
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            total_size_formatted = format_size(total_size_in_bytes) if total_size_in_bytes else "Bilinmiyor"
            
            downloaded_bytes = 0
            last_update_time = time.time()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # Butona tekrar basıldıysa (iptal edildiyse) döngüyü kır
                    if cancel_event.is_set():
                        break

                    if chunk: 
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        
                        current_time = time.time()
                        if current_time - last_update_time > 0.1:
                            if total_size_in_bytes > 0:
                                percent = int((downloaded_bytes / total_size_in_bytes) * 100)
                                downloaded_formatted = format_size(downloaded_bytes)
                                
                                # Sadece yüzdeyi gösteriyoruz
                                btn.configure(text=f"%{percent}")
                                
                                self.status_label.configure(
                                    text=f"İndirilen: {downloaded_formatted} / {total_size_formatted}", 
                                    text_color="#f1c40f"
                                )
                                
                            last_update_time = current_time

            # Eğer iptal edildiyse temizlik yap
            if cancel_event.is_set():
                if os.path.exists(file_path):
                    os.remove(file_path) # Yarım inen dosyayı sil
                
                # Butonu kırmızı yap ve 1.5 saniye sonra tekrar "Kur" durumuna getir
                btn.configure(text="İptal Edildi", fg_color="#c0392b")
                self.status_label.configure(text="İndirme İptal Edildi!", text_color="#e74c3c")
                
                self.after(1500, lambda: btn.configure(text="Kur", fg_color="#2980b9"))
                self.after(1500, lambda: self.status_label.configure(text=f"{self.program_count} Program", text_color="#2ecc71"))
                return

            # Normal şekilde bittiyse programı aç
            btn.configure(text="Açılıyor...", fg_color="#f39c12", state="disabled")
            self.status_label.configure(text="İndirme Tamamlandı!", text_color="#2ecc71")
            
            subprocess.run(file_path, shell=True)
            btn.configure(text="Tamamlandı", fg_color="#27ae60")
            
            self.status_label.configure(text=f"{self.program_count} Program", text_color="#2ecc71")
            
        except Exception as e: 
            btn.configure(text="Hata!", fg_color="#c0392b", state="normal")
            self.status_label.configure(text="Bağlantı Hatası!", text_color="#c0392b")
        finally:
            # İşlem bitince indirme olayını sözlükten sil
            if original_filename in self.download_events:
                del self.download_events[original_filename]

    def clear_temp_files(self):
        if messagebox.askyesno("Temizlik", "Dosyalar silinsin mi?"):
            try:
                for file in os.listdir(DOWNLOAD_DIR): os.remove(os.path.join(DOWNLOAD_DIR, file))
                messagebox.showinfo("Başarılı", "Temizlendi.")
            except: pass

if __name__ == "__main__":
    splash = SplashScreen()
    splash.mainloop()