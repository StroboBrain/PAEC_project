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
        Implements the TLA action for deleting an item from the shopping list, accepts only item objects
        """
        assert isinstance(item_id, uuid.UUID), "Item ID must be a UUID"
        assert isinstance(self.shopping_list.id, uuid.UUID), "Shopping list ID must be a UUID"
        assert isinstance(self.id, uuid.UUID), "User ID must be a UUID"

        if item_id in self.shopping_list.items:
            item = self.shopping_list.items[item_id]
            # Only active items can be deleted
            if not item.is_deleted():
                item.delete_counter += 1 # Only function that can increase the delte counter, so the No_decrease_deleted_counter property only needs to be checked here and in the merge_item
    
    def reinstate_item(self, item_id):
        """
        Implements the TLA action for reinstating an item from the shopping list, accepts only item objects
        """

        assert isinstance(item_id, uuid.UUID), "Item ID must be a UUID"
        assert isinstance(self.shopping_list.id, uuid.UUID), "Shopping list ID must be a UUID"
        assert isinstance(self.id, uuid.UUID), "User ID must be a UUID"

        if item_id in self.shopping_list.items:
            item = self.shopping_list.items[item_id]
            # Only deleted items can be reinstated
            if item.is_deleted():
                item.delete_counter +=1 
    
    def merge_item(self, item_own, item_other):
        """
        Implements the TLA action for merging two items in the shopping list, accepts only item objects
        """
        if item_own == None:
            if item_other == None: # Both items do not exist, nothing to merge
                return
            else:
                # Only item_other exists, add it to the shopping list
                self.shopping_list.items[item_other.id] = item_other
        else:
            if item_other == None: # Only item_own exists, nothing to merge
                return
            else:
                # Both items exist, merge them by taking the max version and delete counter
                item_own.version = max(item_own.version, item_other.version)
                # max is always greater or equal to both delete counters, so the No_decrease_deleted_counter property is not violated
                item_own.delete_counter = max(item_own.delete_counter, item_other.delete_counter) 




    def merge_replica(self, other_replica):
        """
        Implements the TLA action for merging two replicas of the shopping list
        """
        assert isinstance(other_replica, ShoppingListHandler.Replica), "Other replica must be a Replica instance"
        assert isinstance(self.shopping_list.id, uuid.UUID), "Shopping list ID must be a UUID"
        assert isinstance(other_replica.id, uuid.UUID), "Other replica ID must be a UUID"

        
