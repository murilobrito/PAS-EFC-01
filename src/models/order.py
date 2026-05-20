from datetime import datetime

class Order:
    def __init__(self, cliente, tipo_pedido):
        self.id = None
        self.cliente = cliente
        self.tipo_pedido = tipo_pedido
        self.itens = []
        self.status = 'pendente'
        self.data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.total = 0.0

    def add_item(self, item):
        self.itens.append(item)
