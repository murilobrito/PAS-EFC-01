class Item:
    def __init__(self, nome, preco, quantidade, tipo='normal'):
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
        self.tipo = tipo

    def get_subtotal_base(self):
        return self.preco * self.quantidade
