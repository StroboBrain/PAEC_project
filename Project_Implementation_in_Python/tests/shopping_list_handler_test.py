from shopping_list_handler import ShoppingListHandler

def test_add_item():
    handler = ShoppingListHandler()
    replica = handler.intialize_replica()
    replica.add_new_item("Milk")
    assert len(replica.items) == 1
    assert list(replica.items.values())[0].name == "Milk"

