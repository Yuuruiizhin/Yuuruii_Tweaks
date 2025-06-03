import os
import sys
import threading
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from rembg import remove
from datetime import datetime

# --------------------------------------------------
#   Función para obtener la ruta de recursos 
#   (imágenes, .exe, .ico) tanto en modo script 
#   como en modo PyInstaller
# --------------------------------------------------
def resource_path(filename):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

# --------------------------------------------------
#   Variables y carpetas para guardar resultados
# --------------------------------------------------
SCRIPT_DIR = resource_path("")  
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Yuuruii PNGS")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Evento para notificar al hilo principal cuando termine el procesamiento
done_event = threading.Event()

# Guardaremos la imagen 'full' en memoria para poder redibujarla si la ventana cambia de tamaño
current_image_full = None

# --------------------------------------------------
#   Funciones de procesamiento en segundo plano
# --------------------------------------------------
def procesar_en_segundo_plano(ruta_archivo):
    """
    Lee los bytes, elimina el fondo con rembg, crea miniatura,
    guarda la imagen y notifica al hilo principal.
    """
    global current_image_full
    try:
        # 1) Leer bytes originales
        with open(ruta_archivo, "rb") as f:
            datos_originales = f.read()

        # 2) Eliminar fondo (puede tardar)
        datos_sin_fondo = remove(datos_originales)

        # 3) Convertir a PIL.Image (full-res)
        imagen_full = Image.open(io.BytesIO(datos_sin_fondo)).convert("RGBA")
        current_image_full = imagen_full  # Guardamos la full-res

        # 4) Crear miniatura (300×300) para que quepa en ventana inicial de 800×350
        mini = imagen_full.copy()
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        mini.thumbnail((300, 300), resample)

        # 5) Guardar imagen full-res con nombre basado en fecha/hora
        ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_salida = f"{ahora}.png"
        ruta_salida = os.path.join(OUTPUT_DIR, nombre_salida)
        imagen_full.save(ruta_salida, format="PNG")

        # 6) Notificar al hilo principal
        done_event.set()
        root.after(0, lambda: finalizar_proceso(mini, ruta_salida))

    except Exception as e:
        done_event.set()
        root.after(0, lambda: mostrar_error(e))

def update_progress():
    """
    Simula el llenado de la barra de progreso. 
    Avanza mientras done_event no esté seteado.
    """
    if done_event.is_set():
        progress_bar["value"] = 100
        # Ocultamos la barra después de un breve retardo
        root.after(300, lambda: progress_bar.pack_forget())
    else:
        nuevo = progress_bar["value"] + 2
        progress_bar["value"] = min(nuevo, 99)
        root.after(100, update_progress)

def finalizar_proceso(imagen_miniatura, ruta_salida):
    """
    Muestra la miniatura, actualiza el texto y oculta la barra.
    """
    # Convertimos la miniatura a PhotoImage
    tk_img = ImageTk.PhotoImage(imagen_miniatura)
    label_imagen.config(image=tk_img)
    label_imagen.image = tk_img

    label_info.config(text=f"Imagen guardada en:\n{ruta_salida}")
    if progress_bar.winfo_ismapped():
        progress_bar.pack_forget()

def mostrar_error(error):
    """
    Oculta la barra si está visible y muestra un mensaje de error.
    """
    if progress_bar.winfo_ismapped():
        progress_bar.stop()
        progress_bar.pack_forget()
    messagebox.showerror("Error", f"No se pudo procesar la imagen:\n{error}")

def seleccionar_imagen():
    """
    1) Limpia info previa.
    2) Abre diálogo para seleccionar imagen.
    3) Configura y muestra la barra de progreso.
    4) Lanza el thread que procesará la imagen.
    """
    label_info.config(text="")
    label_imagen.config(image="")
    label_imagen.image = None

    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if not ruta:
        return

    done_event.clear()
    progress_bar["mode"] = "determinate"
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    if not progress_bar.winfo_ismapped():
        # Mostramos la barra de progreso ocupando todo el ancho disponible
        progress_bar.pack(fill="x", padx=20, pady=10)

    root.after(100, update_progress)

    hilo = threading.Thread(
        target=procesar_en_segundo_plano,
        args=(ruta,),
        daemon=True
    )
    hilo.start()

def abrir_carpeta():
    """
    Abre la carpeta OUTPUT_DIR en el explorador (Windows).
    """
    try:
        os.startfile(OUTPUT_DIR)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")

# --------------------------------------------------
#   Funciones de la barra de título personalizada
# --------------------------------------------------
def on_close():
    root.destroy()

def on_maximize_restore():
    """
    Al hacer clic en maximizar/restaurar:
     - Si no está maximizado, expandimos a pantalla completa.
     - Si ya estaba maximizado, volvemos a la geometría previa.
    """
    global is_maximized
    if not is_maximized:
        # Guardamos la geometría anterior
        global previous_geometry
        previous_geometry = root.geometry()
        # Maximizamos ocupando toda la pantalla
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        is_maximized = True
    else:
        # Restauramos la geometría previa
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
#   Configuración de la ventana principal
# --------------------------------------------------
root = tk.Tk()
root.title("Yuuruii’s Background Remover")
root.overrideredirect(True)            # Oculta la barra nativa
root.configure(bg="#202020")
# Permitimos redimensionar la ventana
root.resizable(True, True)

# Tamaño inicial 800×350 y centrar en pantalla
window_width = 800
window_height = 350
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
pos_x = (screen_w // 2) - (window_width // 2)
pos_y = (screen_h // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

# Cargar icono de ventana (opcional)
try:
    root.iconbitmap(resource_path("bg.png"))
except Exception:
    pass

# --------------------------------------------------
#  Barra de título personalizada
# --------------------------------------------------
title_bar = tk.Frame(root, bg="#181818", height=40)
title_bar.pack(fill="x")

lbl_title = tk.Label(
    title_bar,
    text="Yuuruii’s Background Remover",
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
#  Contenedor principal (ahora con pack para ser responsive)
# --------------------------------------------------
container = tk.Frame(root, bg="#202020")
container.pack(fill="both", expand=True)

# --------------------------------------------------
#  Widgets del Background Remover
# --------------------------------------------------

# Etiqueta instructiva
label_instruccion = tk.Label(
    container,
    text="Seleccione una imagen para eliminar su fondo",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 14)
)
label_instruccion.pack(pady=(20, 10))

# Botón "Cargar imagen…"
btn_cargar = tk.Button(
    container,
    text="Cargar imagen…",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=seleccionar_imagen,
    padx=20,
    pady=10
)
btn_cargar.pack(pady=(0, 15))

# Barra de progreso (oculta hasta iniciar un proceso)
progress_bar = ttk.Progressbar(
    container,
    orient="horizontal",
    mode="determinate"
)
# NOTA: la barra se empaquetará dinámicamente en seleccionar_imagen()

# Label para mostrar la miniatura resultante
label_imagen = tk.Label(container, bg="#202020")
label_imagen.pack(pady=10)

# Label para mostrar la ruta de guardado o estado
label_info = tk.Label(
    container,
    text="",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10),
    justify="center"
)
label_info.pack(pady=5)

# Botón "Abrir carpeta de salida"
btn_abrir = tk.Button(
    container,
    text="Abrir carpeta de salida",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 12, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=abrir_carpeta,
    padx=20,
    pady=10
)
btn_abrir.pack(pady=(15, 20))

# --------------------------------------------------
#  Estado para maximizar/restaurar
# --------------------------------------------------
is_maximized = False
previous_geometry = root.geometry()

# --------------------------------------------------
#  Inicia el bucle principal de Tkinter
# --------------------------------------------------
root.mainloop()
