import tkinter as tk
from tkinter import messagebox
from Conexion_fb import db

def ventana_registro(ventana_login):
    ventana = tk.Toplevel()
    ventana.title("📝 Registrar Nuevo Usuario")
    ventana.geometry("400x350")
    ventana.configure(bg="#F5E9CC")
    ventana.iconbitmap("Logo_migaja.ico")
    ventana.resizable(False, False)

    def registrar():
        nombre = entrada_nombre.get().strip()
        usuario = entrada_usuario.get().strip()
        contraseña = entrada_contraseña.get().strip()
        confirmar = entrada_confirmar.get().strip()
        rol = rol_var.get()

        # Validaciones
        if not all([nombre, usuario, contraseña, confirmar]):
            messagebox.showwarning("⚠️", "Todos los campos son obligatorios")
            return
            
        if contraseña != confirmar:
            messagebox.showwarning("⚠️", "Las contraseñas no coinciden")
            return

        try:
            # Verificar si el usuario ya existe
            if db.collection("usuarios").document(usuario).get().exists:
                messagebox.showerror("❌", "El usuario ya existe")
                return
                
            # Crear nuevo usuario
            db.collection("usuarios").document(usuario).set({
                "nombre": nombre,
                "contraseña": contraseña,
                "rol": rol
            })
            
            messagebox.showinfo("✅", "Usuario registrado exitosamente")
            ventana.destroy()
            ventana_login.deiconify()
            
        except Exception as e:
            messagebox.showerror("❌", f"Error al registrar: {str(e)}")

    # Widgets
    tk.Label(ventana, text="Nombre completo:", bg="#F5E9CC").pack(pady=5)
    entrada_nombre = tk.Entry(ventana)
    entrada_nombre.pack()

    tk.Label(ventana, text="Usuario:", bg="#F5E9CC").pack(pady=5)
    entrada_usuario = tk.Entry(ventana)
    entrada_usuario.pack()

    tk.Label(ventana, text="Contraseña:", bg="#F5E9CC").pack(pady=5)
    entrada_contraseña = tk.Entry(ventana, show="*")
    entrada_contraseña.pack()

    tk.Label(ventana, text="Confirmar contraseña:", bg="#F5E9CC").pack(pady=5)
    entrada_confirmar = tk.Entry(ventana, show="*")
    entrada_confirmar.pack()

    tk.Label(ventana, text="Rol:", bg="#F5E9CC").pack(pady=5)
    rol_var = tk.StringVar(value="Mesero")
    # Añade "Administrador" a las opciones de rol
    tk.OptionMenu(ventana, rol_var, "Mesero", "Cocinero", "Administrador").pack() 

    # Botones
    tk.Button(ventana, text="Registrar", command=registrar, bg="#40754C", fg="white", width=15).pack(pady=15)
    tk.Button(ventana, text="Cancelar", command=lambda: [ventana.destroy(), ventana_login.deiconify()], 
              bg="#8B2F23", fg="white").pack()

    ventana.protocol("WM_DELETE_WINDOW", lambda: [ventana.destroy(), ventana_login.deiconify()])
