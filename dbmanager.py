import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector

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
#   Funciones de la barra de título personalizada
#   (sin botón de minimizar)
# --------------------------------------------------
def on_close(window):
    window.destroy()

def on_maximize_restore(window, state):
    if not state["is_maximized"]:
        state["previous_geometry"] = window.geometry()
        window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")
        state["is_maximized"] = True
    else:
        window.geometry(state["previous_geometry"])
        state["is_maximized"] = False

def start_move(window, event):
    window.x_click = event.x
    window.y_click = event.y

def on_move(window, event):
    x_new = window.winfo_x() + (event.x - window.x_click)
    y_new = window.winfo_y() + (event.y - window.y_click)
    window.geometry(f"+{x_new}+{y_new}")

# --------------------------------------------------
#   Conexión a la base de datos
# --------------------------------------------------
def conectar_bd():
    global conexion, cursor
    host = entrada_host.get().strip()
    usuario = entrada_usuario.get().strip()
    contraseña = entrada_contraseña.get().strip()
    base_datos = entrada_base_datos.get().strip()
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=usuario,
            password=contraseña,
            database=base_datos
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT DATABASE()")
        bd = cursor.fetchone()[0]
        messagebox.showinfo("Conexión exitosa", f"Conectado a la base de datos: {bd}")
        ventana_login.destroy()
        abrir_ventana_principal()
    except mysql.connector.Error as err:
        messagebox.showerror("Error de conexión", f"No se pudo conectar:\n{err}")

# --------------------------------------------------
#   Ventana principal con estilo Yuuruii tweaks
# --------------------------------------------------
def abrir_ventana_principal():
    global tabla_var, tabla_actual, cursor, conexion

    ventana = tk.Tk()
    ventana.title("Yuuruii's Db Manager")
    ventana.overrideredirect(True)
    ventana.configure(bg="#202020")
    ventana.resizable(False, False)

    # Asignar icono a la ventana principal
    try:
        ventana.iconbitmap(resource_path("icono.ico"))
    except Exception:
        pass

    window_width = 600
    window_height = 400
    screen_w = ventana.winfo_screenwidth()
    screen_h = ventana.winfo_screenheight()
    pos_x = (screen_w // 2) - (window_width // 2)
    pos_y = (screen_h // 2) - (window_height // 2)
    ventana.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    state = {"is_maximized": False, "previous_geometry": ventana.geometry()}

    # Barra de título
    title_bar = tk.Frame(ventana, bg="#181818", height=35)
    title_bar.pack(fill="x")

    lbl_title = tk.Label(
        title_bar,
        text="Yuuruii's Db Manager",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 12, "bold")
    )
    lbl_title.pack(side="left", padx=10, pady=5)

    btn_close = tk.Button(
        title_bar,
        text="✕",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 12, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_close(ventana)
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
        command=lambda: on_maximize_restore(ventana, state)
    )
    btn_maximize.pack(side="right", padx=10, pady=5)

    title_bar.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    title_bar.bind("<B1-Motion>", lambda e: on_move(ventana, e))
    lbl_title.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    lbl_title.bind("<B1-Motion>", lambda e: on_move(ventana, e))

    # Contenedor principal
    container = tk.Frame(ventana, bg="#202020")
    container.place(x=0, y=35, width=window_width, height=window_height - 35)

    tabla_var = tk.StringVar(value="No hay ninguna tabla en uso")
    lbl_estado = tk.Label(
        container,
        textvariable=tabla_var,
        bg="#202020",
        fg="#FF00FF",
        font=("Segoe UI", 12)
    )
    lbl_estado.pack(pady=(20, 10))

    def crear_boton(texto, comando):
        return tk.Button(
            container,
            text=texto,
            bg="#181818",
            fg="#FF00FF",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            activebackground="#FF5555",
            activeforeground="#FFFFFF",
            command=comando,
            padx=15,
            pady=8
        )

    btn_sel_tabla = crear_boton("Seleccionar tabla", seleccionar_tabla)
    btn_sel_tabla.pack(pady=5)

    btn_ver = crear_boton("Ver valores de la tabla", ver_registros)
    btn_ver.pack(pady=5)

    btn_agregar = crear_boton("Agregar valores a la tabla", agregar_registro)
    btn_agregar.pack(pady=5)

    btn_eliminar = crear_boton("Eliminar valores de la tabla", eliminar_registro)
    btn_eliminar.pack(pady=5)

    btn_buscar = crear_boton("Buscar valor por ID", buscar_registro)
    btn_buscar.pack(pady=5)

    ventana.mainloop()

# --------------------------------------------------
#   Funciones de manejo de tablas
# --------------------------------------------------
tabla_actual = None

def seleccionar_tabla():
    global cursor, tabla_actual, tabla_var

    ventana = tk.Toplevel()
    ventana.title("Seleccionar tabla")
    ventana.overrideredirect(True)
    ventana.configure(bg="#202020")
    ventana.resizable(False, False)

    # Asignar icono a la ventana de selección
    try:
        ventana.iconbitmap(resource_path("icono.ico"))
    except Exception:
        pass

    w, h = 300, 200
    sw = ventana.winfo_screenwidth()
    sh = ventana.winfo_screenheight()
    px = (sw // 2) - (w // 2)
    py = (sh // 2) - (h // 2)
    ventana.geometry(f"{w}x{h}+{px}+{py}")

    state = {"is_maximized": False, "previous_geometry": ventana.geometry()}

    title_bar = tk.Frame(ventana, bg="#181818", height=30)
    title_bar.pack(fill="x")

    lbl_t = tk.Label(
        title_bar,
        text="Seleccionar tabla",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold")
    )
    lbl_t.pack(side="left", padx=10, pady=4)

    btn_close = tk.Button(
        title_bar,
        text="✕",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_close(ventana)
    )
    btn_close.pack(side="right", padx=10, pady=4)

    btn_maximize = tk.Button(
        title_bar,
        text="▢",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_maximize_restore(ventana, state)
    )
    btn_maximize.pack(side="right", padx=10, pady=4)

    title_bar.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    title_bar.bind("<B1-Motion>", lambda e: on_move(ventana, e))
    lbl_t.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    lbl_t.bind("<B1-Motion>", lambda e: on_move(ventana, e))

    cont = tk.Frame(ventana, bg="#202020")
    cont.place(x=0, y=30, width=w, height=h - 30)

    if cursor:
        try:
            cursor.execute("SHOW TABLES")
            tablas = [t[0] for t in cursor.fetchall()]
            if tablas:
                seleccion = tk.StringVar(ventana)
                seleccion.set(tablas[0])
                lbl = tk.Label(
                    cont,
                    text="Tablas disponibles:",
                    bg="#202020",
                    fg="#FF00FF",
                    font=("Segoe UI", 11)
                )
                lbl.pack(pady=(20, 5))
                om = tk.OptionMenu(cont, seleccion, *tablas)
                om.config(
                    bg="#181818", fg="#FF00FF", font=("Segoe UI", 10),
                    bd=0, activebackground="#FF5555", activeforeground="#FFFFFF",
                    highlightthickness=0
                )
                om["menu"].config(
                    bg="#181818", fg="#FF00FF", font=("Segoe UI", 10),
                    bd=0, activebackground="#FF5555", activeforeground="#FFFFFF"
                )
                om.pack(pady=5)
                btn_sel = tk.Button(
                    cont,
                    text="Seleccionar",
                    bg="#181818",
                    fg="#FF00FF",
                    font=("Segoe UI", 11, "bold"),
                    bd=0,
                    activebackground="#FF5555",
                    activeforeground="#FFFFFF",
                    command=lambda: al_seleccionar_tabla(seleccion.get(), ventana)
                )
                btn_sel.pack(pady=15)
            else:
                lbl_no = tk.Label(
                    cont,
                    text="No hay tablas disponibles.",
                    bg="#202020",
                    fg="#FF00FF",
                    font=("Segoe UI", 11)
                )
                lbl_no.pack(pady=60)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron obtener las tablas:\n{err}")
    else:
        messagebox.showwarning("Sin conexión", "Aún no hay conexión a la base de datos.")

def al_seleccionar_tabla(nombre_tabla, ventana):
    global tabla_actual, tabla_var
    tabla_actual = nombre_tabla
    tabla_var.set(f"Tabla en uso: {tabla_actual}")
    ventana.destroy()

def ver_registros():
    global cursor, tabla_actual

    if not tabla_actual:
        messagebox.showwarning("Sin tabla seleccionada", "Seleccione una tabla primero.")
        return

    ventana = tk.Toplevel()
    ventana.title(f"Valores de {tabla_actual}")
    ventana.overrideredirect(True)
    ventana.configure(bg="#202020")
    ventana.resizable(True, True)

    # Asignar icono a la ventana de ver registros
    try:
        ventana.iconbitmap(resource_path("icono.ico"))
    except Exception:
        pass

    w, h = 700, 500
    sw = ventana.winfo_screenwidth()
    sh = ventana.winfo_screenheight()
    px = (sw // 2) - (w // 2)
    py = (sh // 2) - (h // 2)
    ventana.geometry(f"{w}x{h}+{px}+{py}")

    state = {"is_maximized": False, "previous_geometry": ventana.geometry()}

    title_bar = tk.Frame(ventana, bg="#181818", height=30)
    title_bar.pack(fill="x")

    lbl_t = tk.Label(
        title_bar,
        text=f"Valores de {tabla_actual}",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold")
    )
    lbl_t.pack(side="left", padx=10, pady=4)

    btn_close = tk.Button(
        title_bar,
        text="✕",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_close(ventana)
    )
    btn_close.pack(side="right", padx=10, pady=4)

    btn_maximize = tk.Button(
        title_bar,
        text="▢",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_maximize_restore(ventana, state)
    )
    btn_maximize.pack(side="right", padx=10, pady=4)

    title_bar.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    title_bar.bind("<B1-Motion>", lambda e: on_move(ventana, e))
    lbl_t.bind("<ButtonPress-1>", lambda e: start_move(ventana, e))
    lbl_t.bind("<B1-Motion>", lambda e: on_move(ventana, e))

    cont = tk.Frame(ventana, bg="#202020")
    cont.place(x=0, y=30, width=w, height=h - 30)

    try:
        cursor.execute(f"SELECT * FROM {tabla_actual}")
        filas = cursor.fetchall()
        columnas = [d[0] for d in cursor.description]
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo obtener datos:\n{err}")
        ventana.destroy()
        return

    # Mapa de FKs
    fk_map = {}
    for col in columnas:
        cursor.execute(
            """
            SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA=DATABASE()
              AND TABLE_NAME=%s
              AND COLUMN_NAME=%s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """,
            (tabla_actual, col)
        )
        ref = cursor.fetchone()
        if ref:
            fk_map[col] = ref

    tbl = ttk.Treeview(cont, columns=columnas, show='headings')
    for c in columnas:
        tbl.heading(c, text=c)
        tbl.column(c, width=100, anchor='center')
    for row in filas:
        tbl.insert('', 'end', values=row)
    tbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_doble_click(event):
        item = tbl.identify_row(event.y)
        col_id = tbl.identify_column(event.x)
        if not item or not col_id:
            return
        idx = int(col_id.replace('#','')) - 1
        col_name = columnas[idx]
        if col_name in fk_map:
            val = tbl.set(item, col_name)
            ref_tab, ref_col = fk_map[col_name]
            try:
                cursor.execute(f"SELECT * FROM {ref_tab} WHERE {ref_col}=%s", (val,))
                rows = cursor.fetchall()
                cols_ref = [d[0] for d in cursor.description]
                v2 = tk.Toplevel()
                v2.title(f"Referencia {col_name} → {ref_tab}")
                v2.configure(bg="#202020")
                # Asignar icono a la ventana secundaria de referencia
                try:
                    v2.iconbitmap(resource_path("icono.ico"))
                except Exception:
                    pass

                txt = tk.Text(v2, bg="#181818", fg="white", font=("Segoe UI", 10))
                txt.pack(fill=tk.BOTH, expand=True)
                txt.insert(tk.END, "\t".join(cols_ref)+"\n")
                txt.insert(tk.END, "-"*50+"\n")
                for r in rows:
                    txt.insert(tk.END, "\t".join(str(x) for x in r)+"\n")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo obtener referencia:\n{err}")

    tbl.bind("<Double-1>", on_doble_click)

def agregar_registro():
    global cursor, tabla_actual, conexion

    if not tabla_actual:
        messagebox.showwarning("Sin tabla seleccionada", "Seleccione una tabla primero.")
        return
    try:
        cursor.execute(f"DESCRIBE {tabla_actual}")
        estructura = cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo obtener estructura:\n{err}")
        return

    # Detectar FKs
    fks = {}
    for col_def in estructura:
        col_name = col_def[0]
        cursor.execute(
            """
            SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA=DATABASE()
              AND TABLE_NAME=%s
              AND COLUMN_NAME=%s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """,
            (tabla_actual, col_name)
        )
        ref = cursor.fetchone()
        if ref:
            ref_table, ref_col = ref
            cursor.execute(f"DESCRIBE {ref_table}")
            cols_ref = [r[0] for r in cursor.fetchall()]
            display_col = cols_ref[1] if len(cols_ref) > 1 else ref_col
            cursor.execute(f"SELECT {ref_col}, {display_col} FROM {ref_table}")
            fks[col_name] = {'table': ref_table, 'pk': ref_col, 'disp': display_col, 'vals': cursor.fetchall()}

    form = tk.Toplevel()
    form.title(f"Agregar registro a {tabla_actual}")
    form.overrideredirect(True)
    form.configure(bg="#202020")
    form.resizable(False, False)

    # Asignar icono a la ventana de agregar registro
    try:
        form.iconbitmap(resource_path("icono.ico"))
    except Exception:
        pass

    w, h = 400, 400
    sw = form.winfo_screenwidth()
    sh = form.winfo_screenheight()
    px = (sw // 2) - (w // 2)
    py = (sh // 2) - (h // 2)
    form.geometry(f"{w}x{h}+{px}+{py}")

    state = {"is_maximized": False, "previous_geometry": form.geometry()}

    title_bar = tk.Frame(form, bg="#181818", height=30)
    title_bar.pack(fill="x")

    lbl_t = tk.Label(
        title_bar,
        text=f"Agregar registro a {tabla_actual}",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold")
    )
    lbl_t.pack(side="left", padx=10, pady=4)

    btn_close = tk.Button(
        title_bar,
        text="✕",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_close(form)
    )
    btn_close.pack(side="right", padx=10, pady=4)

    btn_maximize = tk.Button(
        title_bar,
        text="▢",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_maximize_restore(form, state)
    )
    btn_maximize.pack(side="right", padx=10, pady=4)

    title_bar.bind("<ButtonPress-1>", lambda e: start_move(form, e))
    title_bar.bind("<B1-Motion>", lambda e: on_move(form, e))
    lbl_t.bind("<ButtonPress-1>", lambda e: start_move(form, e))
    lbl_t.bind("<B1-Motion>", lambda e: on_move(form, e))

    cols = [c[0] for c in estructura][1:]
    types = [c[1] for c in estructura][1:]
    widgets = {}

    # Definimos espaciado vertical de 30px
    thirty = 30

    for i, (col, tp) in enumerate(zip(cols, types)):
        lbl = tk.Label(form, text=f"{col}:", bg="#202020", fg="#FF00FF", font=("Segoe UI", 10))
        lbl.place(x=10, y=40 + i * thirty)

        if col in fks:
            opcion = tk.StringVar(form)
            datos = fks[col]['vals']
            map_disp = {str(d[1]): d[0] for d in datos}
            lista_disp = list(map_disp.keys())
            opcion.set(lista_disp[0] if lista_disp else '')
            om = tk.OptionMenu(form, opcion, *lista_disp)
            om.config(
                bg="#181818", fg="#FF00FF", font=("Segoe UI", 10),
                bd=0, activebackground="#FF5555", activeforeground="#FFFFFF",
                highlightthickness=0
            )
            om["menu"].config(
                bg="#181818", fg="#FF00FF", font=("Segoe UI", 10),
                bd=0, activebackground="#FF5555", activeforeground="#FFFFFF"
            )
            om.place(x=150, y=40 + i * thirty)
            widgets[col] = ('fk', opcion, map_disp)

        elif 'date' in tp.lower():
            frame = tk.Frame(form, bg="#202020")
            frame.place(x=150, y=40 + i * thirty)

            tk.Label(frame, text="Año:", bg="#202020", fg="#FF00FF", font=("Segoe UI", 10)).pack(side='left')
            y = tk.Spinbox(frame, from_=1900, to=2100, width=5)
            y.pack(side='left', padx=(0,10))

            tk.Label(frame, text="Mes:", bg="#202020", fg="#FF00FF", font=("Segoe UI", 10)).pack(side='left')
            m = tk.Spinbox(frame, from_=1, to=12, width=3)
            m.pack(side='left', padx=(0,10))

            tk.Label(frame, text="Día:", bg="#202020", fg="#FF00FF", font=("Segoe UI", 10)).pack(side='left')
            d = tk.Spinbox(frame, from_=1, to=31, width=3)
            d.pack(side='left')

            widgets[col] = ('date', y, m, d)

        else:
            e = tk.Entry(form, bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0)
            e.place(x=150, y=40 + i * thirty)
            widgets[col] = ('text', e)

    def guardar():
        vals = []
        for col in cols:
            w = widgets[col]
            if w[0] == 'fk':
                disp_sel = w[1].get()
                pk_val = w[2][disp_sel]
                vals.append(pk_val)
            elif w[0] == 'date':
                yy, mm, dd = w[1].get(), w[2].get().zfill(2), w[3].get().zfill(2)
                vals.append(f"{yy}-{mm}-{dd}")
            else:
                vals.append(w[1].get().strip())
        placeholders = ', '.join(['%s'] * len(vals))
        try:
            cursor.execute(
                f"INSERT INTO {tabla_actual} ({', '.join(cols)}) VALUES ({placeholders})",
                tuple(vals)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Registro agregado correctamente.")
            form.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo agregar:\n{err}")

    btn_guardar = tk.Button(
        form,
        text="Guardar",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=guardar,
        padx=10,
        pady=6
    )
    btn_guardar.place(x=150, y=40 + len(cols) * thirty + 10)

def eliminar_registro():
    global cursor, tabla_actual, conexion

    if not tabla_actual:
        messagebox.showwarning("Sin tabla seleccionada", "Seleccione una tabla primero.")
        return

    try:
        cursor.execute(f"DESCRIBE {tabla_actual}")
        estr = cursor.fetchall()
        id_col = estr[0][0]
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo obtener estructura:\n{err}")
        return

    try:
        cursor.execute(f"SELECT * FROM {tabla_actual}")
        filas = cursor.fetchall()
        columnas = [d[0] for d in cursor.description]
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo obtener registros:\n{err}")
        return

    win = tk.Toplevel()
    win.title(f"Eliminar registros de {tabla_actual}")
    win.overrideredirect(True)
    win.configure(bg="#202020")
    win.resizable(True, True)

    # Asignar icono a la ventana de eliminar registros
    try:
        win.iconbitmap(resource_path("icono.ico"))
    except Exception:
        pass

    w, h = 700, 500
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    px = (sw // 2) - (w // 2)
    py = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{px}+{py}")

    state = {"is_maximized": False, "previous_geometry": win.geometry()}

    title_bar = tk.Frame(win, bg="#181818", height=30)
    title_bar.pack(fill="x")

    lbl_t = tk.Label(
        title_bar,
        text=f"Eliminar registros de {tabla_actual}",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold")
    )
    lbl_t.pack(side="left", padx=10, pady=4)

    btn_close = tk.Button(
        title_bar,
        text="✕",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_close(win)
    )
    btn_close.pack(side="right", padx=10, pady=4)

    btn_maximize = tk.Button(
        title_bar,
        text="▢",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=lambda: on_maximize_restore(win, state)
    )
    btn_maximize.pack(side="right", padx=10, pady=4)

    title_bar.bind("<ButtonPress-1>", lambda e: start_move(win, e))
    title_bar.bind("<B1-Motion>", lambda e: on_move(win, e))
    lbl_t.bind("<ButtonPress-1>", lambda e: start_move(win, e))
    lbl_t.bind("<B1-Motion>", lambda e: on_move(win, e))

    tbl = ttk.Treeview(win, columns=columnas, show='headings')
    for c in columnas:
        tbl.heading(c, text=c)
        tbl.column(c, width=100, anchor='center')
    for row in filas:
        tbl.insert('', 'end', values=row)
    tbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=(40, 10))

    def eliminar_seleccionado():
        sel = tbl.selection()
        if not sel:
            messagebox.showwarning("Aviso", "No ha seleccionado ningún registro.")
            return
        val = tbl.item(sel[0])['values'][columnas.index(id_col)]
        if messagebox.askyesno("Confirmar", f"¿Eliminar registro con {id_col}={val}?"):
            try:
                cursor.execute(f"DELETE FROM {tabla_actual} WHERE {id_col}=%s", (val,))
                conexion.commit()
                messagebox.showinfo("Éxito", "Registro eliminado.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo eliminar:{err}")

    btn_sel = tk.Button(
        win,
        text="Eliminar seleccionado",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=eliminar_seleccionado,
        padx=15,
        pady=6
    )
    btn_sel.place(x=10, y=10)

    frame = tk.Frame(win, bg="#202020")
    frame.place(x=200, y=10)

    tk.Label(frame, text=f"ID columna: {id_col}", bg="#202020", fg="#FF00FF", font=("Segoe UI", 11)).pack(side='left', padx=5)
    entrada_id = tk.Entry(frame, bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0, width=8)
    entrada_id.pack(side='left', padx=5)

    def eliminar_por_id():
        val = entrada_id.get().strip()
        if not val:
            messagebox.showwarning("Aviso", "Ingrese un ID válido.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar registro con {id_col}={val}?"):
            try:
                cursor.execute(f"DELETE FROM {tabla_actual} WHERE {id_col}=%s", (val,))
                conexion.commit()
                messagebox.showinfo("Éxito", "Registro eliminado.")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo eliminar:{err}")

    btn_id = tk.Button(
        frame,
        text="Eliminar por ID",
        bg="#181818",
        fg="#FF00FF",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        activebackground="#FF5555",
        activeforeground="#FFFFFF",
        command=eliminar_por_id,
        padx=10,
        pady=5
    )
    btn_id.pack(side='left', padx=5)

def buscar_registro():
    global cursor, tabla_actual

    if not tabla_actual:
        messagebox.showwarning("Sin tabla seleccionada", "Seleccione una tabla primero.")
        return
    try:
        cursor.execute(f"DESCRIBE {tabla_actual}")
        estructura = cursor.fetchall()
        id_col = estructura[0][0]
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"No se pudo obtener estructura:{err}")
        return
    valor = simpledialog.askstring("Buscar registro", f"Ingrese valor de {id_col}:")
    if valor:
        try:
            cursor.execute(f"SELECT * FROM {tabla_actual} WHERE {id_col}=%s", (valor,))
            fila = cursor.fetchone()
            if fila:
                cols = [d[0] for d in cursor.description]
                v = tk.Toplevel()
                v.title(f"Registro {id_col}={valor}")
                v.configure(bg="#202020")
                # Asignar icono a la ventana de resultado de búsqueda
                try:
                    v.iconbitmap(resource_path("icono.ico"))
                except Exception:
                    pass

                txt = tk.Text(v, bg="#181818", fg="white", font=("Segoe UI", 10))
                txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                txt.insert(tk.END, "\t".join(cols)+"\n")
                txt.insert(tk.END, "-"*50+"\n")
                txt.insert(tk.END, "\t".join(str(x) for x in fila))
            else:
                messagebox.showinfo("No encontrado", f"No existe registro con {id_col}={valor}")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo buscar:{err}")

# ----- Ventana de conexión inicial con estilo Yuuruii tweaks -----
ventana_login = tk.Tk()
ventana_login.title("Yuuruii's Db Manager - Conexión")
ventana_login.overrideredirect(True)
ventana_login.configure(bg="#202020")
ventana_login.resizable(False, False)

# Asignar icono a la ventana de login
try:
    ventana_login.iconbitmap(resource_path("icono.ico"))
except Exception:
    pass

w_login, h_login = 350, 220
sw, sh = ventana_login.winfo_screenwidth(), ventana_login.winfo_screenheight()
px_login = (sw // 2) - (w_login // 2)
py_login = (sh // 2) - (h_login // 2)
ventana_login.geometry(f"{w_login}x{h_login}+{px_login}+{py_login}")

state_login = {"is_maximized": False, "previous_geometry": ventana_login.geometry()}

title_bar = tk.Frame(ventana_login, bg="#181818", height=30)
title_bar.pack(fill="x")

lbl_tl = tk.Label(
    title_bar,
    text="Yuuruii's Db Manager - Conexión",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 11, "bold")
)
lbl_tl.pack(side="left", padx=10, pady=4)

btn_close = tk.Button(
    title_bar,
    text="✕",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 11, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=lambda: on_close(ventana_login)
)
btn_close.pack(side="right", padx=10, pady=4)

btn_maximize = tk.Button(
    title_bar,
    text="▢",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 11, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=lambda: on_maximize_restore(ventana_login, state_login)
)
btn_maximize.pack(side="right", padx=10, pady=4)

title_bar.bind("<ButtonPress-1>", lambda e: start_move(ventana_login, e))
title_bar.bind("<B1-Motion>", lambda e: on_move(ventana_login, e))
lbl_tl.bind("<ButtonPress-1>", lambda e: start_move(ventana_login, e))
lbl_tl.bind("<B1-Motion>", lambda e: on_move(ventana_login, e))

container_login = tk.Frame(ventana_login, bg="#202020")
container_login.place(x=0, y=30, width=w_login, height=h_login-30)

lbl_host = tk.Label(
    container_login,
    text="Host:",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10)
)
lbl_host.grid(row=0, column=0, padx=5, pady=5, sticky='e')
entrada_host = tk.Entry(container_login, bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0)
entrada_host.grid(row=0, column=1, padx=5, pady=5)

lbl_user = tk.Label(
    container_login,
    text="Usuario:",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10)
)
lbl_user.grid(row=1, column=0, padx=5, pady=5, sticky='e')
entrada_usuario = tk.Entry(container_login, bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0)
entrada_usuario.grid(row=1, column=1, padx=5, pady=5)

lbl_pass = tk.Label(
    container_login,
    text="Contraseña:",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10)
)
lbl_pass.grid(row=2, column=0, padx=5, pady=5, sticky='e')
entrada_contraseña = tk.Entry(container_login, show="*", bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0)
entrada_contraseña.grid(row=2, column=1, padx=5, pady=5)

lbl_bd = tk.Label(
    container_login,
    text="Base de datos:",
    bg="#202020",
    fg="#FF00FF",
    font=("Segoe UI", 10)
)
lbl_bd.grid(row=3, column=0, padx=5, pady=5, sticky='e')
entrada_base_datos = tk.Entry(container_login, bg="#181818", fg="white", insertbackground="white", font=("Segoe UI", 10), bd=0)
entrada_base_datos.grid(row=3, column=1, padx=5, pady=5)

btn_conectar = tk.Button(
    container_login,
    text="Conectar",
    bg="#181818",
    fg="#FF00FF",
    font=("Segoe UI", 11, "bold"),
    bd=0,
    activebackground="#FF5555",
    activeforeground="#FFFFFF",
    command=conectar_bd,
    padx=15,
    pady=6
)
btn_conectar.grid(row=4, column=0, columnspan=2, pady=10)

ventana_login.mainloop()
