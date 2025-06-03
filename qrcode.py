import os
import sys
import json
import segno
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.parse import urlparse
from PIL import Image, ImageTk

# --------------------------------------------------
#   Función para obtener la ruta de recursos 
#   (imágenes, .exe, .ico) tanto en modo script 
#   como en modo PyInstaller
# --------------------------------------------------
def resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona tanto para desarrollo como para .exe"""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --------------------------------------------------
#   Funciones de la barra de título personalizada
# --------------------------------------------------
def on_close():
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
#   Funciones de generación de QR
# --------------------------------------------------
def generar_qr_multiformato(url, progress_var=None, status_label=None):
    try:
        # Actualizar estado
        if status_label:
            status_label.config(text="Preparando...")
            status_label.update()

        parsed_url = urlparse(url)
        dominio = parsed_url.netloc
        if not dominio:
            dominio = parsed_url.path.split('/')[0]
        if not dominio:
            dominio = "url"
        dominio_seguro = ''.join(c if c.isalnum() or c in '.-' else '_' for c in dominio)

        carpeta_qr = os.path.join(resource_path(""), "qr")
        if not os.path.exists(carpeta_qr):
            os.makedirs(carpeta_qr)

        if progress_var:
            progress_var.set(20)
            if status_label:
                status_label.config(text="Creando carpetas...")
                status_label.update()

        carpeta_dominio = os.path.join(carpeta_qr, dominio_seguro)
        if not os.path.exists(carpeta_dominio):
            os.makedirs(carpeta_dominio)

        qr = segno.make(url)
        nombre_base = f"qr-{dominio_seguro}"
        ruta_svg = os.path.join(carpeta_dominio, f"{nombre_base}.svg")
        ruta_png = os.path.join(carpeta_dominio, f"{nombre_base}.png")
        ruta_jpg = os.path.join(carpeta_dominio, f"{nombre_base}.jpg")

        if status_label:
            status_label.config(text="Generando SVG...")
            status_label.update()
        qr.save(ruta_svg, scale=5)

        if progress_var:
            progress_var.set(40)
            if status_label:
                status_label.config(text="Generando PNG...")
                status_label.update()

        qr.save(ruta_png, scale=10, border=4)

        if progress_var:
            progress_var.set(60)
            if status_label:
                status_label.config(text="Generando JPG...")
                status_label.update()

        from PIL import Image as PILImage
        png_img = PILImage.open(ruta_png)
        rgb_img = png_img.convert('RGB')
        rgb_img.save(ruta_jpg, quality=95)

        if progress_var:
            progress_var.set(80)
            if status_label:
                status_label.config(text="Guardando información...")
                status_label.update()

        datos = {
            "url_redireccion": url,
            "archivos_generados": {
                "svg": os.path.abspath(ruta_svg),
                "png": os.path.abspath(ruta_png),
                "jpg": os.path.abspath(ruta_jpg)
            }
        }
        ruta_json = os.path.join(carpeta_dominio, "qr_info.json")
        with open(ruta_json, "w") as json_file:
            json.dump(datos, json_file, indent=4)

        if progress_var:
            progress_var.set(100)
            if status_label:
                status_label.config(text="¡Completado!")
                status_label.update()

        return {
            "svg": ruta_svg,
            "png": ruta_png,
            "jpg": ruta_jpg,
            "info": ruta_json,
            "carpeta": carpeta_dominio
        }
    except Exception as e:
        if status_label:
            status_label.config(text=f"Error: {str(e)}")
        return None

def abrir_carpeta(ruta):
    import platform
    if platform.system() == "Windows":
        os.startfile(ruta)
    elif platform.system() == "Darwin":
        os.system(f"open '{ruta}'")
    else:
        os.system(f"xdg-open '{ruta}'")

def generar_qr_gui():
    url = entrada_url.get().strip()
    if not url:
        messagebox.showerror("Error", "Por favor, introduce una URL válida")
        return
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        entrada_url.delete(0, tk.END)
        entrada_url.insert(0, url)

    progress_var.set(0)
    barra_progreso.pack(fill="x", padx=20, pady=(10, 0))
    etiqueta_estado.pack(fill="x", padx=20, pady=(5, 10))
    root.update()

    resultado = generar_qr_multiformato(url, progress_var, etiqueta_estado)
    if resultado:
        etiqueta_estado.config(text="¡Códigos QR generados con éxito!")
        boton_abrir = tk.Button(
            content_frame,
            text="Abrir carpeta con los archivos",
            bg="#181818",
            fg="#FF00FF",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            activebackground="#FF5555",
            activeforeground="#FFFFFF",
            command=lambda: abrir_carpeta(resultado["carpeta"]),
            padx=15,
            pady=8
        )
        boton_abrir.pack(pady=(10, 5))
        info_text = (
            f"Archivos generados en: {resultado['carpeta']}\n\n"
            f"SVG: {os.path.basename(resultado['svg'])}\n"
            f"PNG: {os.path.basename(resultado['png'])}\n"
            f"JPG: {os.path.basename(resultado['jpg'])}"
        )
        label_info = tk.Label(
            content_frame,
            text=info_text,
            bg="#202020",
            fg="white",
            font=("Segoe UI", 10),
            justify="left"
        )
        label_info.pack(fill="x", padx=20, pady=(5, 10))
    else:
        etiqueta_estado.config(text="Error al generar los códigos QR")

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# --------------------------------------------------
#  Configuración de la ventana principal
# --------------------------------------------------
root = tk.Tk()
root.title("Yuuruii QR Generator")
root.overrideredirect(True)
root.configure(bg="#202020")
root.resizable(False, False)

window_width = 800
window_height = 400
center_window(root, window_width, window_height)

try:
    root.iconbitmap(resource_path("icono.ico"))
except Exception:
    pass

# Barra de título personalizada
title_bar = tk.Frame(root, bg="#181818", height=40)
title_bar.pack(fill="x")

lbl_title = tk.Label(
    title_bar,
    text="Yuuruii QR Generator",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold")
)
lbl_title.pack(side="left", padx=10, pady=6)

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
btn_close.pack(side="right", padx=(0, 10), pady=6)

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
btn_maximize.pack(side="right", padx=10, pady=6)

title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", on_move)
lbl_title.bind("<ButtonPress-1>", start_move)
lbl_title.bind("<B1-Motion>", on_move)

# --------------------------------------------------
#  Contenedor principal para widgets
# --------------------------------------------------
content_frame = tk.Frame(root, bg="#202020")
content_frame.place(x=0, y=40, width=window_width, height=window_height - 40)

lbl_encabezado = tk.Label(
    content_frame,
    text="Generador de Códigos QR",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 16, "bold")
)
lbl_encabezado.pack(pady=(20, 10))

entrada_url = tk.Entry(
    content_frame,
    bg="#181818",
    fg="white",
    insertbackground="white",
    font=("Segoe UI", 11),
    width=40,
    bd=0
)
entrada_url.pack(pady=(0, 10))

btn_generar = tk.Button(
    content_frame,
    text="Generar QR",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=generar_qr_gui,
    padx=15,
    pady=8
)
btn_generar.pack(pady=(0, 10))

progress_var = tk.IntVar()
barra_progreso = ttk.Progressbar(
    content_frame,
    orient="horizontal",
    mode="determinate",
    maximum=100,
    variable=progress_var
)
# inicialmente no visible hasta iniciar proceso

etiqueta_estado = tk.Label(
    content_frame,
    text="",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10)
)
# inicialmente no visible hasta iniciar proceso

# Estado de maximizado/restaurar
is_maximized = False
previous_geometry = root.geometry()

root.mainloop()
