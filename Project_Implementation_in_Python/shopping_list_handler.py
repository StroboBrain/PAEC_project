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
    
    class ItemHandler:
        def __init__():
            pass
        @staticmethod
        def create_item(item_name, creator_id):
            item_id = uuid.uuid4()
            return ShoppingListHandler.Item(item_id, creator_id, item_name)
        
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
    
    """
    Each user has its own replica of the shopping list
    """
    class Replica():
        def __init__(self, replica_id, recorded_requests = []):
            self.id = replica_id
            self.recorded_requests = recorded_requests
            self.items = {} # item_id: Item
            