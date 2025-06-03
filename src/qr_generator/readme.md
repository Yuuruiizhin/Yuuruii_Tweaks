# Requieres pyinstaller
for compile in cmd use:
    cd {folder}
    pyinstaller --onefile --windowed --name "Yuuruii Qr Generator" --icon icono.ico --add-data "icono.ico;." qrcode.py

# or only pyinstaller string if u work in vs code space

# code dependencies:
os
sys
json
segno
tkinter
urllib
pillow