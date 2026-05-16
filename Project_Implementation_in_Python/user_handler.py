"""
UserHandler is a singletion class 
"""
import uuid

from shopping_list_handler import ShoppingListHandler

import enum

class UserAction(enum.Enum):
    ADD_ITEM = "add_item"
    REQUEST_QUANTITY_INCREASE = "request_quantity_increase"
    REQUEST_QUANTITY_DECREASE = "request_quantity_decrease"

class UsersHandler:
    """
    Singleton class for handling users
    user_names is a list of unique strings
    default_items is a list of unique strings
    """
    def __init__(self):
        self.userlist = [] # List of user objects
        self.shopping_list_handler = ShoppingListHandler()

    def create_user(self, name):
        user_id = uuid.uuid4() 
        replica = self.shopping_list_handler.intialize_replica()
        user = User(name, user_id, replica)
        return user

    def add_user(self, name):
        temp = self.create_user(name)
        self.userlist.append(temp)
    
    def getUsers(self):
        return self.userlist

class User:
    # shopping_list needs to be a shopping list object
    def __init__(self, name, user_id, replica):
        self.name = name
        self.user_id = user_id
        self.shopping_list = replica

    def add_item(self, item_name):
        """
        Implements the TLA action for adding an item to the shopping list
        """
        item = ShoppingListHandler.ItemHandler.create_item(item_name, self.user_id)
        assert isinstance(item.id, uuid.UUID), "Item ID must be a UUID"
        assert isinstance(item.creator, uuid.UUID), "Item creator must be a UUID"
        assert isinstance(self.shopping_list, ShoppingListHandler.Replica), "Shopping list must be a Replica instance"

        self.shopping_list.items[item.id] = item
    
    def delete_item(self, item_id):
        """
        Implements the TLA action for deleting an item from the shopping list, acepts either an item object or an item ID
        """

        if isinstance(item_id, ShoppingListHandler.Item):
            item_id = item_id.id

        assert isinstance(item_id, uuid.UUID), "Item ID must be a UUID"
        assert isinstance(self.shopping_list.id, uuid.UUID), "Shopping list ID must be a UUID"
        assert isinstance(self.id, uuid.UUID), "User ID must be a UUID"

        if item_id in self.shopping_list.items:
            item = self.shopping_list.items[item_id]
            # Only active items can be deleted
            if not item.is_deleted():
                item.delete_counter += 1