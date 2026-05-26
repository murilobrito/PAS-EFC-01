from src.interfaces.order_repository_interface import OrderRepositoryInterface
from src.models.order import Order
from typing import Dict, Any

class OrderService:
    def __init__(self, repository: OrderRepositoryInterface, payment_strategies: Dict[str, Any] = None, item_strategies: Dict[str, Any] = None, order_strategies: Dict[str, Any] = None):
        self.repository = repository
        self.payment_strategies = payment_strategies or {}
        self.item_strategies = item_strategies or {}
        self.order_strategies = order_strategies or {}
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def _notify(self, event_type: str, order_data: Dict[str, Any]):
        for obs in self.observers:
            obs.update(event_type, order_data)

    def calculate_total(self, order: Order):
        tot = 0.0
        for i in order.itens:
            if i.tipo in self.item_strategies:
                tot += self.item_strategies[i.tipo].calculate(i.preco, i.quantidade)
            else:
                tot += i.preco * i.quantidade
        
        if order.tipo_pedido in self.order_strategies:
            tot = self.order_strategies[order.tipo_pedido].calculate(tot)
        
        order.total = tot
        return tot

    def create_order(self, order: Order) -> int:
        self.calculate_total(order)
        order_id = self.repository.save(order)
        
        order_data = {'id': order_id, 'cli': order.cliente, 'tp': order.tipo_pedido, 'tot': order.total, 'status': 'pendente'}
        self._notify('created', order_data)
        return order_id

    def process_payment(self, order_id: int, method: str, value: float) -> bool:
        order_data = self.repository.get(order_id)
        if not order_data:
            return False
            
        if value < order_data['tot']:
            print("Valor insuficiente!")
            return False

        if method not in self.payment_strategies:
            print("Metodo de pagamento invalido!")
            return False

        strategy = self.payment_strategies[method]
        new_status = strategy.process()
        if new_status:
            self.update_status(order_id, new_status)
        return True

    def update_status(self, order_id: int, status: str):
        order_data = self.repository.get(order_id)
        if not order_data:
            return
            
        self.repository.update_status(order_id, status)
        order_data['status'] = status
        
        self._notify('status_updated', order_data)

    def validate_stock(self, items: list) -> bool:
        est = {'produto1': 100, 'produto2': 50, 'produto3': 75}
        for i in items:
            if i['nome'] not in est:
                print(f"Produto {i['nome']} nao encontrado!")
                return False
            if est[i['nome']] < i['q']:
                print(f"Estoque insuficiente para {i['nome']}!")
                return False
        return True

    def cancel_order(self, order_id: int):
        self.repository.update_status(order_id, 'cancelado')
        print(f"Pedido {order_id} cancelado")
