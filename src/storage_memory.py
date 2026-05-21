import copy
import hashlib
from storage import Storage


class MemoryReplicaBackend(Storage):

    def __init__(self):
        self._replicas = {}
        self._local_users = {}

    def _ensure_replica(self, user_id):
        if user_id not in self._replicas:
            self._replicas[user_id] = {
                "recorded_items": {},
                "recorded_requests": {},
                "known_users": {}
            }

    def get_full_replica(self, user_id: str) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]

    def get_full_replica_deep(self, user_id: str) -> dict:
        self._ensure_replica(user_id)
        return copy.deepcopy(self._replicas[user_id])

    def write_full_replica(self, user_id: str, replica: dict) -> None:
        self._ensure_replica(user_id)
        self._replicas[user_id] = replica

    def get_items(self, user_id: str) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]["recorded_items"]

    def write_items(self, user_id: str, items: dict) -> None:
        self._ensure_replica(user_id)
        self._replicas[user_id]["recorded_items"] = items

    def get_requests(self, user_id: str) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]["recorded_requests"]

    def write_requests(self, user_id: str, recorded_requests: dict) -> None:
        self._ensure_replica(user_id)
        self._replicas[user_id]["recorded_requests"] = recorded_requests

    def get_item(self, user_id: str, iid: str) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]["recorded_items"].get(iid, {})

    def write_item(self, user_id: str, item: dict) -> None:
        self._ensure_replica(user_id)
        self._replicas[user_id].setdefault("recorded_items", {})
        self._replicas[user_id]["recorded_items"][item["iid"]] = item

    def get_request(self, user_id: str, rrid: str) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]["recorded_requests"].get(rrid, {})

    def write_request(self, user_id: str, request: dict) -> None:
        self._ensure_replica(user_id)
        self._replicas[user_id].setdefault("recorded_requests", {})
        self._replicas[user_id]["recorded_requests"][request["rrid"]] = request

    def get_known_users(self, user_id) -> dict:
        self._ensure_replica(user_id)
        return self._replicas[user_id]["known_users"]

    def write_known_users(self, user_id, known_id, known_name):
        self._ensure_replica(user_id)
        self._replicas[user_id].setdefault("known_users", {})
        self._replicas[user_id]["known_users"][known_id] = known_name

    def get_local_users(self):
        return self._local_users

    def write_local_users(self, local_users):
        self._local_users = local_users

    def get_user_password_hash(self, user_id):
        if user_id not in self._local_users:
            print(f"[MemoryBackend] User {user_id} not found")
            return None
        return self._local_users[user_id]["password_hash"]

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()