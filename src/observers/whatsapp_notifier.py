from typing import Dict, Any
from src.observers.notification_observer import OrderObserver

class WhatsAppNotifier(OrderObserver):
    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        cliente = order_data['cli']
        if event_type == 'created':
            print(f"WhatsApp enviado para {cliente}: Pedido recebido!")
        elif event_type == 'status_updated':
            status = order_data.get('status')
            if status in ('aprovado', 'enviado', 'entregue'):
                msg = status if status != 'enviado' else 'enviado'
                print(f"WhatsApp enviado para {cliente}: Pedido {msg}!")
