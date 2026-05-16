"""
Checks the liveness and safety properties of the shopping list implementation.
TypeOK is checked through assertions in the . Might not be needed
"""
from user_handler import UsersHandler

class QuantityNonNegative:
    """
    Currently checked with assertions
    """

    def __init__(self, user_handler):
        self.userlist = user_handler.getUsers()

    def check(self):
        for i in self.userlist:
            assert isinstance(i.shopping_list, UsersHandler.ShoppingListHandler.Replica), "User's shopping list must be a Replica instance"
            for _id, item in i.shopping_list.items.items():
                assert isinstance(item, UsersHandler.ShoppingListHandler.Item), "Shopping list items must be of type Item"
                assert item.quantity >= 0, "Item quantity must be non-negative"
    