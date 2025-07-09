import tkinter as tk
from tkinter import messagebox
# No importamos ventana_registro directamente aquí, se pasa como argumento si es necesario
from Conexion_fb import db
from Clases import Restaurante

# Importar las ventanas de rol al inicio del archivo
# Asegúrate de que estos archivos existan en la misma carpeta
from Mesero import ventana_mesero
from Cocinero import ventana_cocinero
from Inventario import ventana_inventario
from Inventario import ventana_inventario
from Registrarse import ventana_registro # Importar Registrarse aquí para la función abrir_registro

restaurante = Restaurante(db)

# Variable global para la ventana principal de la aplicación (el login)
# Se inicializará una sola vez.
main_app_window = None

def iniciar_app():
    """
    Función para inicializar o mostrar la ventana principal de login.
    Se asegura de que solo haya una instancia de tk.Tk().
    """
    global main_app_window
    if main_app_window is None:
        # Crea la ventana principal solo si no existe
        main_app_window = tk.Tk()
        main_app_window.title("🔐 Login - La Migaja")
        main_app_window.geometry("350x250")
        main_app_window.configure(bg="#F5E9CC")
        main_app_window.iconbitmap("Logo_migaja.ico")
        main_app_window.resizable(False, False)

        # Widgets de la ventana de login
        tk.Label(main_app_window, text="Usuario:", bg="#F5E9CC").pack(pady=5)
        entrada_usuario = tk.Entry(main_app_window)
        entrada_usuario.pack()

        tk.Label(main_app_window, text="Contraseña:", bg="#F5E9CC").pack(pady=5)
        entrada_contrasena = tk.Entry(main_app_window, show="*")
        entrada_contrasena.pack()

        # Botones
        # Usamos lambda para pasar los Entry widgets a la función login
        tk.Button(main_app_window, text="Ingresar", command=lambda: login(entrada_usuario, entrada_contrasena), bg="#8B2F23", fg="white", width=15).pack(pady=10)
        # Pasamos la ventana principal para que ventana_registro pueda ocultarla
        tk.Button(main_app_window, text="Registrar nuevo usuario", command=lambda: abrir_registro(main_app_window), bg="#40754C", fg="white").pack()
        
        # Protocolo para manejar el cierre de la ventana principal
        main_app_window.protocol("WM_DELETE_WINDOW", on_closing_main_window)
    else:
        # Si la ventana ya existe, simplemente la mostramos
        main_app_window.deiconify()

def on_closing_main_window():
    """Maneja el cierre de la ventana principal de la aplicación."""
    if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
        main_app_window.destroy()

def return_to_login_callback():
    """
    Función de callback para ser pasada a las ventanas secundarias.
    Cuando se llama, hace visible la ventana principal de login.
    """
    global main_app_window
    if main_app_window:
        main_app_window.deiconify() # Muestra la ventana principal de login

def login(entrada_usuario_widget, entrada_contrasena_widget):
    """
    Función para manejar el proceso de login.
    Recibe los widgets de entrada para obtener sus valores.
    """
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
                main_app_window.withdraw() # Oculta la ventana principal de login
                if user_data["rol"] == "Mesero":
                    # Pasa el callback para que la ventana de mesero pueda volver al login
                    ventana_mesero(restaurante, user_data["nombre"], return_to_login_callback)
                elif user_data["rol"] == "Cocinero":
                    # Pasa el callback para que la ventana de cocinero pueda volver al login
                    ventana_cocinero(restaurante, user_data["nombre"], return_to_login_callback)
                elif user_data["rol"] == "Administrador":
                    # Pasa el callback para que la ventana de opciones de admin pueda volver al login
                    mostrar_opciones_administrador(restaurante, user_data["nombre"], return_to_login_callback)
            else:
                messagebox.showerror("❌ Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("❌ Error", "Usuario no registrado")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error de conexión: {str(e)}")

def abrir_registro(parent_window):
    """
    Abre la ventana de registro.
    Oculta la ventana padre (login) y pasa un callback para que el registro
    pueda volver a mostrar el login.
    """
    parent_window.withdraw() # Oculta la ventana de login
    ventana_registro(parent_window, return_to_login_callback) # Pasa el callback

def mostrar_opciones_administrador(restaurante_instance, nombre_usuario, return_callback):
    """
    Muestra la ventana de opciones para el administrador.
    """
    # Crea una ventana secundaria (Toplevel) que es hija de la ventana principal
    opciones_ventana = tk.Toplevel(main_app_window) 
    opciones_ventana.title("Opciones de Administrador")
    opciones_ventana.geometry("300x200")
    opciones_ventana.configure(bg="#F5E9CC")
    opciones_ventana.iconbitmap("Logo_migaja.ico")
    opciones_ventana.resizable(False, False)

    tk.Label(opciones_ventana, text=f"Bienvenido, {nombre_usuario}", font=("Times New Roman", 12, "bold"), bg="#F5E9CC").pack(pady=15)

    def abrir_gestion_menu():
        opciones_ventana.destroy() # Destruye la ventana de opciones
        # Llama a la ventana de administración, pasando el callback de retorno
        ventana_administrador(restaurante_instance, nombre_usuario, return_callback) 

    def abrir_gestion_inventario():
        opciones_ventana.destroy() # Destruye la ventana de opciones
        # Llama a la ventana de inventario, pasando el callback de retorno
        ventana_inventario(restaurante_instance, nombre_usuario, return_callback) 

    tk.Button(opciones_ventana, text="Gestión de Menú", command=abrir_gestion_menu,
              bg="#8B2F23", fg="white", width=20, font=("Times New Roman", 11)).pack(pady=5)
    tk.Button(opciones_ventana, text="Gestión de Inventario", command=abrir_gestion_inventario,
              bg="#40754C", fg="white", width=20, font=("Times New Roman", 11)).pack(pady=5)
    
    # Cuando esta ventana de opciones se cierra, se llama al callback para volver al login
    opciones_ventana.protocol("WM_DELETE_WINDOW", return_callback)

if __name__ == "__main__":
    iniciar_app() # Inicializa la ventana principal
    if main_app_window: # Asegura que main_app_window no sea None antes de llamar a mainloop
        main_app_window.mainloop() # Inicia el bucle de eventos de Tkinter una vez
