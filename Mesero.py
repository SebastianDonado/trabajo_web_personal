from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from Clases import Restaurante, Pedido
from Conexion_fb import db # Asegúrate de importar db para Restaurante si no lo haces en Clases

# Configuración de estilo
FONDO = "#F5E9CC"
COLOR_BOTON = "#8B2F23"
COLOR_TEXTO = "#1D5A75"
FUENTE = ("Times New Roman", 12)
TEXTO_TITULO = ("Times New Roman", 14, "bold")

# Definición de subcategorías (puedes expandir esto si tienes más)
# Se usa un conjunto para las categorías principales para una rápida verificación
CATEGORIAS_PRINCIPALES = {"Bebidas", "Entradas", "Gourmet"}
subcategorias = {
    "Bebidas": ["Frías", "Calientes", "Alcohólicas"],
    "Entradas": ["Calientes", "Frías", "Delicias Regionales"],
    "Gourmet": ["Andina", "Caribe", "Orinoquía"]
}

def ventana_mesero(restaurante, nombre_usuario):
    ventana = tk.Tk()
    ventana.title(f"La Migaja - Mesero ({nombre_usuario})")
    ventana.geometry("550x720")
    ventana.configure(bg=FONDO)
    ventana.iconbitmap("Logo_migaja.ico")

    categoria_actual = tk.StringVar(value="Bebidas")

    # Un marco principal para centrar todo el contenido
    # Este marco se expandirá y centrará dentro de la ventana.
    main_content_area = tk.Frame(ventana, bg=FONDO)
    main_content_area.pack(expand=True, fill="both", padx=20, pady=10) # Añade padding general y centra

    # --- HEADER ---
    # Ahora top_frame se empaqueta dentro de main_content_area
    top_frame = tk.Frame(main_content_area, bg=FONDO)
    # Se elimina fill="x" para permitir que top_frame se centre dentro de main_content_area
    top_frame.pack(pady=10) 

    try:
        logo = Image.open("Logo_migaja.jpg")
        logo = logo.resize((100, 100), Image.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo)
        ventana.logo_tk = logo_tk
        tk.Label(top_frame, image=logo_tk, bg=FONDO).pack(side="left", padx=10)
    except:
        tk.Label(top_frame, text="La Migaja", font=TEXTO_TITULO, bg=FONDO).pack(side="left")

    tk.Label(top_frame, 
             text=f"Bienvenido, {nombre_usuario}\nMenú", 
             font=TEXTO_TITULO, 
             bg=FONDO, 
             fg=COLOR_TEXTO).pack(side="left")

    # --- CENTRO: productos ---
    # Ahora center_frame se empaqueta dentro de main_content_area
    center_frame = tk.Frame(main_content_area, bg=FONDO)
    center_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(center_frame, bg=FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(center_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=FONDO)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    productos = restaurante.obtener_menu() # Obtiene todos los productos una vez
    spins_producto = {} # Diccionario para almacenar las variables de cantidad de cada producto

    def mostrar_categoria(categoria):
        categoria_actual.set(categoria)
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        # Diccionario para agrupar productos por subcategoría
        productos_por_subcategoria = {}
        for prod in productos:
            # Aseguramos que la categoría del producto coincida con la categoría seleccionada
            # IMPORTANTE: Añadir .strip().lower() para manejar posibles espacios en blanco y diferencias de mayúsculas/minúsculas
            if prod.categoria.strip().lower() == categoria.strip().lower():
                # Usamos la subcategoría del producto o una cadena vacía si no existe
                # IMPORTANTE: Añadir .strip() a la subcategoría también
                sub = prod.subcategoria.strip() if prod.subcategoria else "Otros" # 'Otros' para productos sin subcategoría específica
                if sub not in productos_por_subcategoria:
                    productos_por_subcategoria[sub] = []
                productos_por_subcategoria[sub].append(prod)
        
        # Ordenar las subcategorías para una visualización consistente
        # Primero las subcategorías predefinidas, luego "Otros", luego cualquier otra
        subcats_ordenadas = [s for s in subcategorias.get(categoria, []) if s in productos_por_subcategoria]
        if "Otros" in productos_por_subcategoria and "Otros" not in subcats_ordenadas:
            subcats_ordenadas.append("Otros")
        for s in sorted(productos_por_subcategoria.keys()):
            if s not in subcats_ordenadas:
                subcats_ordenadas.append(s)

        for sub in subcats_ordenadas:
            # Mostrar título de la subcategoría
            # Se elimina anchor="w" para permitir que el título se centre
            tk.Label(scroll_frame, text=sub, font=TEXTO_TITULO, bg=FONDO, fg=COLOR_TEXTO).pack(padx=10, pady=(10, 0))
            
            # Mostrar productos dentro de esta subcategoría
            for prod in productos_por_subcategoria.get(sub, []):
                frame = tk.Frame(scroll_frame, bg=FONDO, bd=1, relief="solid")
                # Se elimina fill="x" para permitir que el marco del producto se centre
                frame.pack(pady=5, padx=10) 

                try:
                    # Intenta cargar la imagen, si falla, simplemente no la muestra
                    img = Image.open(prod.imagen)
                    img = img.resize((80, 80))
                    img_tk = ImageTk.PhotoImage(img)
                    label_img = tk.Label(frame, image=img_tk, bg=FONDO)
                    label_img.image = img_tk # Mantener referencia para evitar que se recoja por el garbage collector
                    label_img.pack(side="left", padx=5)
                except Exception as e:
                    # print(f"No se pudo cargar la imagen para {prod.nombre}: {e}") # Para depuración
                    pass # Si la imagen no se carga, no se muestra nada

                info = tk.Frame(frame, bg=FONDO)
                info.pack(side="left", expand=True, fill="both")
                tk.Label(info, text=prod.nombre, font=FUENTE, bg=FONDO).pack(anchor="w")
                tk.Label(info, text=f"${prod.precio}", font=FUENTE, bg=FONDO).pack(anchor="w")

                botones = tk.Frame(frame, bg=FONDO)
                botones.pack(side="right", padx=10)
                cantidad = tk.IntVar(value=0)

                def aumentar(var=cantidad):
                    var.set(var.get() + 1)

                def disminuir(var=cantidad):
                    if var.get() > 0:
                        var.set(var.get() - 1)

                tk.Button(botones, text="+", font=TEXTO_TITULO, command=aumentar).pack()
                tk.Label(botones, textvariable=cantidad, bg=FONDO, font=FUENTE).pack()
                tk.Button(botones, text="-", font=TEXTO_TITULO, command=disminuir).pack()
                spins_producto[prod.codigo] = (cantidad, prod)

    # --- BOTONES DE CATEGORÍAS ---
    # Ahora bottom_buttons se empaqueta dentro de main_content_area
    bottom_buttons = tk.Frame(main_content_area, bg=FONDO)
    # Eliminamos fill="x" para que el marco se centre por defecto si su contenido no lo fuerza a expandirse
    bottom_buttons.pack(pady=5) 

    for cat in CATEGORIAS_PRINCIPALES: # Iterar sobre el conjunto de categorías principales
        tk.Button(bottom_buttons, text=cat, command=lambda c=cat: mostrar_categoria(c), font=FUENTE,
                  bg=COLOR_BOTON, fg="white", width=15).pack(side="left", padx=5, pady=5)

    # --- FORMULARIO Y ENVÍO ---
    # Ahora envio_frame se empaqueta dentro de main_content_area
    envio_frame = tk.Frame(main_content_area, bg=FONDO)
    # Eliminamos fill="x" para que el marco se centre por defecto
    envio_frame.pack(pady=10)

    tk.Label(envio_frame, text="Mesa:", bg=FONDO, font=FUENTE).pack()
    entrada_mesa = tk.Entry(envio_frame, font=FUENTE)
    entrada_mesa.pack()

    def enviar():
        mesa = entrada_mesa.get().strip()
        if not mesa:
            messagebox.showwarning("⚠️", "Ingrese el número de mesa")
            return

        pedido = Pedido(mesa=mesa)
        for codigo, (var, producto) in spins_producto.items():
            for _ in range(var.get()):
                pedido.agregar_producto(producto)

        if not pedido.items:
            messagebox.showwarning("⚠️", "Seleccione al menos un producto")
            return

        try:
            restaurante.enviar_pedido(pedido)
            messagebox.showinfo("✅", "Pedido enviado")
            entrada_mesa.delete(0, tk.END)
            for var, _ in spins_producto.values():
                var.set(0)
        except Exception as e:
            messagebox.showerror("❌", f"Error: {e}")

    tk.Button(envio_frame, text="Enviar Pedido", command=enviar, bg=COLOR_BOTON, fg="white", font=TEXTO_TITULO).pack(pady=5)

    def volver():
        if messagebox.askyesno("Confirmar", "¿Cerrar sesión?"):
            ventana.destroy()
            from Login import iniciar_app
            iniciar_app()

    tk.Button(envio_frame, text="Cerrar Sesión", command=volver, bg="#333333", fg="white").pack()

    # Mostrar la categoría inicial al iniciar
    mostrar_categoria("Bebidas")
    ventana.mainloop()

# Función dummy para el cierre de sesión, se importará de Login.py en el uso real
def iniciar_app():
    pass

if __name__ == "__main__":
    # Esto es solo para probar la ventana Mesero directamente
    # En la aplicación real, se llamará desde Login.py
    restaurante_instance = Restaurante(db)
    ventana_mesero(restaurante_instance, "MeseroTest")
