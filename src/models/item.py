class Item:
    def __init__(self, nome: str, preco: float, quantidade: int, tipo: str = 'normal') -> None:
        self.nome: str = nome
        self.preco: float = preco
        self.quantidade: int = quantidade
        self.tipo: str = tipo

    def get_subtotal_base(self) -> float:
        return self.preco * self.quantidade
