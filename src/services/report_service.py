from src.interfaces.order_repository_interface import OrderRepositoryInterface

class ReportService:
    def __init__(self, repository: OrderRepositoryInterface):
        self.repository = repository

    def generate_sales_report(self):
        rs = self.repository.get_all()
        print("=== RELATORIO DE VENDAS ===")
        tot_g = 0
        for r in rs:
            # {r[0]} - Cliente: {r[1]} -  Total: R${r[3]:.2f} - Status: {r[4]} - legacy had weird spaces?
            # legacy: print(f"Pedido #{r[0]} Cliente: {r[1]} Total: R${r[3]:.2f} Status: {r[4]}")
            print(f"Pedido #{r[0]} Cliente: {r[1]} Total: R${r[3]:.2f} Status: {r[4]}")
            tot_g += r[3]
        print(f"Total Geral: R${tot_g:.2f}")
        with open('rel_vendas.txt', 'w') as f:
            f.write(f"Total de vendas: {tot_g}")

    def generate_clients_report(self):
        rs = self.repository.get_all_clients_and_types()
        print("=== RELATORIO DE CLIENTES ===")
        for r in rs:
            n = r[0]
            tp = r[1]
            tot = self.repository.get_total_by_client(n)
            print(f"Cliente: {n} ({tp}) Total gasto: R${tot:.2f}")
        with open('rel_clientes.txt', 'w') as f:
            for r in rs:
                f.write(f"{r[0]}, {r[1]}\n")
