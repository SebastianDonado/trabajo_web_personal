import tkinter as tk
from tkinter import ttk, messagebox
from Clases import Restaurante, Producto
from Conexion_fb import db

# Configuración de estilos (similar a otras ventanas)
FONDO = "#F5E9CC"
COLOR_ENCABEZADO = "#8B2F23"
COLOR_BOTON_ACCION = "#40754C" # Verde para acciones positivas
COLOR_BOTON_PELIGRO = "#8B2F23" # Rojo para eliminar (aunque no lo usaremos aquí directamente)
COLOR_TEXTO = "#1D5A75"
FUENTE_TITULO = ("Times New Roman", 16, "bold")
FUENTE_SUBTITULO = ("Times New Roman", 12, "bold")
FUENTE_NORMAL = ("Times New Roman", 11)
FUENTE_ENTRADA = ("Times New Roman", 10)

def ventana_inventario(restaurante, nombre_usuario):
    ventana = tk.Tk()
    ventana.iconbitmap("Logo_migaja.ico")
    ventana.title(f"📦 Gestión de Inventario - {nombre_usuario}")
    ventana.geometry("700x600")
    ventana.configure(bg=FONDO)

    main_frame = tk.Frame(ventana, bg=FONDO)
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    canvas = tk.Canvas(main_frame, bg=FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=FONDO)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Título
    tk.Label(scrollable_frame,
             text=f"Inventario de Productos - {nombre_usuario}",
             font=FUENTE_TITULO,
             bg=FONDO,
             fg=COLOR_ENCABEZADO).pack(pady=(0, 15))

    # --- Sección de Listado de Productos con Inventario ---
    listado_frame = tk.LabelFrame(scrollable_frame, text="Stock Actual del Menú",
                                  font=FUENTE_SUBTITULO, bg="white", fg=COLOR_ENCABEZADO,
                                  padx=10, pady=10, relief="groove", borderwidth=2)
    listado_frame.pack(fill="both", expand=True, pady=10, padx=5)

    # Treeview para mostrar los productos y su stock
    tree = ttk.Treeview(listado_frame, columns=("Codigo", "Nombre", "Unidades"), show="headings", height=15)
    tree.heading("Codigo", text="Código")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Unidades", text="Unidades")

    # Ancho de columnas
    tree.column("Codigo", width=100, anchor="center")
    tree.column("Nombre", width=250)
    tree.column("Unidades", width=100, anchor="e")

    tree.pack(fill="both", expand=True)

    # Scrollbar para el Treeview
    tree_scrollbar = ttk.Scrollbar(listado_frame, orient="vertical", command=tree.yview)
    tree_scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=tree_scrollbar.set)

    # --- Sección para Actualizar Unidades ---
    update_frame = tk.LabelFrame(scrollable_frame, text="Actualizar Unidades de Producto",
                                 font=FUENTE_SUBTITULO, bg="white", fg=COLOR_ENCABEZADO,
                                 padx=15, pady=15, relief="groove", borderwidth=2)
    update_frame.pack(fill="x", pady=10, padx=5)

    tk.Label(update_frame, text="Código del Producto:", font=FUENTE_NORMAL, bg="white", fg=COLOR_TEXTO).grid(row=0, column=0, sticky="w", pady=5, padx=5)
    entry_codigo_update = tk.Entry(update_frame, font=FUENTE_ENTRADA, width=20)
    entry_codigo_update.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
    entry_codigo_update.config(state="readonly") # Inicialmente readonly para evitar edición manual

    tk.Label(update_frame, text="Nuevas Unidades:", font=FUENTE_NORMAL, bg="white", fg=COLOR_TEXTO).grid(row=1, column=0, sticky="w", pady=5, padx=5)
    entry_unidades_update = tk.Entry(update_frame, font=FUENTE_ENTRADA, width=20)
    entry_unidades_update.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

    def cargar_seleccion_en_campos():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la lista para actualizar.")
            return

        values = tree.item(selected_item, "values")
        codigo = values[0]
        unidades = values[2]

        entry_codigo_update.config(state="normal") # Habilitar para escribir
        entry_codigo_update.delete(0, tk.END)
        entry_codigo_update.insert(0, codigo)
        entry_codigo_update.config(state="readonly") # Volver a deshabilitar

        entry_unidades_update.delete(0, tk.END)
        entry_unidades_update.insert(0, unidades)

    def actualizar_unidades():
        codigo = entry_codigo_update.get().strip()
        nuevas_unidades_str = entry_unidades_update.get().strip()

        if not codigo or not nuevas_unidades_str:
            messagebox.showwarning("Advertencia", "Debe seleccionar un producto y especificar las nuevas unidades.")
            return

        try:
            nuevas_unidades = int(nuevas_unidades_str)
            if nuevas_unidades < 0:
                messagebox.showwarning("Advertencia", "Las unidades no pueden ser negativas.")
                return
        except ValueError:
            messagebox.showwarning("Advertencia", "Las unidades deben ser un número entero válido.")
            return

        if messagebox.askyesno("Confirmar Actualización", f"¿Desea actualizar las unidades de '{codigo}' a {nuevas_unidades}?"):
            if restaurante.actualizar_unidades_producto(codigo, nuevas_unidades):
                messagebox.showinfo("Éxito", "Unidades actualizadas exitosamente.")
                mostrar_inventario() # Refrescar la lista
                # Limpiar campos después de actualizar
                entry_codigo_update.config(state="normal")
                entry_codigo_update.delete(0, tk.END)
                entry_codigo_update.config(state="readonly")
                entry_unidades_update.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "No se pudo actualizar las unidades.")

    btn_cargar_seleccion = tk.Button(update_frame, text="Cargar Seleccionado", command=cargar_seleccion_en_campos,
                                     bg="#FFC107", fg="black", font=FUENTE_NORMAL, width=20) # Amarillo para cargar
    btn_cargar_seleccion.grid(row=2, column=0, pady=10, padx=5, sticky="w")

    btn_actualizar_unidades = tk.Button(update_frame, text="Actualizar Unidades", command=actualizar_unidades,
                                        bg=COLOR_BOTON_ACCION, fg="white", font=FUENTE_NORMAL, width=20)
    btn_actualizar_unidades.grid(row=2, column=1, pady=10, padx=5, sticky="e")

    def mostrar_inventario():
        # Limpiar Treeview
        for item in tree.get_children():
            tree.delete(item)

        productos_inventario = restaurante.obtener_inventario()
        for prod in productos_inventario:
            tree.insert("", "end", values=(prod.codigo, prod.nombre, prod.unidades), iid=prod.codigo)

    # Botones de control de la ventana
    control_frame = tk.Frame(scrollable_frame, bg=FONDO)
    control_frame.pack(fill="x", pady=(20, 10))

    tk.Button(control_frame,
              text="🔄 Actualizar Inventario",
              command=mostrar_inventario,
              bg=COLOR_ENCABEZADO,
              fg="white",
              font=FUENTE_NORMAL).pack(side="left", padx=5)

    tk.Button(control_frame,
              text="🔙 Cerrar Sesión",
              command=lambda: [ventana.destroy(), iniciar_app()], # Asume iniciar_app() está en Login.py
              bg="#333333",
              fg="white",
              font=FUENTE_NORMAL).pack(side="right", padx=5)

    # Mostrar inventario al iniciar
    mostrar_inventario()

    ventana.mainloop()

# Función dummy para el cierre de sesión, se importará de Login.py en el uso real
def iniciar_app():
    pass

if __name__ == "__main__":
    # Esto es solo para probar la ventana Inventario directamente
    # En la aplicación real, se llamará desde Login.py
    restaurante_instance = Restaurante(db)
    ventana_inventario(restaurante_instance, "AdminInventario")
