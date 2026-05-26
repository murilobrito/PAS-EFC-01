from abc import ABC, abstractmethod

class ItemDiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, preco: float, quantidade: int) -> float:
        pass

class NormalItemStrategy(ItemDiscountStrategy):
    def calculate(self, preco: float, quantidade: int) -> float:
        return preco * quantidade

class Desc10ItemStrategy(ItemDiscountStrategy):
    def calculate(self, preco: float, quantidade: int) -> float:
        return preco * quantidade * 0.9

class Desc20ItemStrategy(ItemDiscountStrategy):
    def calculate(self, preco: float, quantidade: int) -> float:
        return preco * quantidade * 0.8

class FreteGratisItemStrategy(ItemDiscountStrategy):
    def calculate(self, preco: float, quantidade: int) -> float:
        return preco * quantidade

class OrderDiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float) -> float:
        pass

class NormalOrderStrategy(OrderDiscountStrategy):
    def calculate(self, total: float) -> float:
        return total

class VipOrderStrategy(OrderDiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 0.95

class CorpOrderStrategy(OrderDiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 0.90

class EspecialOrderStrategy(OrderDiscountStrategy):
    def calculate(self, total: float) -> float:
        return total * 1.15
