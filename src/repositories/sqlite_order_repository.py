import sqlite3
import json
from src.interfaces.order_repository_interface import OrderRepositoryInterface

class SQLiteOrderRepository(OrderRepositoryInterface):
    def __init__(self, db_path='loja.db'):
        self.db = sqlite3.connect(db_path)
        self.c = self.db.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS ped (
            id INTEGER PRIMARY KEY, cli TEXT, itens TEXT,
            tot REAL, st TEXT, dt TEXT, tp TEXT)''')
        self.db.commit()

    def save(self, order) -> int:
        itens_dicts = [{'nome': i.nome, 'p': i.preco, 'q': i.quantidade, 'tipo': i.tipo} for i in order.itens]
        its_str = json.dumps(itens_dicts)
        self.c.execute("INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)",
                       (order.cliente, its_str, order.total, order.status, order.data, order.tipo_pedido))
        self.db.commit()
        order.id = self.c.lastrowid
        return order.id

    def get(self, order_id):
        self.c.execute("SELECT * FROM ped WHERE id=?", (order_id,))
        r = self.c.fetchone()
        if r:
            # Para o Golden Master funcionar no Sis facade, podemos retornar um dicionário ou um Order
            # Vamos retornar um dicionario cru para o facade remontar se precisar, ou retornar Order.
            # O mais limpo e OO é retornar um Order reconstruido ou os dados brutos.
            # Vamos retornar os dados brutos como dicionario aqui para facilitar o refactoring iterativo
            return {'id': r[0], 'cli': r[1], 'itens': json.loads(r[2]),
                    'tot': r[3], 'st': r[4], 'dt': r[5], 'tp': r[6]}
        return None

    def update_status(self, order_id: int, status: str):
        self.c.execute("UPDATE ped SET st=? WHERE id=?", (status, order_id))
        self.db.commit()

    def get_all(self):
        self.c.execute("SELECT * FROM ped")
        return self.c.fetchall()

    def get_all_clients_and_types(self):
        self.c.execute("SELECT DISTINCT cli, tp FROM ped")
        return self.c.fetchall()

    def get_total_by_client(self, client: str) -> float:
        self.c.execute("SELECT * FROM ped WHERE cli=?", (client,))
        rs = self.c.fetchall()
        t = 0.0
        for r in rs:
            t += r[3]
        return t

    def close(self):
        self.db.close()
