"""
UserHandler is a singletion class 
"""
import uuid

from shopping_list_handler import ShoppingListHandler


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