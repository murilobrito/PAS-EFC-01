from abc import ABC, abstractmethod
from typing import Optional, Tuple

class PaymentStrategy(ABC):
    @abstractmethod
    def process(self, value: float, total: float) -> Tuple[bool, Optional[str]]:
        pass

class CartaoStrategy(PaymentStrategy):
    def process(self, value: float, total: float) -> Tuple[bool, Optional[str]]:
        if value < total:
            print("Valor insuficiente!")
            return False, None
        print("Processando pagamento com cartao...")
        print("Cartao validado!")
        return True, 'aprovado'

class PixStrategy(PaymentStrategy):
    def process(self, value: float, total: float) -> Tuple[bool, Optional[str]]:
        if value < total:
            print("Valor insuficiente!")
            return False, None
        print("Gerando QR Code PIX...")
        print("PIX recebido!")
        return True, 'aprovado'

class BoletoStrategy(PaymentStrategy):
    def process(self, value: float, total: float) -> Tuple[bool, Optional[str]]:
        if value < total:
            print("Valor insuficiente!")
            return False, None
        print("Gerando boleto...")
        print("Boleto gerado!")
        return True, None
