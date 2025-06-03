import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# --------------------------------------------------
#   Función para encontrar recursos (imágenes, .exe, .ico)
#   tanto en modo script como en modo PyInstaller
# --------------------------------------------------
def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


# --------------------------------------------------
#   Callbacks que lanzan cada .exe
# --------------------------------------------------
def launch_qr_generator():
    ruta_exe = resource_path("Yuuruii Qr Generator.exe")
    if os.path.isfile(ruta_exe):
        try:
            os.startfile(ruta_exe)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar:\n{e}")
    else:
        messagebox.showerror("Error", "No se encontró 'Yuuruii Qr Generator.exe'")

def launch_extension_manager():
    ruta_exe = resource_path("Yuuruii Extension Manager.exe")
    if os.path.isfile(ruta_exe):
        try:
            os.startfile(ruta_exe)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar:\n{e}")
    else:
        messagebox.showerror("Error", "No se encontró 'Yuuruii Extension Manager.exe'")

def launch_background_remover():
    ruta_exe = resource_path("Yuuruii Background remover.exe")
    if os.path.isfile(ruta_exe):
        try:
            os.startfile(ruta_exe)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar:\n{e}")
    else:
        messagebox.showerror("Error", "No se encontró 'Yuuruii Background remover.exe'")

def launch_db_manager():
    ruta_exe = resource_path("Yuuruii DataBase Manager.exe")
    if os.path.isfile(ruta_exe):
        try:
            os.startfile(ruta_exe)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar:\n{e}")
    else:
        messagebox.showerror("Error", "No se encontró 'Yuuruii DataBase Manager.exe'")


# --------------------------------------------------
#   Funciones de la barra de título personalizada
# --------------------------------------------------
def on_close():
    """
    Al pulsar 'Cerrar', finalizamos cualquier proceso
    asociado a los ejecutables listados y luego cerramos la app.
    """
    procesos_a_terminar = [
        "Yuuruii DataBase Manager.exe",
        "Yuuruii Extension Manager.exe",
        "Yuuruii Qr Generator.exe",
        "Yuuruii Background remover.exe"
    ]

    for proceso in procesos_a_terminar:
        try:
            # /F fuerza la terminación, /IM indica el nombre de imagen (exe)
            subprocess.call(f'taskkill /F /IM "{proceso}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass  # Si falla, continuamos con el siguiente

    root.destroy()

def on_maximize_restore():
    global is_maximized
    if not is_maximized:
        global previous_geometry
        previous_geometry = root.geometry()
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        is_maximized = True
    else:
        root.geometry(previous_geometry)
        is_maximized = False

def start_move(event):
    root.x_click = event.x
    root.y_click = event.y

def on_move(event):
    x_new = root.winfo_x() + (event.x - root.x_click)
    y_new = root.winfo_y() + (event.y - root.y_click)
    root.geometry(f"+{x_new}+{y_new}")


# --------------------------------------------------
#  Configuración de la ventana principal
# --------------------------------------------------
root = tk.Tk()
root.title("Yuuruii tweaks")
root.overrideredirect(True)              # Oculta la barra nativa
root.configure(bg="#202020")             # Fondo oscuro
root.resizable(False, False)

# Tamaño fijo 800×300 y centrar en pantalla
window_width = 800
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
pos_x = (screen_width // 2) - (window_width // 2)
pos_y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

# Cargar el icono de la ventana usando resource_path
try:
    root.iconbitmap(resource_path("icono.ico"))
except Exception:
    pass


# --------------------------------------------------
#  Barra de título personalizada
# --------------------------------------------------
title_bar_height = 40
title_bar = tk.Frame(root, bg="#181818", relief="flat", height=title_bar_height)
title_bar.pack(fill="x")

lbl_title = tk.Label(
    title_bar,
    text="Yuuruii tweaks",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold")
)
lbl_title.pack(side="left", padx=10, pady=(0, 2))

btn_close = tk.Button(
    title_bar,
    text="✕",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=on_close
)
btn_close.pack(side="right", padx=(0, 10), pady=5)

btn_maximize = tk.Button(
    title_bar,
    text="▢",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=on_maximize_restore
)
btn_maximize.pack(side="right", padx=10, pady=5)

title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", on_move)
lbl_title.bind("<ButtonPress-1>", start_move)
lbl_title.bind("<B1-Motion>", on_move)


# --------------------------------------------------
#  Contenedor principal para los iconos y descripciones
# --------------------------------------------------
container = tk.Frame(root, bg="#202020")
container.place(
    x=0,
    y=title_bar_height + 10,
    width=window_width,
    height=window_height - title_bar_height - 20
)
# Dejamos 10 px de espacio sobre y bajo los iconos


# --------------------------------------------------
#  Cargamos las imágenes (144×144 px) para que ocupen
#  casi todo el interior del borde magenta (150×150)
# --------------------------------------------------
icons = {}
for key, fname in [
    ("qr", "qr.png"),
    ("ext", "ext.png"),
    ("bg", "bg.png"),
    ("db", "db.png")
]:
    try:
        # Redimensionamos a 144×144 para llenar el interior de 150×150 con borde de 3 px
        img = Image.open(resource_path(fname)).resize((144, 144), Image.Resampling.LANCZOS)
        icons[key] = ImageTk.PhotoImage(img)
    except Exception:
        icons[key] = None


# --------------------------------------------------
#  Función para crear cada “cuadro” con borde y texto
# --------------------------------------------------
def crear_cuadro(parent, icon_key, texto, comando):
    """
    Crea:
      1) un Frame cuadrado de 150×150 con borde magenta (3 px)
      2) un Button que ocupa todo el Frame y muestra solo la imagen
      3) un Label aparte, que se colocará debajo del Frame, con la descripción
    Devuelve (frame, label_descripcion).
    """
    # 1) Frame con borde magenta, tamaño fijo 150×150
    cuadro = tk.Frame(
        parent,
        bg="#181818",
        highlightthickness=3,
        highlightbackground="#FF00FF",
        width=150,
        height=150
    )
    cuadro.grid_propagate(False)  # Para que no cambie de tamaño

    # 2) Botón solo con imagen (sin texto), que llene todo el Frame
    btn = tk.Button(
        cuadro,
        bg="#181818",
        activebackground="#FF5555",
        bd=0,
        relief="flat",
        command=comando,
        image=icons.get(icon_key)
    )
    btn.pack(expand=True, fill="both")  # La imagen ocupará casi todo el espacio interior

    # 3) Label con texto descriptivo: se creará en el mismo contenedor padre,
    #    pero se posicionará fuera (debajo) del “cuadro” magenta.
    label_desc = tk.Label(
        parent,
        text=texto,
        bg="#202020",
        fg="#FF00FF",
        font=("Segoe UI", 11)
    )

    return cuadro, label_desc


# --------------------------------------------------
#  Creamos los cuatro cuadros (150×150) y sus labels
# --------------------------------------------------
cuadro_qr,  label_qr  = crear_cuadro(container, "qr",  "Qr Generator",          launch_qr_generator)
cuadro_ext, label_ext = crear_cuadro(container, "ext", "Extension Manager",     launch_extension_manager)
cuadro_bg,  label_bg  = crear_cuadro(container, "bg",  "Background Remover",    launch_background_remover)
cuadro_db,  label_db  = crear_cuadro(container, "db",  "Db Manager",            launch_db_manager)

# --------------------------------------------------
#  Calculamos pad_x para distribuir 4 cuadros en 800 px
#  Cada cuadro mide 150 px, así que quedan 800 - 4×150 = 200 px libres
#  Lo dividimos en 5 espacios iguales: (200 / 5) = 40 px
# --------------------------------------------------
pad_x = (window_width - 4 * 150) // 5  # (800 - 600) / 5 = 40

# --------------------------------------------------
#  Ubicamos los cuadros y las etiquetas descriptivas
#  - Los cuadros (de 150×150) se ponen en y = 10
#  - Las etiquetas (de 150 px de ancho) se ponen en y = 10 + 150 + 5 = 165
# --------------------------------------------------
y_cuadro = 10
y_label  = y_cuadro + 150 + 5  # 165

# Qr Generator
cuadro_qr.place(x=pad_x,                      y=y_cuadro)
label_qr.place(x=pad_x,                       y=y_label, width=150)

# Extension Manager
cuadro_ext.place(x=pad_x * 2 + 150,            y=y_cuadro)
label_ext.place(x=pad_x * 2 + 150,             y=y_label, width=150)

# Background Remover
cuadro_bg.place(x=pad_x * 3 + 300,             y=y_cuadro)
label_bg.place(x=pad_x * 3 + 300,              y=y_label, width=150)

# Db Manager
cuadro_db.place(x=pad_x * 4 + 450,             y=y_cuadro)
label_db.place(x=pad_x * 4 + 450,              y=y_label, width=150)


# --------------------------------------------------
#  Estado para maximizar/restaurar (aunque la ventana es fija)
# --------------------------------------------------
is_maximized = False
previous_geometry = root.geometry()


# --------------------------------------------------
#  Inicia el loop principal de Tkinter
# --------------------------------------------------
root.mainloop()
