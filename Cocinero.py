import tkinter as tk
from tkinter import ttk, messagebox
from Clases import Restaurante

# Configuración de estilos
FONDO = "#F5E9CC"
COLOR_ENCABEZADO = "#8B2F23"
FUENTE_TITULO = ("Times New Roman", 14, "bold")
FUENTE_NORMAL = ("Times New Roman", 11)
FUENTE_PRODUCTOS = ("Times New Roman", 10)

def ventana_cocinero(restaurante, nombre_usuario):
    ventana = tk.Tk()
    ventana.iconbitmap("Logo_migaja.ico")
    ventana.title(f"👨‍🍳 Cocina - {nombre_usuario}")
    ventana.geometry("800x700")
    ventana.configure(bg=FONDO)
    
    # Frame principal con scroll
    main_frame = tk.Frame(ventana, bg=FONDO)
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Canvas y scrollbar
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
             text=f"Pedidos Pendientes - {nombre_usuario}",
             font=FUENTE_TITULO, 
             bg=FONDO,
             fg=COLOR_ENCABEZADO).pack(pady=(0, 15))
    
    # Contenedor de pedidos
    pedidos_frame = tk.Frame(scrollable_frame, bg=FONDO)
    pedidos_frame.pack(fill="x")
    
    def mostrar_pedidos():
        # Limpiar pedidos anteriores
        for widget in pedidos_frame.winfo_children():
            widget.destroy()
        
        # Obtener pedidos
        pedidos = restaurante.obtener_pedidos_pendientes()
        
        if not pedidos:
            tk.Label(pedidos_frame, 
                    text="No hay pedidos pendientes",
                    font=FUENTE_NORMAL,
                    bg=FONDO).pack(pady=20)
            return
            
        for pedido in pedidos:
            # Frame para cada pedido
            frame_pedido = tk.Frame(pedidos_frame, 
                                  bg="white",
                                  relief="groove",
                                  borderwidth=1,
                                  padx=10,
                                  pady=10)
            frame_pedido.pack(fill="x", pady=5, padx=5)
            
            # Encabezado del pedido
            tk.Label(frame_pedido, 
                    text=f"📝 Pedido {pedido.get('codigo', 'Sin código')} - Mesa: {pedido.get('mesa', 'S/M')}",
                    font=FUENTE_TITULO,
                    bg="white",
                    anchor="w").pack(fill="x")
            
            # Productos
            productos_frame = tk.Frame(frame_pedido, bg="white")
            productos_frame.pack(fill="x", pady=(5, 0))
            
            for item in pedido.get('items', []):
                tk.Label(productos_frame,
                        text=f"  • {item['nombre']} (${item['precio']})",
                        font=FUENTE_PRODUCTOS,
                        bg="white",
                        anchor="w").pack(fill="x")
            
            # Total y botón
            footer_frame = tk.Frame(frame_pedido, bg="white")
            footer_frame.pack(fill="x", pady=(10, 0))
            
            tk.Label(footer_frame,
                    text=f"Total: ${pedido.get('total', 0):.2f}",
                    font=FUENTE_NORMAL,
                    bg="white").pack(side="left")
            
            tk.Button(footer_frame,
                     text="Marcar como Servido",
                     command=lambda p=pedido['id']: marcar_servido(p),
                     bg="#40754C",
                     fg="white",
                     font=FUENTE_NORMAL).pack(side="right")
    
    def marcar_servido(pedido_id):
        if messagebox.askyesno("Confirmar", "¿Marcar este pedido como servido?"):
            try:
                restaurante.marcar_pedido_servido(pedido_id)
                messagebox.showinfo("Éxito", "Pedido marcado como servido")
                mostrar_pedidos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
    
    # Botones de control
    control_frame = tk.Frame(scrollable_frame, bg=FONDO)
    control_frame.pack(fill="x", pady=(20, 10))
    
    tk.Button(control_frame,
             text="🔄 Actualizar Pedidos",
             command=mostrar_pedidos,
             bg=COLOR_ENCABEZADO,
             fg="white",
             font=FUENTE_NORMAL).pack(side="left", padx=5)
    
    tk.Button(control_frame,
             text="🔙 Cerrar Sesión",
             command=lambda: [ventana.destroy(), iniciar_app()],
             bg="#333333",
             fg="white",
             font=FUENTE_NORMAL).pack(side="right", padx=5)
    
    # Mostrar pedidos al iniciar
    mostrar_pedidos()
    
    ventana.mainloop()

def iniciar_app():
    # Función dummy para el cierre de sesión
    pass