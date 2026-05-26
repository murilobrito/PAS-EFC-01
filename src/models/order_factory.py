from src.models.order import Order
from src.models.item import Item
from typing import List, Dict, Any

class OrderFactory:
    @staticmethod
    def create(cliente: str, itens_dict: List[Dict[str, Any]], tipo_pedido: str) -> Order:
        order = Order(cliente, tipo_pedido)
        for i in itens_dict:
            order.add_item(Item(i['nome'], i['p'], i['q'], i.get('tipo', 'normal')))
        return order
