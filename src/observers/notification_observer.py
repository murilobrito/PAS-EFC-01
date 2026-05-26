from abc import ABC, abstractmethod
from typing import Dict, Any

class OrderObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, order_data: Dict[str, Any]):
        pass

class EmailNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]):
        cliente = order_data['cli']
        tp = order_data['tp']
        if event_type == 'created':
            if tp == 'especial':
                print(f"Email especial enviado para {cliente}: Pedido especial recebido!")
            else:
                print(f"Email enviado para {cliente}: Pedido recebido!")
        elif event_type == 'status_updated':
            if tp == 'especial':
                return
            status = order_data['status']
            if status == 'aprovado':
                print(f"Email enviado para {cliente}: Pedido aprovado!")
            elif status == 'enviado':
                print(f"Email enviado para {cliente}: Pedido enviado")
            elif status == 'entregue':
                print(f"Email enviado para {cliente}: Pedido entregue!")

class SMSNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]):
        cliente = order_data['cli']
        tp = order_data['tp']
        if tp == 'vip':
            if event_type == 'created':
                print(f"SMS enviado para {cliente}: Pedido VIP recebido!")
            elif event_type == 'status_updated' and order_data.get('status') == 'aprovado':
                print(f"SMS enviado para {cliente}: Pedido aprovado!")

class AccountManagerNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]):
        if event_type == 'created' and order_data['tp'] == 'corporativo':
            print(f"Notificacao enviada ao gerente de conta de {order_data['cli']}")

class PointsNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]):
        if event_type == 'status_updated' and order_data.get('status') == 'entregue':
            tp = order_data['tp']
            tot = order_data['tot']
            if tp == 'vip':
                pts = int(tot * 2)
                print(f"Cliente VIP ganhou {pts} pontos!")
            elif tp == 'corporativo':
                pts = int(tot * 1.5)
                print(f"Cliente corporativo ganhou {pts} pontos!")
            elif tp != 'especial':
                pts = int(tot)
                print(f"Cliente ganhou {pts} pontos!")

class EspecialNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]):
        if event_type == 'status_updated' and order_data['tp'] == 'especial':
            print(f"Pedido especial {order_data['id']} > {order_data['status']}")
