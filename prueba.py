import os
from PIL import Image, ImageTk

# Ruta base para imágenes
ruta_base_imagenes = os.path.join(os.getcwd(), "imagenes_productos")

try:
    ruta_imagen = os.path.join(ruta_base_imagenes, prod.imagen)
    print(f"Buscando imagen en: {ruta_imagen}")
    img = Image.open(ruta_imagen)
    img = img.resize((80, 80), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    label_img = tk.Label(frame, image=img_tk, bg=FONDO)
    label_img.image = img_tk  # prevenir garbage collection
    label_img.pack(side="left", padx=5)
except Exception as e:
    print(f"❌ Error cargando imagen {ruta_imagen}: {e}")
