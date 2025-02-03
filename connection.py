import tkinter as tk
from tkinter import messagebox
from analysis import connect_to_db

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
    
    # AQUI REDIRIGIR A LA NUEVA VENTANA DONDE SE ANALIZA LA BASE DE DATOS
    connection_gui.destroy() # Cierra la ventana de conexión


    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Nueva Interfaz")
    nueva_ventana.geometry("400x400")
    nueva_ventana.resizable(False, False)

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
