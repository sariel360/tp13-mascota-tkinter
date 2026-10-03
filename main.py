"""
TP N° 13 - Laboratorio de Aplicaciones II - 6° G
IPET N° 249 "Nicolás Copérnico"

Opción 4: Mascota Virtual (Tamagotchi)

Indicadores (0 a 100):
    Hambre    -> sube con el tiempo        (peligro si llega a 100, es decir, saciedad 0)
    Energía   -> baja con el tiempo        (Game Over si llega a 0)
    Felicidad -> baja con el tiempo        (Game Over si llega a 0)

Acciones: Alimentar, Jugar, Dormir. El tiempo avanza con after() cada 3 segundos.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------------
# CONSTANTES
# ----------------------------------------------------------------------------
ANCHO, ALTO = 800, 600          # Tamaño obligatorio de la ventana
INTERVALO_MS = 3000             # after(): actualización de métricas cada 3 s
NOMBRE_MAX = 12                 # Largo máximo del nombre de la mascota
VALOR_INICIAL = 50              # Valor de cada indicador al iniciar/reiniciar
UMBRAL_PELIGRO = 25             # Zona crítica (<= 25, o >= 75 para el hambre)

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_EMBLEMA = os.path.join(RUTA_BASE, "assets", "emblema.png")

# Paleta institucional (tomada del escudo del IPET 249)
COLOR_FONDO = "#FFFF7B"         # Amarillo del escudo: fondo de la ventana
COLOR_PANEL = "#FFFDE0"         # Amarillo muy claro: paneles y mascota
COLOR_ACENTO = "#FB7D7C"        # Coral de los engranajes: botones y detalles
COLOR_ACENTO_HOVER = "#FFA09F"  # Coral claro: botón bajo el cursor
COLOR_SUBTITULO = "#B53A39"     # Coral oscuro: subtítulo legible sobre el amarillo
COLOR_TEXTO = "#2B2B1A"         # Casi negro (letras del escudo): títulos
COLOR_TEXTO_OSCURO = "#2B2B1A"  # Texto sobre paneles claros y botones coral
COLOR_BOTON_OSCURO = "#2B2B1A"  # Fondo del botón Reiniciar
COLOR_OK = "#505028"            # Indicador en rango normal
COLOR_PELIGRO = "#C62828"       # Indicador en zona crítica

# Estado del juego (un único diccionario para no dispersar variables globales)
estado = {
    "nombre": "Copi",
    "hambre": VALOR_INICIAL,
    "energia": VALOR_INICIAL,
    "felicidad": VALOR_INICIAL,
    "ticks": 0,          # Cantidad de ciclos de 3 s vividos
    "vivo": True,
    "job": None,         # Id devuelto por after(), necesario para cancelarlo
    "mensaje": "¡Cuidá a tu mascota!",
}

# Referencias a los widgets que se actualizan durante el juego
W = {}

# Indicadores: (texto visible, clave en `estado`)
INDICADORES = [("Hambre", "hambre"), ("Energía", "energia"), ("Felicidad", "felicidad")]


# ----------------------------------------------------------------------------
# LÓGICA DEL JUEGO
# ----------------------------------------------------------------------------
def limitar(valor):
    """Mantiene un indicador dentro del rango 0-100."""
    return max(0, min(100, valor))


def en_peligro(clave):
    """Indica si un indicador está en zona crítica (el hambre es inversa)."""
    if clave == "hambre":
        return estado["hambre"] >= 100 - UMBRAL_PELIGRO
    return estado[clave] <= UMBRAL_PELIGRO


def estado_animo():
    """Devuelve (clave, descripción) según el estado actual de la mascota."""
    if not estado["vivo"]:
        return "muerta", "Tu mascota ya no puede más..."
    if estado["hambre"] >= 100 - UMBRAL_PELIGRO:
        return "hambrienta", "Tiene muchísima hambre"
    if estado["energia"] <= UMBRAL_PELIGRO:
        return "cansada", "Está agotada, necesita dormir"
    if estado["felicidad"] <= UMBRAL_PELIGRO:
        return "triste", "Está triste, quiere jugar"
    return "feliz", "Se siente muy bien"


def mostrar_mensaje(texto):
    """Guarda y muestra el mensaje inferior."""
    estado["mensaje"] = texto
    W["lbl_mensaje"].config(text=texto)


def verificar_fin():
    """Si algún indicador llegó al límite, termina la partida. Devuelve True/False."""
    if estado["hambre"] >= 100 or estado["energia"] <= 0 or estado["felicidad"] <= 0:
        game_over()
        return True
    return False


def aplicar_accion(d_hambre, d_energia, d_felicidad, mensaje):
    """Modifica los indicadores, valida el fin de partida y refresca la pantalla."""
    if not estado["vivo"]:
        return
    estado["hambre"] = limitar(estado["hambre"] + d_hambre)
    estado["energia"] = limitar(estado["energia"] + d_energia)
    estado["felicidad"] = limitar(estado["felicidad"] + d_felicidad)
    if verificar_fin():
        return
    actualizar_interfaz()
    mostrar_mensaje(mensaje)


def alimentar(evento=None):
    """Alimentar: reduce Hambre y disminuye levemente Energía."""
    aplicar_accion(-25, -5, 0, f"{estado['nombre']} comió. ¡Ñam!")


def jugar(evento=None):
    """Jugar: incrementa Felicidad y reduce Energía."""
    aplicar_accion(0, -10, +20, f"{estado['nombre']} se divirtió jugando.")


def dormir(evento=None):
    """Dormir: recupera Energía, incrementa Hambre y reduce Felicidad."""
    aplicar_accion(+10, +30, -10, f"{estado['nombre']} durmió una siesta. Zzz...")


def tick():
    """Paso del tiempo: Hambre sube, Energía y Felicidad bajan (cada 3 s)."""
    if not estado["vivo"]:
        return
    estado["hambre"] = limitar(estado["hambre"] + 4)
    estado["energia"] = limitar(estado["energia"] - 3)
    estado["felicidad"] = limitar(estado["felicidad"] - 3)
    estado["ticks"] += 1
    if verificar_fin():
        return
    actualizar_interfaz()
    # Se vuelve a programar a sí misma: así funciona el "bucle" con after()
    estado["job"] = W["root"].after(INTERVALO_MS, tick)


def cancelar_tick():
    """Cancela el after() pendiente para no duplicar ciclos al reiniciar."""
    if estado["job"] is not None:
        W["root"].after_cancel(estado["job"])
        estado["job"] = None


def game_over():
    """Pantalla de fin de juego: bloquea las acciones y habilita el reinicio."""
    estado["vivo"] = False
    cancelar_tick()
    actualizar_interfaz()
    mostrar_mensaje("GAME OVER - Presioná «Reiniciar Mascota»")


def reiniciar():
    """Reinicia todos los indicadores a 50 puntos y reanuda el tiempo."""
    cancelar_tick()
    for _, clave in INDICADORES:
        estado[clave] = VALOR_INICIAL
    estado["ticks"] = 0
    estado["vivo"] = True
    actualizar_interfaz()
    mostrar_mensaje(f"¡{estado['nombre']} volvió a la vida!")
    estado["job"] = W["root"].after(INTERVALO_MS, tick)


# ----------------------------------------------------------------------------
# VALIDACIÓN DE DATOS (manejo de excepciones)
# ----------------------------------------------------------------------------
def validar_nombre(texto):
    """Valida el nombre ingresado. Lanza ValueError si es incorrecto."""
    nombre = texto.strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    if len(nombre) > NOMBRE_MAX:
        raise ValueError(f"El nombre admite hasta {NOMBRE_MAX} caracteres.")
    if nombre.isdigit():
        raise ValueError("El nombre debe tener letras, no solo números.")
    return nombre


def confirmar_nombre(evento=None):
    """Evento <Return> / botón Guardar: asigna el nombre a la mascota."""
    try:
        estado["nombre"] = validar_nombre(W["entry_nombre"].get())
    except ValueError as error:
        messagebox.showwarning("Nombre inválido", str(error))
        W["entry_nombre"].focus_set()
        return
    actualizar_interfaz()
    mostrar_mensaje(f"¡Hola, {estado['nombre']}!")
    W["root"].focus_set()   # Devuelve el foco a la ventana (atajos F1-F3)


# ----------------------------------------------------------------------------
# EVENTOS DE INTERFAZ
# ----------------------------------------------------------------------------
def al_entrar_boton(evento, ayuda):
    """Evento <Enter>: resalta el botón y muestra una ayuda contextual."""
    boton = evento.widget
    if str(boton["state"]) == "normal":
        boton.config(bg=COLOR_ACENTO_HOVER)
        W["lbl_mensaje"].config(text=ayuda)


def al_salir_boton(evento):
    """Evento <Leave>: restaura el color y el mensaje anterior."""
    evento.widget.config(bg=COLOR_ACENTO)
    W["lbl_mensaje"].config(text=estado["mensaje"])


def al_cerrar():
    """Evento de ventana WM_DELETE_WINDOW: confirma antes de salir."""
    if messagebox.askokcancel("Salir", "¿Querés cerrar la Mascota Virtual?"):
        cancelar_tick()
        W["root"].destroy()


# ----------------------------------------------------------------------------
# DIBUJO DE LA MASCOTA
# ----------------------------------------------------------------------------
def dibujar_mascota(animo):
    """Dibuja la mascota en el Canvas según su estado de ánimo."""
    c = W["canvas"]
    c.delete("all")
    colores = {
        "feliz": "#7BD389", "hambrienta": "#F2B705", "cansada": "#9BA8C9",
        "triste": "#7FB3E6", "muerta": "#B0B0B0",
    }
    # Orejas y cuerpo
    c.create_oval(55, 20, 115, 80, fill=colores[animo], outline=COLOR_TEXTO_OSCURO, width=3)
    c.create_oval(185, 20, 245, 80, fill=colores[animo], outline=COLOR_TEXTO_OSCURO, width=3)
    c.create_oval(40, 45, 260, 225, fill=colores[animo], outline=COLOR_TEXTO_OSCURO, width=4)

    # Ojos
    if animo == "muerta":
        for x in (110, 190):
            c.create_line(x - 12, 98, x + 12, 122, width=4, fill=COLOR_TEXTO_OSCURO)
            c.create_line(x - 12, 122, x + 12, 98, width=4, fill=COLOR_TEXTO_OSCURO)
    elif animo == "cansada":
        for x in (110, 190):
            c.create_line(x - 14, 112, x + 14, 112, width=5, fill=COLOR_TEXTO_OSCURO)
    else:
        for x in (110, 190):
            c.create_oval(x - 12, 98, x + 12, 126, fill=COLOR_TEXTO_OSCURO)
            c.create_oval(x - 5, 102, x + 1, 108, fill="white", outline="white")

    # Boca
    if animo == "feliz":
        c.create_arc(105, 130, 195, 195, start=200, extent=140, style=tk.ARC,
                     width=4, outline=COLOR_TEXTO_OSCURO)
    elif animo == "triste":
        c.create_arc(105, 165, 195, 215, start=20, extent=140, style=tk.ARC,
                     width=4, outline=COLOR_TEXTO_OSCURO)
    elif animo == "hambrienta":
        c.create_oval(135, 155, 165, 190, fill="#7A2E2E", outline=COLOR_TEXTO_OSCURO, width=3)
    else:
        c.create_line(125, 170, 175, 170, width=4, fill=COLOR_TEXTO_OSCURO)

    if animo == "cansada":
        c.create_text(255, 45, text="z Z", font=("Helvetica", 22, "bold"), fill=COLOR_TEXTO_OSCURO)
    if animo == "muerta":
        c.create_text(150, 245, text="GAME OVER", font=("Helvetica", 18, "bold"),
                      fill=COLOR_PELIGRO)

    c.move("all", -15, 0)   # Centra el dibujo (pensado para 300 px) en el Canvas de 270 px


def actualizar_interfaz():
    """Sincroniza barras, etiquetas, botones y dibujo con el estado actual."""
    for _, clave in INDICADORES:
        W[f"pb_{clave}"]["value"] = estado[clave]
        W[f"pb_{clave}"].config(
            style="Peligro.Horizontal.TProgressbar" if en_peligro(clave)
            else "Ok.Horizontal.TProgressbar")
        W[f"pct_{clave}"].config(text=f"{estado[clave]}%")

    animo, descripcion = estado_animo()
    segundos = estado["ticks"] * INTERVALO_MS // 1000
    W["lbl_nombre"].config(text=estado["nombre"])
    W["lbl_estado"].config(text=descripcion)
    W["lbl_edad"].config(text=f"Tiempo de vida: {segundos // 60:02d}:{segundos % 60:02d}")
    dibujar_mascota(animo)

    # Acciones bloqueadas si terminó el juego; reinicio habilitado solo entonces
    modo_accion = tk.NORMAL if estado["vivo"] else tk.DISABLED
    for nombre in ("btn_alimentar", "btn_jugar", "btn_dormir"):
        W[nombre].config(state=modo_accion)
    W["btn_reiniciar"].config(state=tk.DISABLED if estado["vivo"] else tk.NORMAL)


# ----------------------------------------------------------------------------
# CONSTRUCCIÓN DE LA INTERFAZ
# ----------------------------------------------------------------------------
def cargar_emblema():
    """Carga el emblema del colegio (.png). Devuelve None si no se puede leer."""
    try:
        imagen = tk.PhotoImage(file=RUTA_EMBLEMA)
        factor = max(1, imagen.width() // 64)      # Se reduce a ~64 px de ancho
        return imagen.subsample(factor, factor)
    except tk.TclError:
        return None


def crear_estilos():
    """Define los estilos ttk (barras de progreso y botón Guardar)."""
    estilo = ttk.Style()
    estilo.theme_use("clam")   # 'clam' permite personalizar colores en todos los SO
    for nombre, color in (("Ok", COLOR_OK), ("Peligro", COLOR_PELIGRO)):
        estilo.configure(f"{nombre}.Horizontal.TProgressbar", troughcolor="#DADADA",
                         background=color, bordercolor=COLOR_TEXTO_OSCURO,
                         lightcolor=color, darkcolor=color, thickness=20)
    estilo.configure("Guardar.TButton", font=("Helvetica", 10, "bold"),
                     background=COLOR_ACENTO, foreground=COLOR_TEXTO_OSCURO)
    estilo.map("Guardar.TButton", background=[("active", COLOR_ACENTO_HOVER)])


def crear_boton_accion(padre, texto, comando, ayuda, columna):
    """Crea un botón de acción con eventos <Enter>/<Leave> y lo ubica con grid()."""
    boton = tk.Button(padre, text=texto, command=comando, width=10, bg=COLOR_ACENTO,
                      fg=COLOR_TEXTO_OSCURO, activebackground=COLOR_ACENTO_HOVER,
                      font=("Helvetica", 11, "bold"), relief=tk.FLAT, cursor="hand2",
                      disabledforeground="#7A7A7A")
    boton.grid(row=0, column=columna, padx=5, pady=5)
    boton.bind("<Enter>", lambda e: al_entrar_boton(e, ayuda))
    boton.bind("<Leave>", al_salir_boton)
    return boton


def construir_cabecera(root):
    """Cabecera con emblema y títulos (se apila con pack)."""
    cabecera = tk.Frame(root, bg=COLOR_FONDO)
    cabecera.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(10, 5))

    W["emblema"] = cargar_emblema()     # Se guarda la referencia: si no, Tk la borra
    if W["emblema"]:
        tk.Label(cabecera, image=W["emblema"], bg=COLOR_FONDO).pack(side=tk.LEFT)
    else:
        tk.Label(cabecera, text="IPET 249", bg=COLOR_FONDO, fg=COLOR_TEXTO,
                 font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)

    titulos = tk.Frame(cabecera, bg=COLOR_FONDO)
    titulos.pack(side=tk.LEFT, padx=15)
    tk.Label(titulos, text="IPET 249 - Mascota Virtual", bg=COLOR_FONDO, fg=COLOR_TEXTO,
             font=("Helvetica", 20, "bold")).pack(anchor="w")
    tk.Label(titulos, text="Laboratorio de Aplicaciones II - 6° G", bg=COLOR_FONDO,
             fg=COLOR_SUBTITULO, font=("Helvetica", 11, "bold")).pack(anchor="w")


def construir_zona_mascota(padre):
    """Panel izquierdo: dibujo de la mascota y sus datos (pack)."""
    marco = tk.Frame(padre, bg=COLOR_PANEL, bd=3, relief=tk.RIDGE)
    marco.grid(row=0, column=0, padx=(0, 10), sticky="n")

    W["canvas"] = tk.Canvas(marco, width=270, height=260, bg=COLOR_PANEL, highlightthickness=0)
    W["canvas"].pack(padx=10, pady=(10, 0))
    W["lbl_nombre"] = tk.Label(marco, bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
                               font=("Helvetica", 18, "bold"))
    W["lbl_nombre"].pack()
    W["lbl_estado"] = tk.Label(marco, bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
                               font=("Helvetica", 11))
    W["lbl_estado"].pack()
    W["lbl_edad"] = tk.Label(marco, bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
                             font=("Helvetica", 10))
    W["lbl_edad"].pack(pady=(0, 10))


def construir_zona_control(padre):
    """Panel derecho: nombre, indicadores y acciones (grid, celdas alineadas)."""
    marco = tk.Frame(padre, bg=COLOR_PANEL, bd=3, relief=tk.RIDGE)
    marco.grid(row=0, column=1, sticky="n")
    marco.columnconfigure(1, weight=1)

    # Fila 0: nombre de la mascota (Entry + botón ttk)
    tk.Label(marco, text="Nombre:", bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
             font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=8, pady=12, sticky="e")
    W["entry_nombre"] = tk.Entry(marco, font=("Helvetica", 12), width=12)
    W["entry_nombre"].insert(0, estado["nombre"])
    W["entry_nombre"].grid(row=0, column=1, pady=12, sticky="ew")
    W["entry_nombre"].bind("<Return>", confirmar_nombre)           # Evento de teclado
    ttk.Button(marco, text="Guardar", style="Guardar.TButton",
               command=confirmar_nombre).grid(row=0, column=2, padx=8, pady=12)

    ttk.Separator(marco, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=3,
                                                    sticky="ew", padx=8)

    # Filas 2-4: indicadores (etiqueta | barra ttk | porcentaje)
    for fila, (texto, clave) in enumerate(INDICADORES, start=2):
        tk.Label(marco, text=texto, bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
                 font=("Helvetica", 11, "bold")).grid(row=fila, column=0, padx=8,
                                                      pady=10, sticky="e")
        W[f"pb_{clave}"] = ttk.Progressbar(marco, orient=tk.HORIZONTAL, length=120,
                                           maximum=100, mode="determinate")
        W[f"pb_{clave}"].grid(row=fila, column=1, pady=10, sticky="ew")
        W[f"pct_{clave}"] = tk.Label(marco, width=5, bg=COLOR_PANEL, fg=COLOR_TEXTO_OSCURO,
                                     font=("Helvetica", 11))
        W[f"pct_{clave}"].grid(row=fila, column=2, padx=8)

    ttk.Separator(marco, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=3,
                                                    sticky="ew", padx=8, pady=(5, 0))

    # Fila 6: acciones (cada botón con su propia función)
    acciones = tk.Frame(marco, bg=COLOR_PANEL)
    acciones.grid(row=6, column=0, columnspan=3, pady=8)
    W["btn_alimentar"] = crear_boton_accion(
        acciones, "Alimentar", alimentar, "Alimentar: baja el hambre, gasta un poco de energía (F1)", 0)
    W["btn_jugar"] = crear_boton_accion(
        acciones, "Jugar", jugar, "Jugar: sube la felicidad, gasta energía (F2)", 1)
    W["btn_dormir"] = crear_boton_accion(
        acciones, "Dormir", dormir, "Dormir: recupera energía, da hambre y resta felicidad (F3)", 2)

    # Fila 7: reinicio (solo se habilita en Game Over)
    W["btn_reiniciar"] = tk.Button(marco, text="Reiniciar Mascota", command=reiniciar,
                                   bg=COLOR_BOTON_OSCURO, fg="white", font=("Helvetica", 11, "bold"),
                                   activebackground="#4A4A33", activeforeground="white",
                                   disabledforeground="#9A9A80", relief=tk.FLAT, width=22)
    W["btn_reiniciar"].grid(row=7, column=0, columnspan=3, pady=(0, 12))


def construir_interfaz(root):
    """
    Arma la ventana combinando los dos gestores de layout:
      - pack():  apila de arriba hacia abajo los bloques grandes (cabecera, cuerpo
                 y mensaje) y se adapta bien si cambia el alto de la ventana.
      - grid():  alinea en filas y columnas lo que es tabular (panel mascota |
                 panel de control, y etiqueta | barra | % de cada indicador).
    Nunca se mezclan en el mismo contenedor: cada Frame usa un solo gestor.
    """
    crear_estilos()
    construir_cabecera(root)                                    # pack

    cuerpo = tk.Frame(root, bg=COLOR_FONDO)                     # pack + grid interno
    cuerpo.pack(side=tk.TOP, expand=True, padx=15, pady=5)   # sin fill: queda centrado
    construir_zona_mascota(cuerpo)                              # grid
    construir_zona_control(cuerpo)                              # grid

    W["lbl_mensaje"] = tk.Label(root, bg=COLOR_ACENTO, fg=COLOR_TEXTO_OSCURO,
                                font=("Helvetica", 11, "bold"), pady=6)
    W["lbl_mensaje"].pack(side=tk.BOTTOM, fill=tk.X)            # pack


def main():
    """Crea la ventana principal, enlaza eventos globales e inicia el juego."""
    root = tk.Tk()
    W["root"] = root
    root.title("IPET 249 - Mascota Virtual | Lab. de Aplicaciones II")
    root.geometry(f"{ANCHO}x{ALTO}")
    root.resizable(False, False)
    root.configure(bg=COLOR_FONDO)

    construir_interfaz(root)

    # Eventos globales: atajos de teclado y cierre de ventana
    root.bind("<F1>", alimentar)
    root.bind("<F2>", jugar)
    root.bind("<F3>", dormir)
    root.protocol("WM_DELETE_WINDOW", al_cerrar)

    actualizar_interfaz()
    mostrar_mensaje(estado["mensaje"])
    estado["job"] = root.after(INTERVALO_MS, tick)
    root.mainloop()


if __name__ == "__main__":
    main()
