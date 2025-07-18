# Mesero.py
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from Clases import Restaurante, Pedido
from Conexion_fb import db

FONDO = "#F5E9CC"
COLOR_BOTON = "#8B2F23"
COLOR_TEXTO = "#1D5A75"
FUENTE = ("Times New Roman", 12)
TEXTO_TITULO = ("Times New Roman", 14, "bold")
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
    ventana.imagenes_guardadas = {}

    main_content_area = tk.Frame(ventana, bg=FONDO)
    main_content_area.pack(expand=True, fill="both", padx=20, pady=10)

    tk.Label(main_content_area, text=f"Bienvenido, {nombre_usuario}\nMenú", font=TEXTO_TITULO, bg=FONDO, fg=COLOR_TEXTO).pack(pady=10)

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

    productos = [p for p in restaurante.obtener_menu() if p.unidades > 0]
    spins_producto = {p.codigo: [tk.IntVar(value=0), p] for p in productos}

    resumen_pedido = tk.Label(main_content_area, text="Pedido vacío", bg=FONDO, font=FUENTE, wraplength=500, justify="left")
    resumen_pedido.pack(pady=5)

    envio_frame = tk.Frame(main_content_area, bg=FONDO)
    envio_frame.pack(pady=10)

    tk.Label(envio_frame, text="Mesa:", bg=FONDO, font=FUENTE).pack()
    entrada_mesa = tk.Entry(envio_frame, font=FUENTE)
    entrada_mesa.pack()

    def actualizar_resumen():
        items = []
        for codigo, (var, producto) in spins_producto.items():
            cant = var.get()
            if cant > 0:
                items.append(f"{producto.nombre} x{cant}")
        resumen_pedido.config(text="Pedido: " + ", ".join(items) if items else "Pedido vacío")

    def mostrar_categoria(categoria):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        productos_filtrados = [p for p in productos if p.categoria.strip().lower() == categoria.strip().lower()]
        productos_por_sub = {}
        for p in productos_filtrados:
            sub = p.subcategoria or "Otros"
            productos_por_sub.setdefault(sub, []).append(p)

        for sub, lista in productos_por_sub.items():
            tk.Label(scroll_frame, text=sub, font=TEXTO_TITULO, bg=FONDO, fg=COLOR_TEXTO).pack(padx=10, pady=(10, 0))
            for p in lista:
                frame = tk.Frame(scroll_frame, bg=FONDO, bd=1, relief="solid")
                frame.pack(pady=5, padx=10, fill="x")

                label_img = tk.Label(frame, bg=FONDO)
                label_img.pack(side="left", padx=5)
                if p.imagen:
                    try:
                        r = requests.get(p.imagen)
                        img = Image.open(BytesIO(r.content)).resize((80, 80), Image.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        label_img.config(image=img_tk)
                        label_img.image = img_tk
                        ventana.imagenes_guardadas[p.codigo] = img_tk
                    except Exception as e:
                        print(f"Error imagen {p.nombre}: {e}")

                info = tk.Frame(frame, bg=FONDO)
                info.pack(side="left", expand=True, fill="both")
                tk.Label(info, text=p.nombre, font=FUENTE, bg=FONDO).pack(anchor="w")
                tk.Label(info, text=f"${p.precio}", font=FUENTE, bg=FONDO).pack(anchor="w")

                botones = tk.Frame(frame, bg=FONDO)
                botones.pack(side="right", padx=10)
                cantidad = spins_producto[p.codigo][0]

                def sumar(v=cantidad):
                    v.set(v.get() + 1)
                    actualizar_resumen()

                def restar(v=cantidad):
                    if v.get() > 0:
                        v.set(v.get() - 1)
                        actualizar_resumen()

                tk.Button(botones, text="+", font=TEXTO_TITULO, command=sumar).pack()
                tk.Label(botones, textvariable=cantidad, font=FUENTE, bg=FONDO, width=4).pack()
                tk.Button(botones, text="-", font=TEXTO_TITULO, command=restar).pack()

        actualizar_resumen()

    def enviar():
        mesa = entrada_mesa.get().strip()
        if not mesa:
            messagebox.showwarning("⚠️", "Ingrese el número de mesa")
            return
        if restaurante.existe_pedido_mesa(mesa):
            messagebox.showwarning("⚠️", f"Ya existe un pedido para la mesa {mesa}")
            return
        pedido = Pedido(mesa=mesa)
        for codigo, (var, producto) in spins_producto.items():
            for _ in range(var.get()):
                pedido.agregar_producto(producto)
        if not pedido.items:
            messagebox.showwarning("⚠️", "Seleccione al menos un producto")
            return
        pedido.generar_codigo(restaurante)
        try:
            restaurante.enviar_pedido(pedido)
            messagebox.showinfo("✅", f"Pedido enviado correctamente. Código: {pedido.codigo}")
            entrada_mesa.delete(0, tk.END)
            for var, _ in spins_producto.values():
                var.set(0)
            actualizar_resumen()
        except Exception as e:
            messagebox.showerror("❌", f"Error: {e}")

    tk.Button(envio_frame, text="Enviar Pedido", command=enviar, bg=COLOR_BOTON, fg="white", font=TEXTO_TITULO).pack(pady=5)

    botones_categorias = tk.Frame(main_content_area, bg=FONDO)
    botones_categorias.pack(pady=5)
    for cat in CATEGORIAS_PRINCIPALES:
        tk.Button(botones_categorias, text=cat, command=lambda c=cat: mostrar_categoria(c),
                  font=FUENTE, bg=COLOR_BOTON, fg="white", width=15).pack(side="left", padx=5, pady=5)

    # ✅ BOTÓN DE CERRAR SESIÓN - AÑADIDO
    cerrar_sesion_frame = tk.Frame(main_content_area, bg=FONDO)
    cerrar_sesion_frame.pack(pady=(10, 5))
    tk.Button(cerrar_sesion_frame,
              text="🔙 Cerrar Sesión",
              command=lambda: [ventana.destroy(), iniciar_app()],
              bg="#333333",
              fg="white",
              font=TEXTO_TITULO,
              width=20).pack(pady=5)

    mostrar_categoria("Bebidas")
    ventana.mainloop()

if __name__ == "__main__":
    restaurante = Restaurante(db)
    ventana_mesero(restaurante, "MeseroTest")
