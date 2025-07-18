# Login.py
import tkinter as tk
from tkinter import messagebox
from Conexion_fb import db
from Clases import Restaurante

# Importar las ventanas de rol al inicio del archivo
from Mesero import ventana_mesero
from Cocinero import ventana_cocinero
from Inventario import ventana_inventario
from Registrarse import ventana_registro

restaurante = Restaurante(db)

# Variable global para la ventana principal de la aplicación (el login)
main_app_window = None

def iniciar_app():
    global main_app_window
    if main_app_window is None:
        main_app_window = tk.Tk()
        main_app_window.title("🔐 Login - La Migaja")
        main_app_window.geometry("350x250")
        main_app_window.configure(bg="#F5E9CC")
        main_app_window.iconbitmap("Logo_migaja.ico")
        main_app_window.resizable(False, False)

        tk.Label(main_app_window, text="Usuario:", bg="#F5E9CC").pack(pady=5)
        entrada_usuario = tk.Entry(main_app_window)
        entrada_usuario.pack()

        tk.Label(main_app_window, text="Contraseña:", bg="#F5E9CC").pack(pady=5)
        entrada_contrasena = tk.Entry(main_app_window, show="*")
        entrada_contrasena.pack()

        tk.Button(main_app_window, text="Ingresar", command=lambda: login(entrada_usuario, entrada_contrasena),
                  bg="#8B2F23", fg="white", width=15).pack(pady=10)
        tk.Button(main_app_window, text="Registrar nuevo usuario", command=lambda: abrir_registro(main_app_window),
                  bg="#40754C", fg="white").pack()

        main_app_window.protocol("WM_DELETE_WINDOW", on_closing_main_window)
    else:
        main_app_window.deiconify()

def on_closing_main_window():
    if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
        main_app_window.destroy()

def return_to_login_callback():
    global main_app_window
    if main_app_window:
        main_app_window.deiconify()

def login(entrada_usuario_widget, entrada_contrasena_widget):
    usuario = entrada_usuario_widget.get().strip()
    contraseña = entrada_contrasena_widget.get().strip()

    if not usuario or not contraseña:
        messagebox.showwarning("⚠️", "Debes completar todos los campos.")
        return

    try:
        user_ref = db.collection("usuarios").document(usuario).get()

        if user_ref.exists:
            user_data = user_ref.to_dict()
            if user_data["contraseña"] == contraseña:
                main_app_window.withdraw()
                if user_data["rol"] == "Mesero":
                    ventana_mesero(restaurante, user_data["nombre"])
                elif user_data["rol"] == "Cocinero":
                    ventana_cocinero(restaurante, user_data["nombre"])
                elif user_data["rol"] == "Administrador":
                    ventana_inventario(restaurante, user_data["nombre"], return_to_login_callback)
            else:
                messagebox.showerror("❌ Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("❌ Error", "Usuario no registrado")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error de conexión: {str(e)}")

def abrir_registro(parent_window):
    parent_window.withdraw()
    ventana_registro(parent_window)

if __name__ == "__main__":
    iniciar_app()
    if main_app_window:
        main_app_window.mainloop()
