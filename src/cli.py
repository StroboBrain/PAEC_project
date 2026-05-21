import sys, os
from replica_sync import ReplicaSync
from storage_provider import get_backend
from request_handler import Request, RequestHandler
from item_handler import Item, ItemHandler


class CLIInterface:
    def __init__(self, user_id):
        self.user_id = user_id

        print("[ReplicaSync] Starting listener...")
        ReplicaSync.start_listener(self.user_id)
        addr = ReplicaSync.address()
        if addr:
            print(f"[ReplicaSync] Listening at {addr}")
        else:
            print("[ReplicaSync] Failed to start listener.")

    def _resolve_entity(self, entity_type: str, name_or_id: str):
        backend = get_backend()
        replica = backend.get_full_replica(self.user_id)
        entities = {}

        if entity_type in ("user", "known_users"):
            entities = replica.get("known_users", {})
            search_type = "user"
        elif entity_type in ("item", "recorded_items"):
            entities = replica.get("recorded_items", {})
            search_type = "item"
        elif entity_type in ("request", "recorded_requests"):
            entities = replica.get("recorded_requests", {})
            search_type = "request"
        else:
            raise ValueError("Invalid entity_type")

        # 1. Exact ID Match Optimization
        if name_or_id in entities:
            return name_or_id

        # 2. Friendly Name Match
        matches = []
        if search_type == "user":
            matches = [uid for uid, uname in entities.items() if uname == name_or_id]
        elif search_type == "item":
            matches = [iid for iid, data in entities.items() if data.get("name") == name_or_id]
        elif search_type == "request":
            matches = [rrid for rrid, data in entities.items() if data.get("name") == name_or_id]

        if not matches:
            print(f"No {search_type} found matching '{name_or_id}'.")
            return ""

        if len(matches) == 1:
            return matches[0]

        # 3. Handle Ambiguities
        print(f"Multiple {search_type}s found with that name:")
        for eid in matches:
            if search_type == "user":
                print(f"  - {entities[eid]} (id: {eid})")
            elif search_type == "item":
                print(f"  - {entities[eid].get('name')} (id: {eid})")
            elif search_type == "request":
                print(f"  - {entities[eid].get('name')} | Sender: {entities[eid].get('sender')} (id: {eid})")

        chosen = input("Enter the exact id to use: ").strip()
        if chosen in matches:
            return chosen
        print("Invalid choice.")
        return ""

    def run(self):
        print("\nType 'help' to see available commands.\n")
        try:
            while True:
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()              
                cmd_input = input("shopping_list> ").strip()
                if not cmd_input:
                    continue
                parts = cmd_input.split()
                cmd, args = parts[0], parts[1:]

                if cmd in ("exit", "quit", "q"):
                    print("Exiting Shopping list CLI.")
                    break
                elif cmd == "clear":
                    self.cmd_clear()
                elif cmd == "help":
                    self.print_help()
                elif cmd == "print":
                    self.print(args)
                elif cmd == "create_item":
                    print(self.create_item(args))
                elif cmd == "create_request":
                    print(self.create_request(args))
                elif cmd == "process_request":
                    print(self.process_request(args))
                elif cmd == "delete_item":
                    print(self.delete_item(args))
                elif cmd == "reinstate_item":
                    print(self.reinstate_item(args))
                elif cmd == "sync":
                    self.trigger_sync(args)
                else:
                    print("Unknown command. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to leave.")
        finally:
            ReplicaSync.stop_listener()

    def print_help(self):
        print("Available Commands:")
        print("  print [all|items|requests|users]                       - Display replica states")
        print("  create_item <name> <quantity>                          - Initialize a baseline inventory item")
        print("  create_request <item_name|id> <request_name> <amount>  - Request a quantity modification (+/-)")
        print("  process_request <req_id|req_name> <accept|deny>        - Creator processes modifications")
        print("  delete_item <item_name|id>                             - Mark an item as deleted")
        print("  reinstate_item <item_name|id>                          - Un-delete a removed item")
        print("  sync [push|pull] <host> <port>                         - Push or pull dynamic updates to/from other peer")
        print("  clear)                                                 - clear the command window")
        print("  exit / quit                                            - Safely terminate runtime listeners")



    def cmd_clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print(self, args):
        backend = get_backend()
        replica = backend.get_full_replica(self.user_id)
        target = args[0] if args else "all"

        if target == "all":
            print(replica)
        elif target == "items":
            for item in replica.get("recorded_items", {}).values():
                if item: print(Item.from_dict(item))
        elif target == "requests":
            for request in replica.get("recorded_requests", {}).values():
                if request: 
                    if "name" not in request: request["name"] = request.get("rrid", "Unknown")
                    print(Request.from_dict(request))
        elif target == "users":
            for uid, uname in replica.get("known_users", {}).items():
                print(f"{uname} (id: {uid})")
        else:
            print("Usage: print [all|items|requests|users]")


    def create_item(self, args):
        if len(args) < 2:
            return "Usage: create_item <name> <quantity>"
        name = args[0]
        try:
            quantity = int(args[1])
        except ValueError:
            return "Error: Quantity must be an integer."

        _, msg = ItemHandler.create_item(self.user_id, name, quantity)
        return msg

    def create_request(self, args):
        if len(args) < 2:
            return "Usage: create_request <item_name|item_id> <request_name> <change_amount>"
        
        # Look up item to extract its true ID and name string
        iid = self._resolve_entity("item", args[0])
        if not iid:
            return "Error: Could not locate that target item."
            
        backend = get_backend()
        item_data = backend.get_item(self.user_id, iid)
        item_name = item_data.get("name", "UnknownItem")

        try:
            amount = int(args[2])
        except ValueError:
            return "Error: Change amount must be an integer scalar value."

        _, msg = RequestHandler.create_request(self.user_id, iid, item_name, args[1], amount)
        return msg

    def process_request(self, args):
        if len(args) < 2:
            return "Usage: process_request <request_id|request_name> <accept|deny>"
        
        rrid = self._resolve_entity("request", args[0])
        if not rrid:
            return "Error: Could not locate the target request object."
            
        decision = args[1].lower()
        if decision not in ("accept", "deny"):
            return "Error: Output evaluation parameter must be either 'accept' or 'deny'."

        if decision == "accept":
            _, msg = RequestHandler.process_request(self.user_id, rrid, accept=True)
            return msg
        else:
            _, msg = RequestHandler.process_request(self.user_id, rrid, accept=False)
            return msg

    def delete_item(self, args):
        if len(args) < 1:
            return "Usage: delete_item <name|item_id>"
        iid = self._resolve_entity("item", args[0])
        if not iid:
            return "Error: Could not locate that target item."
        _, msg = ItemHandler.delete_item(self.user_id, iid)
        return msg

    def reinstate_item(self, args):
        if len(args) < 1:
            return "Usage: reinstate_item <name|item_id>"
        iid = self._resolve_entity("item", args[0])
        if not iid:
            return "Error: Could not locate that target item."
        _, msg = ItemHandler.reinstate_item(self.user_id, iid)
        return msg

    def trigger_sync(self, args):
        if len(args) < 3:
            print("Usage: sync <pull|push> <target_host> <target_port>")
            return

        direction = args[0].lower()
        if direction not in ("pull", "push"):
            print("Error: Direction parameter must be explicitly defined as either 'pull' or 'push'.")
            return

        try:
            host = args[1]
            port = int(args[2])
            
            if direction == "pull":
                print(f"[CLI] Initiating data request... pulling from peer at {host}:{port}")
                ReplicaSync.request_replica(host, port)
                
            elif direction == "push":
                print(f"[CLI] Broadcasting state changes... pushing local replica data to {host}:{port}")
                ReplicaSync.send_full_replica(host, port)
                
        except ValueError:
            print("Error: Port parameter must be a valid numeric integer value.")
        except Exception as e:
            print(f"Sync instantiation failure: {e}")