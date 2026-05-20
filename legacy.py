import sqlite3
import json
from datetime import datetime

class Sis:
    def __init__(self):
        self.db = sqlite3.connect('loja.db')
        self.c = self.db.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS ped (
            id INTEGER PRIMARY KEY, cli TEXT, itens TEXT,
            tot REAL, st TEXT, dt TEXT, tp TEXT)''')
        self.db.commit()

    def add_ped(self, n, its, t):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tot = 0
        for i in its:
            if i['tipo'] == 'normal':
                tot += i['p'] * i['q']
            elif i['tipo'] == 'desc10':
                tot += i['p'] * i['q'] * 0.9
            elif i['tipo'] == 'desc20':
                tot += i['p'] * i['q'] * 0.8
            elif i['tipo'] == 'frete_gratis':
                tot += i['p'] * i['q']

        if t == 'vip':
            tot = tot * 0.95
        elif t == 'corporativo':
            tot = tot * 0.90

        its_str = json.dumps(its)
        self.c.execute("INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)",
                       (n, its_str, tot, 'pendente', dt, t))
        self.db.commit()

        if t == 'normal':
            print(f"Email enviado para {n}: Pedido recebido!")
        elif t == 'vip':
            print(f"Email enviado para {n}: Pedido recebido!")
            print(f"SMS enviado para {n}: Pedido VIP recebido!")
        elif t == 'corporativo':
            print(f"Email enviado para {n}: Pedido recebido!")
            print(f"Notificacao enviada ao gerente de conta de {n}")
        return self.c.lastrowid

    def get_ped(self, id):
        self.c.execute("SELECT * FROM ped WHERE id=?", (id,))
        r = self.c.fetchone()
        if r:
            return {'id': r[0], 'cli': r[1], 'itens': json.loads(r[2]),
                    'tot': r[3], 'st': r[4], 'dt': r[5], 'tp': r[6]}
        return None

    def upd_st(self, id, s):
        p = self.get_ped(id)
        if p:
            self.c.execute("UPDATE ped SET st=? WHERE id=?", (s, id))
            self.db.commit()
            if s == 'aprovado':
                print(f"Email enviado para {p['cli']}: Pedido aprovado!")
                if p['tp'] == 'vip':
                    print(f"SMS enviado para {p['cli']}: Pedido aprovado!")
            elif s == 'enviado':
                print(f"Email enviado para {p['cli']}: Pedido enviado")
            elif s == 'entregue':
                print(f"Email enviado para {p['cli']}: Pedido entregue!")
                if p['tp'] == 'vip':
                    pts = int(p['tot'] * 2)
                    print(f"Cliente VIP ganhou {pts} pontos!")
                elif p['tp'] == 'corporativo':
                    pts = int(p['tot'] * 1.5)
                    print(f"Cliente corporativo ganhou {pts} pontos!")
                else:
                    pts = int(p['tot'])
                    print(f"Cliente ganhou {pts} pontos!")

    def calc_tot_cli(self, n):
        self.c.execute("SELECT * FROM ped WHERE cli=?", (n,))
        rs = self.c.fetchall()
        t = 0
        for r in rs:
            t += r[3]
        return t

    def gerar_rel(self, tipo):
        if tipo == 'vendas':
            self.c.execute("SELECT * FROM ped")
            rs = self.c.fetchall()
            print("=== RELATORIO DE VENDAS ===")
            tot_g = 0
            for r in rs:
                print(f"Pedido #{r[0]} Cliente: {r[1]} Total: R${r[3]:.2f} Status: {r[4]}")
                tot_g += r[3]
            print(f"Total Geral: R${tot_g:.2f}")
            with open('rel_vendas.txt', 'w') as f:
                f.write(f"Total de vendas: {tot_g}")
        elif tipo == 'clientes':
            self.c.execute("SELECT DISTINCT cli, tp FROM ped")
            rs = self.c.fetchall()
            print("=== RELATORIO DE CLIENTES ===")
            for r in rs:
                n = r[0]
                tp = r[1]
                tot = self.calc_tot_cli(n)
                print(f"Cliente: {n} ({tp}) Total gasto: R${tot:.2f}")
            with open('rel_clientes.txt', 'w') as f:
                for r in rs:
                    f.write(f"{r[0]}, {r[1]}\n")

    def proc_pag(self, id, m, vl):
        p = self.get_ped(id)
        if not p:
            return False
        if vl < p['tot']:
            print("Valor insuficiente!")
            return False

        if m == 'cartao':
            print("Processando pagamento com cartao...")
            print("Cartao validado!")
            self.upd_st(id, 'aprovado')
            return True
        elif m == 'pix':
            print("Gerando QR Code PIX...")
            print("PIX recebido!")
            self.upd_st(id, 'aprovado')
            return True
        elif m == 'boleto':
            print("Gerando boleto...")
            print("Boleto gerado!")
            return True
        else:
            print("Metodo de pagamento invalido!")
            return False

    def validar_estoque(self, its):
        est = {'produto1': 100, 'produto2': 50, 'produto3': 75}
        for i in its:
            if i['nome'] not in est:
                print(f"Produto {i['nome']} nao encontrado!")
                return False
            if est[i['nome']] < i['q']:
                print(f"Estoque insuficiente para {i['nome']}!")
                return False
        return True

    def cancelar_pedido(self, id):
        self.c.execute("UPDATE ped SET st=? WHERE id=?", ('cancelado', id))
        self.db.commit()
        print(f"Pedido {id} cancelado")

    def close(self):
        self.db.close()

class PedEspecial(Sis):
    def add_ped(self, n, its, t):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tot = 0
        for i in its:
            if i['tipo'] == 'normal':
                tot += i['p'] * i['q']
            elif i['tipo'] == 'desc10':
                tot += i['p'] * i['q'] * 0.9
            elif i['tipo'] == 'desc20':
                tot += i['p'] * i['q'] * 0.8
        tot = tot * 1.15
        its_str = json.dumps(its)
        self.c.execute("INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)",
                       (n, its_str, tot, 'pendente', dt, t))
        self.db.commit()
        print(f"Email especial enviado para {n}: Pedido especial recebido!")
        return self.c.lastrowid

    def upd_st(self, id, s):
        p = self.get_ped(id)
        if p:
            self.c.execute("UPDATE ped SET st=? WHERE id=?", (s, id))
            self.db.commit()
            print(f"Pedido especial {id} > {s}")

def main():
    s = Sis()
    its1 = [{'nome': 'produto1', 'p': 100, 'q': 2, 'tipo': 'normal'},
            {'nome': 'produto2', 'p': 50, 'q': 1, 'tipo': 'desc10'}]
    if s.validar_estoque(its1):
        id1 = s.add_ped('Joao Silva', its1, 'normal')
        print(f"Pedido {id1} criado!")
        s.proc_pag(id1, 'cartao', 250)
        s.upd_st(id1, 'enviado')
        s.upd_st(id1, 'entregue')

    its2 = [{'nome': 'produto3', 'p': 200, 'q': 1, 'tipo': 'desc20'}]
    if s.validar_estoque(its2):
        id2 = s.add_ped('Maria Santos', its2, 'vip')
        s.proc_pag(id2, 'pix', 160)

    its3 = [{'nome': 'produto1', 'p': 100, 'q': 5, 'tipo': 'normal'}]
    if s.validar_estoque(its3):
        id3 = s.add_ped('Empresa XYZ', its3, 'corporativo')
        s.proc_pag(id3, 'boleto', 500)

    s.gerar_rel('vendas')
    print()
    s.gerar_rel('clientes')
    s.close()

if __name__ == '__main__':
    main()