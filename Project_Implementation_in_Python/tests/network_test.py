import uuid

from network import Network_Simulator

class dummy_user:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return self.user_id

class dummy_user_handler:
    def __init__(self, users):
        self.users = users

    def getUsers(self):
        return self.users

def test_send_message():
    dummy_user_1 = dummy_user(uuid.uuid4())
    dummy_user_2 = dummy_user(uuid.uuid4())
    user_handler = dummy_user_handler([dummy_user_1, dummy_user_2])
    network = Network_Simulator(user_handler)
    network.send_message(dummy_user_1, dummy_user_2, "Hello, user 2!")
    assert network.messages[dummy_user_2.user_id][0].content == "Hello, user 2!"
    