"""
ShoppingList is the class that holds the data, does not have any logic
"""
import uuid

class ShoppingListHandler:    
    # possible items is a list of items that can be added
    def __init__(self):
        pass

    def intialize_replica(self):
        return self.Replica(uuid.uuid4())
    
    class Item:
        def __init__(self, item_id, creator, name):
            # TLA implementation
            self.id = item_id
            self.creator = creator
            self.version = 0
            self.delete_counter = 0
            # Implementation specific
            self.name = name
    
    class Request():
        def __init__(self, request_id, sender, change_amount, processed = False):
            self.request_id = request_id
            self.sender = sender
            self.change_amount = change_amount
            self.processed = processed
    
    class Replica():
        def __init__(self, replica_id, recorded_requests = []):
            self.id = replica_id
            self.recorded_requests = recorded_requests
            self.items = {} # item_id: Item

        def add_new_item(self, item_name):
            item_id = uuid.uuid4()
            item = ShoppingListHandler.Item(item_id, self.id, item_name)
            self.items[item_id] = item

        def create_replica(self):
            replica_id = self.generate_id()
            return self.Replica(replica_id, self, [])
        
        def generate_request(self, user, change_amount):
            id = self.generate_id()
            return self.Request(id, user, change_amount, False)
        



            