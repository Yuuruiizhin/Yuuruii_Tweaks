import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
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
#   Listas de extensiones admitidas
# --------------------------------------------------
IMAGE_FORMATS = {
    "jpeg", "jpg", "png", "bmp", "gif", "tiff", "heif", "raw", "psd",
    "ico", "webp"
}
VIDEO_FORMATS = {
    "mp4", "avi", "mkv", "flv", "mov", "wmv", "divx", "h264", "xvid", "rm", "webm"
}
AUDIO_FORMATS = {
    "wav", "aiff", "au", "flac", "m4a", "shn", "tta", "atrc", "alac",
    "mp3", "vorbis", "mpc", "aac", "wma", "opus", "ogg", "dsd", "mqa"
}

def obtener_extension(ruta):
    return os.path.splitext(ruta)[1].lower().lstrip(".")

def determinar_categoria(ext):
    if ext in IMAGE_FORMATS:
        return "imagen"
    elif ext in VIDEO_FORMATS:
        return "video"
    elif ext in AUDIO_FORMATS:
        return "audio"
    else:
        return None

def convertir_imagen(ruta_entrada, ruta_salida, formato_salida):
    try:
        img = Image.open(ruta_entrada)
        if formato_salida.lower() in {"jpeg", "jpg"}:
            img = img.convert("RGB")
        img.save(ruta_salida, formato_salida.upper())
        return True, None
    except Exception as e:
        return False, str(e)

def convertir_con_ffmpeg(ruta_entrada, ruta_salida):
    try:
        cmd = ["ffmpeg", "-y", "-i", ruta_entrada, ruta_salida]
        proceso = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proceso.returncode == 0:
            return True, None
        else:
            error_msg = proceso.stderr.decode("utf-8", errors="ignore")
            return False, error_msg
    except FileNotFoundError:
        return False, "No se encontró FFmpeg. Verifica que esté instalado y en tu PATH."
    except Exception as e:
        return False, str(e)

def abrir_en_explorador(ruta_carpeta):
    if sys.platform.startswith("win"):
        os.startfile(ruta_carpeta)
    elif sys.platform == "darwin":
        subprocess.run(["open", ruta_carpeta])
    else:
        subprocess.run(["xdg-open", ruta_carpeta])

# --------------------------------------------------
#   Clase principal: FileExtensionChanger con estilo “Yuuruii tweaks”
# --------------------------------------------------
class FileExtensionChanger(tk.Tk):
    def __init__(self):
        super().__init__()
        self._ruta_seleccionada = None
        self._categoria = None
        self._ultima_carpeta_salida = None

        # --------- Configuración de ventana ----------
        self.title("Yuuruii's File Extension Manager")
        self.overrideredirect(True)
        self.configure(bg="#202020")
        self.resizable(False, False)

        # Tamaño 800×350, centrado
        window_width = 800
        window_height = 350
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = (screen_w // 2) - (window_width // 2)
        pos_y = (screen_h // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        # Icono de la ventana (opcional: debe estar en misma carpeta)
        try:
            self.iconbitmap(resource_path("icono.ico"))
        except Exception:
            pass

        # Estado maximizado/restaurar
        self.is_maximized = False
        self.previous_geometry = self.geometry()

        # --------- Barra de título personalizada ----------
        title_bar = tk.Frame(self, bg="#181818", height=40)
        title_bar.pack(fill="x")

        lbl_title = tk.Label(
            title_bar,
            text="Yuuruii's File Extension Manager",
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
            command=self.on_close
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
            command=self.on_maximize_restore
        )
        btn_maximize.pack(side="right", padx=10, pady=6)

        # Permitir mover ventana desde la barra
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.on_move)
        lbl_title.bind("<ButtonPress-1>", self.start_move)
        lbl_title.bind("<B1-Motion>", self.on_move)

        # --------- Contenedor principal ----------
        container = tk.Frame(self, bg="#202020")
        container.place(x=0, y=40, width=800, height=310)

        # Encabezado dentro del contenedor
        lbl_encabezado = tk.Label(
            container,
            text="Cambio de Formato de Archivos",
            bg="#202020",
            fg="#FF00FF",
            font=("Segoe UI", 14, "bold")
        )
        lbl_encabezado.pack(pady=(20, 10))

        # Botón “Seleccionar archivo…”
        btn_seleccionar = tk.Button(
            container,
            text="Seleccionar archivo…",
            bg="#181818",
            fg="#FF00FF",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            activebackground="#FF5555",
            activeforeground="#FFFFFF",
            command=self._seleccionar_archivo,
            padx=20,
            pady=8
        )
        btn_seleccionar.pack(pady=(0, 15))

        # Etiqueta que muestra la ruta del archivo seleccionado
        self.lbl_ruta = tk.Label(
            container,
            text="No hay archivo seleccionado",
            bg="#202020",
            fg="gray",
            font=("Segoe UI", 10),
            wraplength=760,
            justify="center"
        )
        self.lbl_ruta.pack(pady=(0, 15))

        # Marco para combobox y botón “Convertir”
        marco_conv = tk.Frame(container, bg="#202020")
        marco_conv.pack(pady=(0, 15), padx=20, fill="x")

        lbl_formato = tk.Label(
            marco_conv,
            text="Formato de salida:",
            bg="#202020",
            fg="#FF00FF",
            font=("Segoe UI", 12)
        )
        lbl_formato.grid(row=0, column=0, sticky="e")

        # Combobox manual (sin ttk) usando OptionMenu
        self._formatos_var = tk.StringVar()
        self.optionmenu = tk.OptionMenu(
            marco_conv,
            self._formatos_var,
            ()
        )
        self.optionmenu.config(
            bg="#181818", fg="#FF00FF", font=("Segoe UI", 11),
            bd=0, activebackground="#FF5555", activeforeground="#FFFFFF",
            highlightthickness=0
        )
        self.optionmenu["menu"].config(
            bg="#181818", fg="#FF00FF", font=("Segoe UI", 10),
            bd=0, activebackground="#FF5555", activeforeground="#FFFFFF"
        )
        self.optionmenu.grid(row=0, column=1, padx=(10, 10), sticky="ew")

        btn_convertir = tk.Button(
            marco_conv,
            text="Convertir",
            bg="#181818",
            fg="#FF00FF",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            activebackground="#FF5555",
            activeforeground="#FFFFFF",
            command=self._convertir_archivo,
            padx=15,
            pady=6
        )
        btn_convertir.grid(row=0, column=2, padx=(10, 0))

        # Deshabilitar al inicio
        self._formatos_var.set("")
        self.optionmenu.config(state="disabled")
        btn_convertir.config(state="disabled")
        self.btn_convertir = btn_convertir

        # Botón “Abrir carpeta” (deshabilitado al inicio)
        btn_abrir = tk.Button(
            container,
            text="Abrir carpeta",
            bg="#181818",
            fg="#FF00FF",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            activebackground="#FF5555",
            activeforeground="#FFFFFF",
            command=self._abrir_carpeta_salida,
            padx=20,
            pady=8
        )
        btn_abrir.pack(pady=(0, 20))
        btn_abrir.config(state="disabled")
        self.btn_abrir = btn_abrir

    # -------------------------------------------------
    #   Métodos de barra de título (mover, minimizar...)
    # -------------------------------------------------
    def on_close(self):
        self.destroy()

    def on_maximize_restore(self):
        if not self.is_maximized:
            self.previous_geometry = self.geometry()
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self.is_maximized = True
        else:
            self.geometry(self.previous_geometry)
            self.is_maximized = False

    def start_move(self, event):
        self.x_click = event.x
        self.y_click = event.y

    def on_move(self, event):
        x_new = self.winfo_x() + (event.x - self.x_click)
        y_new = self.winfo_y() + (event.y - self.y_click)
        self.geometry(f"+{x_new}+{y_new}")

    # -------------------------------------------------
    #   Seleccionar archivo y poblar formatos disponibles
    # -------------------------------------------------
    def _seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        ext = obtener_extension(ruta)
        categoria = determinar_categoria(ext)
        if categoria is None:
            messagebox.showerror(
                "Formato no admitido",
                f"La extensión '.{ext}' no está en la lista de formatos soportados."
            )
            self._ruta_seleccionada = None
            self._categoria = None
            self.lbl_ruta.config(text="No hay archivo seleccionado", fg="gray")
            self.optionmenu.config(state="disabled")
            self._formatos_var.set("")
            self.btn_convertir.config(state="disabled")
            self.btn_abrir.config(state="disabled")
            return

        self._ruta_seleccionada = ruta
        self._categoria = categoria
        nombre_archivo = os.path.basename(ruta)
        self.lbl_ruta.config(text=f"Archivo seleccionado: {nombre_archivo}", fg="#FF00FF")

        formatos_disp = []
        if categoria == "imagen":
            formatos_disp = sorted(list(IMAGE_FORMATS - {ext}))
        elif categoria == "video":
            formatos_disp = sorted(list(VIDEO_FORMATS - {ext}))
        elif categoria == "audio":
            formatos_disp = sorted(list(AUDIO_FORMATS - {ext}))

        formatos_mostrar = [f.upper() for f in formatos_disp]
        # Reconstruir OptionMenu
        menu = self.optionmenu["menu"]
        menu.delete(0, "end")
        for fmt in formatos_mostrar:
            menu.add_command(
                label=fmt,
                command=lambda value=fmt: self._formatos_var.set(value)
            )
        if formatos_mostrar:
            self._formatos_var.set(formatos_mostrar[0])
            self.optionmenu.config(state="normal")
            self.btn_convertir.config(state="normal")
        else:
            self._formatos_var.set("")
            self.optionmenu.config(state="disabled")
            self.btn_convertir.config(state="disabled")

        self.btn_abrir.config(state="disabled")

    # -------------------------------------------------
    #   Convertir el archivo según categoría
    # -------------------------------------------------
    def _convertir_archivo(self):
        formato_salida = self._formatos_var.get().lower()
        ruta_entrada = self._ruta_seleccionada
        if not ruta_entrada or not formato_salida:
            messagebox.showerror("Error", "No se especificó el archivo o el formato de salida.")
            return

        raiz = os.path.dirname(os.path.abspath(sys.argv[0])) if not getattr(sys, "frozen", False) else os.path.dirname(sys.executable)
        carpeta_base = os.path.join(raiz, "Archive converter")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        carpeta_fecha = os.path.join(carpeta_base, fecha_hoy)
        os.makedirs(carpeta_fecha, exist_ok=True)

        nombre_sin_ext = os.path.splitext(os.path.basename(ruta_entrada))[0]
        ruta_salida = os.path.join(carpeta_fecha, f"{nombre_sin_ext}.{formato_salida}")

        if os.path.exists(ruta_salida):
            resp = messagebox.askyesno(
                "Sobrescribir",
                f"El archivo '{os.path.basename(ruta_salida)}' ya existe en:\n{carpeta_fecha}\n¿Deseas sobrescribirlo?"
            )
            if not resp:
                return

        if self._categoria == "imagen":
            exito, error_msg = convertir_imagen(ruta_entrada, ruta_salida, formato_salida)
        else:
            exito, error_msg = convertir_con_ffmpeg(ruta_entrada, ruta_salida)

        if exito:
            messagebox.showinfo(
                "Conversión exitosa",
                f"Se ha creado:\n\n{os.path.basename(ruta_salida)}\nen:\n{carpeta_fecha}"
            )
            self._ultima_carpeta_salida = carpeta_fecha
            self.btn_abrir.config(state="normal")
        else:
            messagebox.showerror(
                "Error en la conversión",
                f"No se pudo convertir el archivo.\n\nDetalles:\n{error_msg}"
            )
            self.btn_abrir.config(state="disabled")

    # -------------------------------------------------
    #   Abrir carpeta de salida en el explorador
    # -------------------------------------------------
    def _abrir_carpeta_salida(self):
        if self._ultima_carpeta_salida and os.path.isdir(self._ultima_carpeta_salida):
            abrir_en_explorador(self._ultima_carpeta_salida)
        else:
            messagebox.showerror("Error", "No se encontró la carpeta de salida.")


# --------------------------------------------------
#   Punto de entrada
# --------------------------------------------------
if __name__ == "__main__":
    # Verificar que Pillow esté instalado
    try:
        _ = Image
    except ImportError:
        messagebox.showerror(
            "Dependencia faltante",
            "La librería Pillow no está instalada.\nInstálala con:\n\npip install pillow"
        )
        sys.exit(1)

    app = FileExtensionChanger()
    app.mainloop()
