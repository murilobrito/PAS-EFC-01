from src.strategies.discount_strategy import ItemDiscountStrategy

class VolumeDiscountDecorator(ItemDiscountStrategy):
    def __init__(self, base_strategy: ItemDiscountStrategy) -> None:
        self.base_strategy = base_strategy
    
    def calculate(self, preco: float, quantidade: int) -> float:
        base_tot = self.base_strategy.calculate(preco, quantidade)
        if quantidade >= 3:
            return base_tot * 0.85
        return base_tot
