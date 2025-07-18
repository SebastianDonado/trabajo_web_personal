from Conexion_fb import db

class Producto:
    def __init__(self, codigo, nombre, precio, categoria="", subcategoria="", imagen="", unidades=0):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.imagen = imagen
        self.unidades = unidades

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} - ${self.precio} ({self.unidades} unidades)"

    def a_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio": self.precio,
            "categoria": self.categoria,
            "subcategoria": self.subcategoria,
            "imagen": self.imagen,
            "unidades": self.unidades
        }

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
            "codigo": self.codigo,  # ✅ Corrección aplicada aquí
            "items": [vars(p) for p in self.items],
            "total": self.total,
            "estado": self.estado,
            "mesa": self.mesa
        }

    def generar_codigo(self, restaurante):
        pedidos = restaurante.db.collection("pedidos").get()
        codigos = [p.to_dict().get("codigo", "") for p in pedidos if "codigo" in p.to_dict()]
        numeros = [int(cod[1:]) for cod in codigos if cod.startswith("P") and cod[1:].isdigit()]
        siguiente_numero = max(numeros) + 1 if numeros else 1
        self.codigo = f"P{siguiente_numero}"

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
                data.get("imagen", ""),
                data.get("unidades", 0)
            )
            productos.append(producto)
        return productos

    def obtener_inventario(self):
        productos_inventario = []
        try:
            docs = self.db.collection("menu").stream()
            for doc in docs:
                data = doc.to_dict()
                producto = Producto(
                    data.get("codigo", ""),
                    data.get("nombre", ""),
                    data.get("precio", 0),
                    data.get("categoria", ""),
                    data.get("subcategoria", ""),
                    data.get("imagen", ""),
                    data.get("unidades", 0)
                )
                productos_inventario.append(producto)
            return productos_inventario
        except Exception as e:
            print(f"Error al obtener el inventario: {e}")
            return []

    def actualizar_unidades_producto(self, codigo_producto, nuevas_unidades):
        try:
            docs = self.db.collection("menu").where("codigo", "==", codigo_producto).limit(1).get()
            if len(docs) > 0:
                doc_id = docs[0].id
                self.db.collection("menu").document(doc_id).update({"unidades": nuevas_unidades})
                print(f"Unidades del producto '{codigo_producto}' actualizadas a {nuevas_unidades}.")
                return True
            else:
                print(f"Producto con código '{codigo_producto}' no encontrado para actualizar unidades.")
                return False
        except Exception as e:
            print(f"Error al actualizar unidades del producto: {e}")
            return False

    def obtener_producto_por_codigo(self, codigo_producto):
        try:
            docs = self.db.collection("menu").where("codigo", "==", codigo_producto).limit(1).get()
            if len(docs) > 0:
                data = docs[0].to_dict()
                return Producto(
                    data.get("codigo", ""),
                    data.get("nombre", ""),
                    data.get("precio", 0),
                    data.get("categoria", ""),
                    data.get("subcategoria", ""),
                    data.get("imagen", ""),
                    data.get("unidades", 0)
                )
            return None
        except Exception as e:
            print(f"Error al obtener producto por código: {e}")
            return None

    def agregar_producto_menu(self, producto):
        try:
            self.db.collection("menu").add(producto.a_dict())
            return True
        except Exception as e:
            print(f"Error al agregar producto al menú: {e}")
            return False

    def actualizar_producto_menu(self, producto):
        try:
            docs = self.db.collection("menu").where("codigo", "==", producto.codigo).limit(1).get()
            if len(docs) > 0:
                doc_id = docs[0].id
                self.db.collection("menu").document(doc_id).update(producto.a_dict())
                return True
            else:
                print(f"Producto con código '{producto.codigo}' no encontrado para actualizar el menú.")
                return False
        except Exception as e:
            print(f"Error al actualizar producto en el menú: {e}")
            return False

    def eliminar_producto_menu(self, codigo_producto):
        try:
            docs = self.db.collection("menu").where("codigo", "==", codigo_producto).limit(1).get()
            if len(docs) > 0:
                doc_id = docs[0].id
                self.db.collection("menu").document(doc_id).delete()
                return True
            else:
                print(f"Producto con código '{codigo_producto}' no encontrado para eliminar del menú.")
                return False
        except Exception as e:
            print(f"Error al eliminar producto del menú: {e}")
            return False

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

    def existe_pedido_mesa(self, mesa):
        try:
            docs = (
                self.db.collection("pedidos")
                .where(filter=("mesa", "==", mesa))
                .where(filter=("estado", "==", "pendiente"))
                .limit(1)
                .get()
            )
            return len(docs) > 0
        except Exception as e:
            print(f"Error al verificar pedido para la mesa {mesa}: {e}")
            return False
