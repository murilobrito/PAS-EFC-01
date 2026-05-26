from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from src.models.order import Order

class OrderRepositoryInterface(ABC):
    @abstractmethod
    def save(self, order: Order) -> int:
        pass

    @abstractmethod
    def get(self, order_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_status(self, order_id: int, status: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def get_all_clients_and_types(self) -> List[Tuple[Any, ...]]:
        pass

    @abstractmethod
    def get_total_by_client(self, client: str) -> float:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
