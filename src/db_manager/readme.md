# Requieres pyinstaller
for compile in cmd use:
    cd {folder}
    pyinstaller --onefile --windowed --name "Yuuruii DataBase Manager" --icon icono.ico --add-data "icono.ico;." dbmanager.py

or only pyinstaller string if u work in vs code space

# code dependencies:
os
sys
tkinter as tk
tkinter
mysql.connector