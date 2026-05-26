from abc import ABC, abstractmethod
from typing import Optional

class PaymentStrategy(ABC):
    @abstractmethod
    def process(self) -> Optional[str]:
        pass

class CartaoStrategy(PaymentStrategy):
    def process(self) -> Optional[str]:
        print("Processando pagamento com cartao...")
        print("Cartao validado!")
        return 'aprovado'

class PixStrategy(PaymentStrategy):
    def process(self) -> Optional[str]:
        print("Gerando QR Code PIX...")
        print("PIX recebido!")
        return 'aprovado'

class BoletoStrategy(PaymentStrategy):
    def process(self) -> Optional[str]:
        print("Gerando boleto...")
        print("Boleto gerado!")
        return None
