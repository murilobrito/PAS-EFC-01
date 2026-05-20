from src.interfaces.order_repository_interface import OrderRepositoryInterface
from src.models.order import Order

class OrderService:
    def __init__(self, repository: OrderRepositoryInterface):
        self.repository = repository

    def calculate_total(self, order: Order, apply_ped_especial_rule: bool = False):
        tot = 0.0
        for i in order.itens:
            if i.tipo == 'normal':
                tot += i.preco * i.quantidade
            elif i.tipo == 'desc10':
                tot += i.preco * i.quantidade * 0.9
            elif i.tipo == 'desc20':
                tot += i.preco * i.quantidade * 0.8
            elif i.tipo == 'frete_gratis':
                tot += i.preco * i.quantidade
        
        if apply_ped_especial_rule:
            tot = tot * 1.15
        else:
            if order.tipo_pedido == 'vip':
                tot *= 0.95
            elif order.tipo_pedido == 'corporativo':
                tot *= 0.90
        
        order.total = tot
        return tot

    def create_order(self, order: Order, is_special: bool = False) -> int:
        self.calculate_total(order, apply_ped_especial_rule=is_special)
        order_id = self.repository.save(order)
        
        n = order.cliente
        if is_special:
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

        if method == 'cartao':
            print("Processando pagamento com cartao...")
            print("Cartao validado!")
            self.update_status(order_id, 'aprovado')
            return True
        elif method == 'pix':
            print("Gerando QR Code PIX...")
            print("PIX recebido!")
            self.update_status(order_id, 'aprovado')
            return True
        elif method == 'boleto':
            print("Gerando boleto...")
            print("Boleto gerado!")
            return True
        else:
            print("Metodo de pagamento invalido!")
            return False

    def update_status(self, order_id: int, status: str, is_special: bool = False):
        order_data = self.repository.get(order_id)
        if not order_data:
            return
            
        self.repository.update_status(order_id, status)
        
        if is_special:
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
