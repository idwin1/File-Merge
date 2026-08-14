import os
import sys
import subprocess
import json
import shutil
import fnmatch
import zipfile
from pathlib import Path

# Lista de librerías externas que requiere tu proyecto
LIBRERIAS_REQUERIDAS = {
    "colorama": "colorama",
    "tkinter": "tkinter"
}

def verificar_e_instalar_librerias():
    for import_name, pip_name in LIBRERIAS_REQUERIDAS.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[+] Instalando '{pip_name}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

verificar_e_instalar_librerias()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from colorama import init, Fore

init(autoreset=True)

CONFIG_FILE = "config.json"

# Estructuras por defecto que se guardarán en el JSON si no existen
ESTRUCTURA_POR_DEFECTO = {
    "Pruebas/Evidencias de Pruebas Coppel/Evidencias": ["EE_CP_*"],
    "Pruebas/Evidencias de Pruebas Coppel/Matriz casos prueba": ["MCP_*"],
    "Pruebas/Evidencias de Pruebas Coppel": ["MPH_*","SE_*","PP*","EncuestaAut*","EST*"],
    "Pruebas/Evidencias de pruebas Softtek": ["Reporte_pruebas*"]
}

ZIP_POR_DEFECTO = {
    "Pruebas.zip": [
        "Pruebas/Evidencias de Pruebas Coppel/Evidencias",
        "Pruebas/Evidencias de Pruebas Coppel/Matriz Casos Prueba"
    ]
}

def cargar_configuracion():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def guardar_configuracion(datos):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

class OrganizadorEstructura:

    def __init__(self, ventana_principal):
        self.root = ventana_principal
        self.root.title("Organizador de Estructura de Pruebas")
        self.root.geometry("750x500")
        self.root.resizable(False, False)
        
        # Paleta de colores oscura
        self.bg_color = "#121212"
        self.panel_color = "#1E1E1E"
        self.text_color = "#FFFFFF"
        self.btn_blue = "#5865F2"
        self.btn_orange = "#FF9800"
        self.btn_teal = "#00BCD4"
        
        self.root.configure(bg=self.bg_color)
        self.root.withdraw()

        # Configuración inicial
        self.datos_config = cargar_configuracion()
        
        cambios_en_config = False

        # Inyectar estructura de carpetas por defecto en el JSON si no existe
        if "Estructura_Archivos" not in self.datos_config:
            self.datos_config["Estructura_Archivos"] = ESTRUCTURA_POR_DEFECTO
            cambios_en_config = True
            
        # Inyectar configuración de ZIP por defecto en el JSON si no existe
        if "Configuracion_Zip" not in self.datos_config:
            self.datos_config["Configuracion_Zip"] = ZIP_POR_DEFECTO
            cambios_en_config = True

        if cambios_en_config:
            guardar_configuracion(self.datos_config)

        self.ruta_origen = self.datos_config.get("Ruta_Origen_Estructura", "")
        self.ruta_destino = self.datos_config.get("Ruta_Destino_Estructura", "")

        self.root.deiconify()
        self.construir_interfaz()

    def construir_interfaz(self):
        # Header
        frame_header = tk.Frame(self.root, bg=self.bg_color)
        frame_header.pack(fill="x", pady=15, padx=20)
        
        tk.Label(
            frame_header, text="🗂️ Estructurador de Archivos y ZIP", 
            font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.text_color
        ).pack(side="left")

        # Acciones
        frame_acciones = tk.Frame(self.root, bg=self.panel_color, padx=10, pady=10)
        frame_acciones.pack(fill="x", padx=20)

        btn_opts = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "padx": 10, "pady": 5, "cursor": "hand2"}

        tk.Button(frame_acciones, text="📂 Carpeta Origen", bg=self.btn_blue, command=self.cambiar_origen, **btn_opts).pack(side="left", padx=5)
        tk.Button(frame_acciones, text="📁 Carpeta Destino", bg=self.btn_orange, command=self.cambiar_destino, **btn_opts).pack(side="left", padx=5)
        tk.Button(frame_acciones, text="⚡ Organizar y Zipear", bg=self.btn_teal, command=self.organizar_archivos, **btn_opts).pack(side="right", padx=5)

        # Panel de Rutas
        frame_rutas = tk.Frame(self.root, bg=self.panel_color, padx=20, pady=20)
        frame_rutas.pack(fill="both", expand=True, padx=20, pady=20)

        texto_origen = self.ruta_origen if self.ruta_origen else "No seleccionada"
        self.lbl_origen = tk.Label(frame_rutas, text=f"Origen: {texto_origen}", font=("Segoe UI", 9), bg=self.panel_color, fg="#AAAAAA", wraplength=550, justify="left")
        self.lbl_origen.pack(anchor="w", pady=(0, 15))

        texto_destino = self.ruta_destino if self.ruta_destino else "No seleccionada"
        self.lbl_destino = tk.Label(frame_rutas, text=f"Destino: {texto_destino}", font=("Segoe UI", 9), bg=self.panel_color, fg="#FFB74D", wraplength=550, justify="left")
        self.lbl_destino.pack(anchor="w", pady=(0, 15))

        self.lbl_estado = tk.Label(frame_rutas, text="Listo para procesar.", font=("Segoe UI", 10, "bold"), bg=self.panel_color, fg="white", justify="left")
        self.lbl_estado.pack(anchor="w", pady=10)

    def guardar_ruta(self, clave, ruta):
        # Recargar JSON por si el usuario lo modificó a mano antes de cambiar la ruta
        self.datos_config = cargar_configuracion()
        self.datos_config[clave] = ruta
        guardar_configuracion(self.datos_config)

    def cambiar_origen(self):
        nueva = filedialog.askdirectory(title="Selecciona la carpeta con los archivos mezclados")
        if nueva:
            self.ruta_origen = os.path.abspath(nueva)
            self.guardar_ruta("Ruta_Origen_Estructura", self.ruta_origen)
            self.lbl_origen.config(text=f"Origen: {self.ruta_origen}")

    def cambiar_destino(self):
        nueva = filedialog.askdirectory(title="Selecciona dónde crear la estructura 'Pruebas'")
        if nueva:
            self.ruta_destino = os.path.abspath(nueva)
            self.guardar_ruta("Ruta_Destino_Estructura", self.ruta_destino)
            self.lbl_destino.config(text=f"Destino: {self.ruta_destino}")

    def organizar_archivos(self):
        if not self.ruta_origen or not os.path.exists(self.ruta_origen):
            self.lbl_estado.config(text="Error: Ruta de origen inválida.", fg=self.btn_orange)
            return
        if not self.ruta_destino or not os.path.exists(self.ruta_destino):
            self.lbl_estado.config(text="Error: Ruta de destino inválida.", fg=self.btn_orange)
            return

        # Leemos el JSON en el momento exacto para aplicar cambios dinámicos
        datos_actualizados = cargar_configuracion()
        estructura = datos_actualizados.get("Estructura_Archivos", {})
        config_zip = datos_actualizados.get("Configuracion_Zip", {})

        if not estructura:
            self.lbl_estado.config(text="Error: No hay estructura en el config.json.", fg=self.btn_orange)
            return

        archivos_copiados = 0
        zips_creados = 0

        self.lbl_estado.config(text="Procesando... copiando archivos.", fg="white")
        self.root.update()

        try:
            # 1. ORDENAR Y COPIAR ARCHIVOS
            for raiz, carpetas, archivos in os.walk(self.ruta_origen):
                # Evita un bucle infinito si la carpeta destino está dentro de la origen
                if os.path.commonpath([self.ruta_destino]) == os.path.commonpath([self.ruta_destino, raiz]):
                    continue

                for archivo in archivos:
                    for ruta_carpeta_destino, patrones in estructura.items():
                        coincide = False
                        for patron in patrones:
                            if fnmatch.fnmatch(archivo, patron):
                                coincide = True
                                break
                        
                        if coincide:
                            carpeta_final = os.path.join(self.ruta_destino, ruta_carpeta_destino)
                            os.makedirs(carpeta_final, exist_ok=True)
                            
                            ruta_origen_archivo = os.path.join(raiz, archivo)
                            ruta_destino_archivo = os.path.join(carpeta_final, archivo)
                            
                            try:
                                if not os.path.exists(ruta_destino_archivo):
                                    shutil.copy2(ruta_origen_archivo, ruta_destino_archivo)
                                    archivos_copiados += 1
                            except shutil.SameFileError:
                                pass
                            
                            break

            # 2. GENERAR ARCHIVOS ZIP (Solo con la carpeta final)
            if config_zip:
                self.lbl_estado.config(text=f"Copiados {archivos_copiados} archivos. Comprimiendo ZIP...", fg="white")
                self.root.update()

                for nombre_zip, carpetas_a_zipear in config_zip.items():
                    ruta_zip_completa = os.path.join(self.ruta_destino, nombre_zip)
                    
                    with zipfile.ZipFile(ruta_zip_completa, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for subcarpeta in carpetas_a_zipear:
                            # Ejemplo de subcarpeta: "Pruebas/Evidencias de Pruebas/Evidencias"
                            ruta_subcarpeta = os.path.join(self.ruta_destino, subcarpeta)
                            
                            if os.path.exists(ruta_subcarpeta):
                                # Extraemos SOLAMENTE el nombre final de la carpeta (ej. "Evidencias")
                                nombre_carpeta_final = os.path.basename(os.path.normpath(ruta_subcarpeta))
                                
                                for raiz_zip, dirs_zip, archivos_zip in os.walk(ruta_subcarpeta):
                                    for arch_nombre in archivos_zip:
                                        ruta_archivo_completa = os.path.join(raiz_zip, arch_nombre)
                                        
                                        # Calculamos la ruta relativa del archivo respecto a su carpeta contenedora
                                        ruta_relativa_interna = os.path.relpath(ruta_archivo_completa, ruta_subcarpeta)
                                        
                                        # Construimos la ruta para el ZIP: "Evidencias/archivo.docx"
                                        arcname_arch = os.path.join(nombre_carpeta_final, ruta_relativa_interna)
                                        
                                        zipf.write(ruta_archivo_completa, arcname_arch)
                                        
                    zips_creados += 1

            self.lbl_estado.config(text=f"¡Éxito! {archivos_copiados} archivos organizados y {zips_creados} ZIP(s) creados.", fg="#4CAF50")

        except Exception as e:
            self.lbl_estado.config(text=f"Error durante el proceso: {str(e)}", fg="red")


if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    ventana = tk.Tk()
    ventana.configure(bg="#121212")
    app = OrganizadorEstructura(ventana)
    ventana.mainloop()