import os
import json
import copy
import hashlib

from storage import Storage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # src/main/
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data"))

os.makedirs(DATA_DIR, exist_ok=True)


class DiskReplicaBackend(Storage):

    def _read_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _write_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _replica_path(self, user_id):
        return os.path.join(DATA_DIR, "replicas", user_id, "replica.json")


    def get_full_replica(self, user_id: str) -> dict:
        data = self._read_json(self._replica_path(user_id))
        return copy.deepcopy(data)
    
    def get_full_replica_deep(self, user_id: str) -> dict:
        return self.get_full_replica(user_id=user_id)

    def write_full_replica(self, user_id: str, replica: dict) -> None:
        self._write_json(self._replica_path(user_id), replica)


    def get_items(self, user_id: str) -> dict:
        rep = self._read_json(self._replica_path(user_id))
        return copy.deepcopy(rep.get("recorded_items", {}))

    def write_items(self, user_id: str, items: dict) -> None:
        rep = self._read_json(self._replica_path(user_id))
        rep["recorded_items"] = items
        self._write_json(self._replica_path(user_id), rep)


    def get_requests(self, user_id: str) -> dict:
        rep = self._read_json(self._replica_path(user_id))
        return copy.deepcopy(rep.get("recorded_requests", {}))

    def write_requests(self, user_id: str, recorded_requests: dict) -> None:
        rep = self._read_json(self._replica_path(user_id))
        rep["recorded_requests"] = recorded_requests
        self._write_json(self._replica_path(user_id), rep)


    def get_item(self, user_id: str, iid: str) -> dict:
        rep = self._read_json(self._replica_path(user_id))
        return copy.deepcopy(rep.get("recorded_items", {}).get(iid, {}))

    def write_item(self, user_id: str, item: dict) -> None:
        rep = self._read_json(self._replica_path(user_id))
        rep.setdefault("recorded_items", {})
        rep["recorded_items"][item["iid"]] = item
        self._write_json(self._replica_path(user_id), rep)


    def get_request(self, user_id: str, rrid: str) -> dict:
        rep = self._read_json(self._replica_path(user_id))
        return copy.deepcopy(rep.get("recorded_requests", {}).get(rrid, {}))

    def write_request(self, user_id: str, request: dict) -> None:
        rep = self._read_json(self._replica_path(user_id))
        rep.setdefault("recorded_requests", {})
        rep["recorded_requests"][request["rrid"]] = request
        self._write_json(self._replica_path(user_id), rep)

    def get_known_users(self, user_id) -> dict:
        user_replica = self.get_full_replica(user_id)
        return copy.deepcopy(user_replica.get("known_users", {}))

    def write_known_users(self, user_id, known_id, known_name):
        user_replica = self.get_full_replica(user_id)
        known = user_replica.get("known_users", {})
        known[known_id] = known_name
        user_replica["known_users"] = known
        self.write_full_replica(user_id, user_replica)

    def get_local_users(self):
        path = os.path.join(DATA_DIR, "local_users.json")
        return self._read_json(path)

    def write_local_users(self, local_users):
        path = os.path.join(DATA_DIR, "local_users.json")
        self._write_json(path, local_users)

    def get_user_password_hash(self, user_id):
        users = self.get_local_users()
        if user_id not in users:
            print(f"[DiskBackend] User {user_id} not found")
            return None
        return users[user_id]["password_hash"]

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
