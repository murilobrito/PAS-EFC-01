from datetime import datetime
from typing import List, Optional
from src.models.item import Item

class Order:
    def __init__(self, cliente: str, tipo_pedido: str) -> None:
        self.id: Optional[int] = None
        self.cliente: str = cliente
        self.tipo_pedido: str = tipo_pedido
        self.itens: List[Item] = []
        self.status: str = 'pendente'
        self.data: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.total: float = 0.0

    def add_item(self, item: Item) -> None:
        self.itens.append(item)
