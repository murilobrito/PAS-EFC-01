from abc import ABC, abstractmethod

class OrderRepositoryInterface(ABC):
    @abstractmethod
    def save(self, order) -> int:
        pass

    @abstractmethod
    def get(self, order_id):
        pass

    @abstractmethod
    def update_status(self, order_id: int, status: str):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_all_clients_and_types(self):
        pass

    @abstractmethod
    def get_total_by_client(self, client: str) -> float:
        pass
