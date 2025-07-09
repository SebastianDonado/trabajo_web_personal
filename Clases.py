from Conexion_fb import db

class Producto:
    def __init__(self, codigo, nombre, precio, categoria="", subcategoria="", imagen=""):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.imagen = imagen

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} - ${self.precio}"

class Pedido:
    def __init__(self, mesa=""):
        self.items = []
        self.total = 0
        self.estado = "pendiente"
        self.mesa = mesa

    def agregar_producto(self, producto):
        self.items.append(producto)
        self.total += producto.precio

    def a_dict(self):
        return {
            "items": [vars(p) for p in self.items],
            "total": self.total,
            "estado": self.estado,
            "mesa": self.mesa
        }

class Restaurante:
    def __init__(self, db):
        self.db = db

    def obtener_menu(self):
        productos = []
        docs = self.db.collection("menu").stream()
        for doc in docs:
            data = doc.to_dict()
            producto = Producto(
                data.get("codigo", ""),
                data.get("nombre", ""),
                data.get("precio", 0),
                data.get("categoria", ""),
                data.get("subcategoria", ""),
                data.get("imagen", "")
            )
            productos.append(producto)
        return productos

    def enviar_pedido(self, pedido):
        self.db.collection("pedidos").add(pedido.a_dict())

    def obtener_pedidos_pendientes(self):
        pedidos = []
        try:
            docs = self.db.collection("pedidos").where("estado", "==", "pendiente").stream()
            for doc in docs:
                pedido = doc.to_dict()
                pedido["id"] = doc.id
                pedidos.append(pedido)
        except Exception as e:
            print(f"Error al obtener pedidos: {e}")
        return pedidos

    def marcar_pedido_servido(self, pedido_id):
        self.db.collection("pedidos").document(pedido_id).update({
            "estado": "servido"
        })

    def obtener_pedido_por_id(self, pedido_id):
        doc = self.db.collection("pedidos").document(pedido_id).get()
        if doc.exists:
            pedido = doc.to_dict()
            pedido["id"] = pedido_id
            return pedido
        return None
