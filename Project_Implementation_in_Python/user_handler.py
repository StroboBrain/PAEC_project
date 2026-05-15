"""
UserHandler is a singletion class 
"""
from shopping_list import ShoppingList

class UsersHandler:
    """
    Singleton class for handling users
    user_names is a list of unique strings
    default_items is a list of unique strings
    """
    def __init__(self, user_names = None, default_items = None):
        self.next_users_id = 0 # user id is a unique integer that is incremented for each new user
        self.userlist = [] # List of user objects
        if default_items:
            assert(len(set(default_items)) == len(default_items)), "Default items must be unique"
        if user_names:
            assert(len(set(user_names)) == len(user_names)), "User names must be unique"
            for name in user_names:
                self.add_user(name, default_items)
    
    def create_user(self, name, shopping_list):
        # Simulate creating a user with a unique ID
        user_id = self.next_users_id
        self.next_users_id += 1
        user = User(name, user_id, ShoppingList(shopping_list))
        return user

    def add_user(self, name, shopping_list):
        temp = self.create_user(name, shopping_list)
        self.userlist.append(temp)
    
    def getUsers(self):
        return self.userlist

class User:
    # shopping_list needs to be a shopping list object
    def __init__(self, name, user_id, shopping_list):
        self.name = name
        self.user_id = user_id
        self.shopping_list = shopping_list