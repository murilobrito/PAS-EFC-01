from typing import Optional, Tuple
from src.strategies.payment_strategy import PaymentStrategy

class CriptoStrategy(PaymentStrategy):
    def process(self, value: float, total: float) -> Tuple[bool, Optional[str]]:
        total_com_taxa = total * 1.02
        if value < total_com_taxa:
            print("Valor insuficiente para cobrir a taxa de criptomoeda!")
            return False, None
        print("Gerando endereco de Criptomoeda...")
        print("Criptomoeda recebida!")
        return True, 'aprovado'
