# Requieres pyinstaller
for compile in cmd use:
    cd {folder}
    pyinstaller --onefile --windowed --name "Yuuruii Extension Manager" --icon icono.ico --add-data "icono.ico;." filemanager.py

# or only pyinstaller string if u work in vs code space

# code dependencies:
os
sys
subprocess
tkinter as tk
tkinter
pillow
datetime