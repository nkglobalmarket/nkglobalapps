@echo off
title NK Global Apps - Tam Otomatik Kurulum
color 0b

:: Sistemde Python var mı diye kontrol et
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ==============================================================
    echo      Sistemde Python bulunamadi! Sifir PC algilandi.
    echo      Python otomatik olarak indiriliyor, lutfen bekleyin...
    echo ==============================================================
    
    curl -L -o python_setup.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    
    echo.
    echo Kurulum yapiliyor, lutfen pencereyi KAPATMAYIN...
    echo Bu islem bilgisayar hizina gore 1-2 dakika surebilir.
    
    start /wait python_setup.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    
    echo.
    echo Python kurulumu basarili! Gecici dosyalar temizleniyor...
    del python_setup.exe
) else (
    echo ==============================================================
    echo      Python sistemde zaten kurulu, kuruluma devam ediliyor...
    echo ==============================================================
)

echo.
echo ==============================================================
echo      Gerekli Kutuphaneler Indiriliyor (customtkinter, bs4 vb.)
echo ==============================================================
py -m pip install --upgrade pip >nul 2>&1
py -m pip install customtkinter requests beautifulsoup4 pillow

echo.
echo ==============================================================
echo      Uygulama Dosyalari Guncelleniyor/Indiriliyor...
echo ==============================================================

:: GitHub'daki dosyayı main.py olarak indirir
curl -L -o main.py https://raw.githubusercontent.com/nkglobalmarket/nkglobalapps/refs/heads/main/main.py

echo.
echo ==============================================================
echo      Her Sey Hazir! NK Global Apps Baslatiliyor...
echo ==============================================================

:: Programı başlat (siyah konsol ekranı olmadan açılması için pyw kullanılır)
start "" pyw main.py

:: CMD ekranını kapat
exit
