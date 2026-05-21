import json
from network_handler import UDPNetworkHandler, NetworkMessage, MessageType
import sys, threading
from storage_provider import get_backend

print_lock = threading.Lock()


class ReplicaSync:
    network_handler: UDPNetworkHandler = None
    user_id: str = None

    @staticmethod
    def safe_print(*args, **kwargs):
        with print_lock:
            print(*args, **kwargs)

    @staticmethod
    def start_listener(user_id: str, host="127.0.0.1", port=0):
        if ReplicaSync.network_handler:
            ReplicaSync.safe_print("[ReplicaSync] Listener already running.")
            return

        ReplicaSync.user_id = user_id
        ReplicaSync.network_handler = UDPNetworkHandler(
            host=host,
            port=port,
            on_message=ReplicaSync._handle_message
        )
        ReplicaSync.network_handler.start()

    @staticmethod
    def stop_listener():
        if not ReplicaSync.network_handler:
            ReplicaSync.safe_print("[ReplicaSync] Listener not active.")
            return
        ReplicaSync.network_handler.stop()
        ReplicaSync.network_handler = None
        ReplicaSync.safe_print("[ReplicaSync] Listener stopped.")

    @staticmethod
    def address():
        if ReplicaSync.network_handler:
            return ReplicaSync.network_handler.address()
        return None

    @staticmethod
    def _handle_message(msg: NetworkMessage, addr):
        ReplicaSync.safe_print(f"[ReplicaSync] Received {msg.type.name} from {addr}")

        if msg.type == MessageType.REPLICA_UPDATE:
            ReplicaSync._handle_replica_update(msg, addr)
        elif msg.type == MessageType.REQUEST_REPLICA:
            ReplicaSync._handle_replica_request(addr)
        else:
            ReplicaSync.safe_print(f"[ReplicaSync] Unhandled message type: {msg.type.name}")

    @staticmethod
    def _handle_replica_update(msg: NetworkMessage, addr):
        payload = msg.payload
        replica_data = payload.get("replica_data")
        sender = payload.get("sender_id")

        if not replica_data or not sender:
            ReplicaSync.safe_print("[ReplicaSync] Invalid REPLICA_UPDATE message.")
            return -1

        ReplicaSync.safe_print("[ReplicaSync] Merging replicas...")
        ReplicaSync._merge_replica(other_replica=replica_data)
        ReplicaSync.safe_print("[ReplicaSync] Finished merging replicas.")

    @staticmethod
    def _merge_item(item_own, item_other):
        if not item_own and not item_other:
            return None
        if item_own and not item_other:
            return item_own
        if not item_own and item_other:
            return item_other

        # Both records exist -> Compare version for quantity
        ver_own = item_own.get("version", 0)
        ver_other = item_other.get("version", 0)

        if ver_own >= ver_other:
            merged_item = item_own.copy()
        else:
            merged_item = item_other.copy()

        # deleted counter is causal length counter, so take max
        del_own = item_own.get("deleted_counter", 0)
        del_other = item_other.get("deleted_counter", 0)
        merged_item["deleted_counter"] = max(del_own, del_other)

        return merged_item

    @staticmethod
    def _merge_request(req_own, req_other):
        if not req_own and not req_other:
            return None
        if req_own and not req_other:
            return req_own
        if not req_own and req_other:
            return req_other

        # Request ID matches on both peers -> take logical or of processed
        merged_req = req_own.copy()
        merged_req["processed"] = bool(req_own.get("processed", False) or req_other.get("processed", False))
            
        return merged_req

    @staticmethod
    def _merge_replica(other_replica):

        backend = get_backend()
        own_replica = backend.get_full_replica(ReplicaSync.user_id) or {}

        own_items = own_replica.get("recorded_items", {}) or {}
        other_items = other_replica.get("recorded_items", {}) or {}
        own_requests = own_replica.get("recorded_requests", {}) or {}
        other_requests = other_replica.get("recorded_requests", {}) or {}
        own_users = own_replica.get("known_users", {}) or {}
        other_users = other_replica.get("known_users", {}) or {}

        # 1. Merge items
        merged_items = {}
        all_item_ids = set(own_items.keys()) | set(other_items.keys())
        for iid in all_item_ids:
            merged_items[iid] = ReplicaSync._merge_item(own_items.get(iid), other_items.get(iid))

        # 2. Merge requests
        merged_requests = {}
        all_req_ids = set(own_requests.keys()) | set(other_requests.keys())
        for rrid in all_req_ids:
            merged_requests[rrid] = ReplicaSync._merge_request(own_requests.get(rrid), other_requests.get(rrid))

        # 3. Merge known users
        merged_users = ReplicaSync._merge_known_users(own_users, other_users)

        rebuilt_replica = {
            "id": ReplicaSync.user_id,
            "recorded_items": merged_items,
            "recorded_requests": merged_requests,
            "known_users": merged_users
        }
        backend.write_full_replica(ReplicaSync.user_id, rebuilt_replica)

    @staticmethod
    def _merge_known_users(own_users, other_users):
        if not own_users: return other_users or {}
        if not other_users: return own_users or {}

        merged_users = {}
        all_uids = set(own_users.keys()) | set(other_users.keys())

        for uid in all_uids:
            own_name = own_users.get(uid)
            other_name = other_users.get(uid)

            if own_name and not other_name:
                merged_users[uid] = own_name
            elif other_name and not own_name:
                merged_users[uid] = other_name
            else:
                merged_users[uid] = max(own_name, other_name)
        return merged_users

    @staticmethod
    def _handle_replica_request(addr):
        ReplicaSync.safe_print(f"[ReplicaSync] Peer at {addr} requested our replica.")
        ReplicaSync.send_full_replica(addr[0], addr[1])

    @staticmethod
    def send_full_replica(target_host: str, target_port: int):
        backend = get_backend()
        if not ReplicaSync.network_handler:
            ReplicaSync.safe_print("[ReplicaSync] Listener not running — cannot send.")
            return

        replica = backend.get_full_replica(ReplicaSync.user_id)
        msg = NetworkMessage(
            MessageType.REPLICA_UPDATE,
            {
                "sender_id": ReplicaSync.user_id,
                "replica_data": replica
            }
        )
        ReplicaSync.network_handler.send_message(msg, target_host, target_port)
        ReplicaSync.safe_print(f"[ReplicaSync] Sent replica to {target_host}:{target_port}")

    @staticmethod
    def request_replica(target_host: str, target_port: int):
        if not ReplicaSync.network_handler:
            ReplicaSync.safe_print("[ReplicaSync] Listener not running — cannot request.")
            return

        msg = NetworkMessage(
            MessageType.REQUEST_REPLICA,
            {"sender_id": ReplicaSync.user_id}
        )
        ReplicaSync.network_handler.send_message(msg, target_host, target_port)
        ReplicaSync.safe_print(f"[ReplicaSync] Requested replica from {target_host}:{target_port}")