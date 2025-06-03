# icons
    db.png
    ext.png
    bg.png
    qr.png
# rute of images ../Yuuruii Tweaks SRC/icons/
# move the icons .png for main folder

# main instance

Requieres pyinstaller
Requieres all secondary apps compiled into folder: Yuuruii background remover, Yuuruii DataBase Manager, Yuuruii Extension Manager, Yuuruii Qr Generator
for compile in cmd use:

    cd {folder}

    pyinstaller --onefile --windowed --name "Yuuruii Tweaks" --icon icono.ico --add-data "icono.ico;." --add-data "Yuuruii Qr Generator.exe;." --add-data "Yuuruii Extension Manager.exe;." --add-data "Yuuruii DataBase Manager;." --add-data "Yuuruii Background Remover;." Yuuruii_Tweaks.py

for a correctly execute need a all inside icons: 

# the folder will look like:
C:\
└── /../
    └── /../
        └── Yuuruii Tweaks SRC
            ├── bg.png
            ├── db.png
            ├── ext.png
            ├── icono.ico
            ├── main.py
            ├── qr.png
            ├── Yuuruii background remover.exe
            ├── Yuuruii DataBase Manager.exe
            ├── Yuuruii Extension Manager.exe
            └── Yuuruii Qr Generator.exe


# or only pyinstaller string if u work in vs code space

# code dependencies:
os
sys
subprocess
tkinter
pillow