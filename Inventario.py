# Inventario.py
import tkinter as tk
from tkinter import ttk, messagebox
from Clases import Producto
from PIL import Image, ImageTk

FONDO = "#F5E9CC"
COLOR_ENCABEZADO = "#8B2F23"
COLOR_BOTON_ACCION = "#40754C"
COLOR_BOTON_PELIGRO = "#8B2F23"
COLOR_TEXTO = "#1D5A75"
FUENTE_TITULO = ("Times New Roman", 20, "bold")
FUENTE_NORMAL = ("Times New Roman", 14)

def ventana_inventario(restaurante, nombre_usuario, return_callback):
    ventana = tk.Toplevel()
    ventana.title("Gestión de Inventario - La Migaja")
    ventana.geometry("900x650")
    ventana.configure(bg=FONDO)
    ventana.iconbitmap("Logo_migaja.ico")

    # Título centrado
    tk.Label(ventana, text=f"Inventario - Bienvenido {nombre_usuario}",
             font=FUENTE_TITULO, fg=COLOR_ENCABEZADO, bg=FONDO).pack(pady=20)

    # Frame principal centrado
    main_frame = tk.Frame(ventana, bg="white", bd=2, relief="groove")
    main_frame.pack(padx=30, pady=20, fill="both", expand=True)

    # Tabla Treeview
    tree = ttk.Treeview(main_frame, columns=("codigo", "nombre", "unidades", "precio"),
                        show="headings", height=15)
    tree.heading("codigo", text="Código")
    tree.heading("nombre", text="Nombre")
    tree.heading("unidades", text="Unidades")
    tree.heading("precio", text="Precio")

    for col in ("codigo", "nombre", "unidades", "precio"):
        tree.column(col, anchor="center", width=200)

    tree.pack(pady=10, fill="both", expand=True)

    # Scrollbar para Treeview
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Entradas de edición de unidades
    form_frame = tk.Frame(ventana, bg=FONDO)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Código:", font=FUENTE_NORMAL, bg=FONDO, fg=COLOR_TEXTO).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    codigo_entry = tk.Entry(form_frame, font=FUENTE_NORMAL, width=20)
    codigo_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Unidades Nuevas:", font=FUENTE_NORMAL, bg=FONDO, fg=COLOR_TEXTO).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    unidades_entry = tk.Entry(form_frame, font=FUENTE_NORMAL, width=20)
    unidades_entry.grid(row=1, column=1, padx=10, pady=5)

    # Botones de acción
    btn_frame = tk.Frame(ventana, bg=FONDO)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Actualizar Unidades", command=lambda: actualizar_unidades(),
              font=FUENTE_NORMAL, bg=COLOR_BOTON_ACCION, fg="white", width=20).pack(side="left", padx=15)

    tk.Button(btn_frame, text="Actualizar Tabla", command=lambda: mostrar_inventario(),
              font=FUENTE_NORMAL, bg="#007BFF", fg="white", width=20).pack(side="left", padx=15)

    tk.Button(btn_frame, text="Volver al Login", command=lambda: volver(),
              font=FUENTE_NORMAL, bg=COLOR_BOTON_PELIGRO, fg="white", width=20).pack(side="left", padx=15)

    def mostrar_inventario():
        for item in tree.get_children():
            tree.delete(item)
        inventario = restaurante.obtener_inventario()
        for producto in inventario:
            tree.insert("", "end", values=(producto.codigo, producto.nombre, producto.unidades, f"${producto.precio}"))

    def actualizar_unidades():
        codigo = codigo_entry.get().strip()
        unidades = unidades_entry.get().strip()
        if not codigo or not unidades:
            messagebox.showwarning("Advertencia", "Debes llenar ambos campos.")
            return
        try:
            unidades_int = int(unidades)
            if restaurante.actualizar_unidades_producto(codigo, unidades_int):
                messagebox.showinfo("Éxito", f"Unidades de {codigo} actualizadas.")
                mostrar_inventario()
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
        except ValueError:
            messagebox.showerror("Error", "Unidades deben ser un número entero.")

    def volver():
        ventana.destroy()
        return_callback()

    mostrar_inventario()
    ventana.mainloop()
