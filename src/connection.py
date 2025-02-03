import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from analysis import (
    connect_to_db,
    detect_orphan_records,
    detect_duplicate_keys,
    detect_missing_foreign_keys,
    detect_foreign_keys_not_in_primary_key,
    close_connection,
    get_results_path
)

def conectar():
    servidor = entry_servidor.get()
    base_datos = entry_bd.get()
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()
    
    if servidor and base_datos and usuario and contrasena:
        if connect_to_db(servidor, base_datos, usuario, contrasena):
            go_to_analyze()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
    else:
        messagebox.showwarning("Error", "Por favor, completa todos los campos.")


def go_to_analyze():
    connection_gui.destroy()  # Cierra la ventana de conexión

    # Crear ventana de análisis
    analysis_window = tk.Tk()
    analysis_window.title("Análisis de Base de Datos SQL Server")
    analysis_window.geometry("800x600")
    analysis_window.resizable(True, True)

    # Frame principal con scrollbar
    main_frame = tk.Frame(analysis_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Canvas y scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Título
    title_label = tk.Label(scrollable_frame, text="Resultados del Análisis", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Función para crear secciones de resultados
    def create_result_section(title, frame):
        section_frame = tk.LabelFrame(frame, text=title, padx=5, pady=5)
        section_frame.pack(fill=tk.X, pady=5)
        
        text_widget = tk.Text(section_frame, height=10, wrap=tk.WORD)
        text_widget.pack(fill=tk.X, padx=5, pady=5)
        
        return text_widget

    # Crear secciones para cada tipo de análisis
    orphan_text = create_result_section("Registros Huérfanos", scrollable_frame)
    duplicate_text = create_result_section("Claves Duplicadas", scrollable_frame)
    missing_fk_text = create_result_section("Tablas sin Claves Foráneas", scrollable_frame)
    fk_not_pk_text = create_result_section("Claves Foráneas fuera de PK", scrollable_frame)

    # Función para ejecutar el análisis
    def run_analysis():
        try:
            # Limpiar resultados anteriores
            for text_widget in [orphan_text, duplicate_text, missing_fk_text, fk_not_pk_text]:
                text_widget.delete(1.0, tk.END)

            # Ejecutar análisis y obtener las rutas de los archivos
            orphan_path = detect_orphan_records()
            duplicate_path = detect_duplicate_keys()
            missing_fk_path = detect_missing_foreign_keys()
            fk_not_pk_path = detect_foreign_keys_not_in_primary_key()

            # Función para cargar y mostrar resultados
            def load_results(file_path, text_widget):
                try:
                    if not file_path or not os.path.exists(file_path):
                        text_widget.insert(tk.END, "No se encontraron resultados.\n")
                        return

                    with open(file_path, 'r', encoding='utf-8') as f:
                        results = json.load(f)

                    if not results:
                        text_widget.insert(tk.END, "No se encontraron problemas.\n")
                        return

                    # Mostrar resultados
                    for item in results:
                        text_widget.insert(tk.END, json.dumps(item, indent=2, ensure_ascii=False))
                        text_widget.insert(tk.END, "\n" + "-"*50 + "\n")

                except Exception as e:
                    text_widget.insert(tk.END, f"Error al cargar resultados: {str(e)}\n")

            # Cargar resultados en cada sección
            load_results(orphan_path, orphan_text)
            load_results(duplicate_path, duplicate_text)
            load_results(missing_fk_path, missing_fk_text)
            load_results(fk_not_pk_path, fk_not_pk_text)

            messagebox.showinfo("Éxito", "Análisis completado correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis: {str(e)}")

    def on_closing():
        """Función para manejar el cierre de la ventana"""
        try:
            close_connection()  # Cerrar la conexión a la base de datos
        finally:
            analysis_window.destroy()

    # Botones de control
    button_frame = tk.Frame(scrollable_frame)
    button_frame.pack(pady=10)

    analyze_button = tk.Button(
        button_frame,
        text="Ejecutar Análisis",
        command=run_analysis,
        bg="#0078D7",
        fg="white",
        font=("Arial", 10)
    )
    analyze_button.pack(side=tk.LEFT, padx=5)

    exit_button = tk.Button(
        button_frame,
        text="Salir",
        command=on_closing,
        bg="#FF4444",
        fg="white",
        font=("Arial", 10)
    )
    exit_button.pack(side=tk.LEFT, padx=5)

    # Configurar el scrollbar
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configurar el binding del mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Configurar el protocolo de cierre de ventana
    analysis_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Iniciar ventana
    analysis_window.mainloop()

# Crear la ventana principal
connection_gui = tk.Tk()
connection_gui.title("Auditor de base de datos SQL Server")
connection_gui.geometry("400x400")
connection_gui.resizable(False, False)

# Agregar widgets
titulo = tk.Label(connection_gui, text="Auditor de base de datos SQL Server", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

descripcion = tk.Label(connection_gui, text="Ingresa los datos de la conexión", font=("Arial", 12))
descripcion.pack(pady=5)

tk.Label(connection_gui, text="Servidor:", font=("Arial", 10)).pack(anchor="w", padx=20)
entry_servidor = tk.Entry(connection_gui, width=40)
entry_servidor.pack(pady=5)

tk.Label(connection_gui, text="Base de datos:", font=("Arial", 10)).pack(anchor="w", padx=20)
entry_bd = tk.Entry(connection_gui, width=40)
entry_bd.pack(pady=5)

tk.Label(connection_gui, text="Usuario:", font=("Arial", 10)).pack(anchor="w", padx=20)
entry_usuario = tk.Entry(connection_gui, width=40)
entry_usuario.pack(pady=5)

tk.Label(connection_gui, text="Contraseña:", font=("Arial", 10)).pack(anchor="w", padx=20)
entry_contrasena = tk.Entry(connection_gui, show="*", width=40)
entry_contrasena.pack(pady=5)

boton_conectar = tk.Button(connection_gui, text="Conectar", command=conectar, font=("Arial", 10), bg="#0078D7", fg="white")
boton_conectar.pack(pady=20)

# Iniciar el bucle de la interfaz
connection_gui.mainloop()
