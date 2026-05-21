from abc import ABC, abstractmethod

class Storage(ABC):

    @abstractmethod
    def get_full_replica(self, user_id: str) -> dict:
        pass

    @abstractmethod
    def write_full_replica(self, user_id: str, replica: dict) -> None:
        pass

    @abstractmethod
    def get_items(self, user_id: str) -> dict:
        pass

    @abstractmethod
    def write_items(self, user_id: str, expenses: dict) -> None:
        pass

    @abstractmethod
    def get_requests(self, user_id: str) -> dict:
        pass

    @abstractmethod
    def write_requests(self, user_id: str, groups: dict) -> None:
        pass

    @abstractmethod
    def get_item(self, user_id: str, eid: str) -> dict:
        pass

    @abstractmethod
    def write_item(self, user_id: str, expense: dict) -> None:
        pass

    @abstractmethod
    def get_request(self, user_id: str, gid: str) -> dict:
        pass

    @abstractmethod
    def write_request(self, user_id: str, group: dict) -> None:
        pass
