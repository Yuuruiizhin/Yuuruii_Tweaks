# Requieres pyinstaller
for compile in cmd use:
    cd {folder}
    pyinstaller --onefile --windowed --name "Yuuruii Background Remover" --icon icono.ico --add-data "icono.ico;." bgremove.py

or only pyinstaller string if u work in vs code space

# code dependencies:
os
sys
threading
io
tkinter
pillow
rembg 
datetime 