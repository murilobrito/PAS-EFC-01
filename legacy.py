from src.repositories.sqlite_order_repository import SQLiteOrderRepository
from src.services.order_service import OrderService
from src.services.report_service import ReportService
from src.models.item import Item
from src.models.order import Order

class Sis:
    def __init__(self):
        self.repo = SQLiteOrderRepository('loja.db')
        self.order_service = OrderService(self.repo)
        self.report_service = ReportService(self.repo)

    def add_ped(self, n, its, t):
        order = Order(n, t)
        for i in its:
            order.add_item(Item(i['nome'], i['p'], i['q'], i.get('tipo', 'normal')))
        return self.order_service.create_order(order, is_special=False)

    def get_ped(self, id):
        return self.repo.get(id)

    def upd_st(self, id, s):
        self.order_service.update_status(id, s, is_special=False)

    def calc_tot_cli(self, n):
        return self.repo.get_total_by_client(n)

    def gerar_rel(self, tipo):
        if tipo == 'vendas':
            self.report_service.generate_sales_report()
        elif tipo == 'clientes':
            self.report_service.generate_clients_report()

    def proc_pag(self, id, m, vl):
        return self.order_service.process_payment(id, m, vl)

    def validar_estoque(self, its):
        return self.order_service.validate_stock(its)

    def cancelar_pedido(self, id):
        self.order_service.cancel_order(id)

    def close(self):
        self.repo.close()

class PedEspecial(Sis):
    def add_ped(self, n, its, t):
        order = Order(n, t)
        for i in its:
            order.add_item(Item(i['nome'], i['p'], i['q'], i.get('tipo', 'normal')))
        return self.order_service.create_order(order, is_special=True)

    def upd_st(self, id, s):
        self.order_service.update_status(id, s, is_special=True)

def main():
    pass

if __name__ == '__main__':
    main()