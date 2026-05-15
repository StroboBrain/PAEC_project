"""
ShoppingList is the class that holds the data, does not have any logic
"""

from sqlite3 import Time


class ShoppingList:    
    # possible items is a list of items that can be added
    def init__(self, possible_items):
        # item id is simply the index of the item
        self.possible_items = possible_items
    
    def add_item(self, item_name):
        pass
    
    def generate_item_id(self, item_name):
        timestamp = Time.get_current_time()
        item_id = hash((item_name, timestamp))
        return item_id


    class Item:
        def __init__(self, name, item_id, quantity):
            self.name = name
            self.added_quantity = [quantity]
            self.decreased_quantity = 0
            self.item_deleted = 0
