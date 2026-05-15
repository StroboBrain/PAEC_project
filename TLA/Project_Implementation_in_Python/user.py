"""
"""

class UserCreator:
    def __init__(self):
        self.users_id = 0
    def create_user(self, name, shopping_list):
        # Simulate creating a user with a unique ID
        user_id = self.users_id
        self.users_id += 1
        return User(name, user_id, shopping_list)

class User:
    # shopping_list needs to be a shopping list object
    def __init__(self, name, user_id, shopping_list):
        self.name = name
        self.user_id = user_id
        self.shopping_list = shopping_list
