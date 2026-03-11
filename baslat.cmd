@echo off
title NK Global Apps - Tam Otomatik Kurulum
color 0b

:: Sistemde Python kontrolü
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ==============================================================
    echo     Sistemde Python bulunamadi!
    echo     Python otomatik olarak indiriliyor, lutfen bekleyin...
    echo ==============================================================
    
    curl -L -o python_setup.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    
    echo.
    echo Kurulum yapiliyor, lutfen pencereyi KAPATMAYIN...
    
    start /wait python_setup.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo.
    echo Python kurulumu basarili!
    del python_setup.exe
)

:: Gerekli kütüphanelerin kurulumu
echo ==============================================================
echo     Gerekli Kutuphaneler Kontrol Ediliyor...
echo ==============================================================
py -m pip install --upgrade pip >nul 2>&1
py -m pip install customtkinter requests beautifulsoup4 pillow >nul 2>&1

echo.
echo ==============================================================
echo     NK Global Apps GitHub'dan Yukleniyor ve Baslatiliyor...
echo ==============================================================

:: GitHub'daki kodu indirip arka planda calistiran Python komutu
:: Not: Bu komut kodu indirdikten sonra pyw ile sessizce baslatir.
py -c "import requests; code = requests.get('https://raw.githubusercontent.com/nkglobalmarket/nkglobalapps/refs/heads/main/main.py').text; exec(code)"

echo.
echo Islem tamamlandi.
exit
