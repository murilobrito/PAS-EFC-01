from src.interfaces.order_repository_interface import OrderRepositoryInterface
from src.models.order import Order
from typing import Dict, Any

class OrderService:
    def __init__(self, repository: OrderRepositoryInterface, payment_strategies: Dict[str, Any] = None, item_strategies: Dict[str, Any] = None, order_strategies: Dict[str, Any] = None):
        self.repository = repository
        self.payment_strategies = payment_strategies or {}
        self.item_strategies = item_strategies or {}
        self.order_strategies = order_strategies or {}

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
        
        n = order.cliente
        if order.tipo_pedido == 'especial':
            print(f"Email especial enviado para {n}: Pedido especial recebido!")
            return order_id

        if order.tipo_pedido == 'normal':
            print(f"Email enviado para {n}: Pedido recebido!")
        elif order.tipo_pedido == 'vip':
            print(f"Email enviado para {n}: Pedido recebido!")
            print(f"SMS enviado para {n}: Pedido VIP recebido!")
        elif order.tipo_pedido == 'corporativo':
            print(f"Email enviado para {n}: Pedido recebido!")
            print(f"Notificacao enviada ao gerente de conta de {n}")
            
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
        
        if order_data['tp'] == 'especial':
            print(f"Pedido especial {order_id} > {status}")
            return
            
        cli = order_data['cli']
        tp = order_data['tp']
        tot = order_data['tot']
        
        if status == 'aprovado':
            print(f"Email enviado para {cli}: Pedido aprovado!")
            if tp == 'vip':
                print(f"SMS enviado para {cli}: Pedido aprovado!")
        elif status == 'enviado':
            print(f"Email enviado para {cli}: Pedido enviado")
        elif status == 'entregue':
            print(f"Email enviado para {cli}: Pedido entregue!")
            if tp == 'vip':
                pts = int(tot * 2)
                print(f"Cliente VIP ganhou {pts} pontos!")
            elif tp == 'corporativo':
                pts = int(tot * 1.5)
                print(f"Cliente corporativo ganhou {pts} pontos!")
            else:
                pts = int(tot)
                print(f"Cliente ganhou {pts} pontos!")

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
