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

    message = network.messages[dummy_user_2.user_id][0]

    assert message.sender == dummy_user_1.user_id
    assert message.receiver == dummy_user_2.user_id
    assert message.content == "Hello, user 2!"


def test_broad_cast_message():
    dummy_user_1 = dummy_user(uuid.uuid4())
    dummy_user_2 = dummy_user(uuid.uuid4())
    dummy_user_3 = dummy_user(uuid.uuid4())

    user_handler = dummy_user_handler(
        [dummy_user_1, dummy_user_2, dummy_user_3]
    )
    network = Network_Simulator(user_handler)

    network.broad_cast_message(dummy_user_1, "Hello, everyone!")

    for user in [dummy_user_1, dummy_user_2, dummy_user_3]:
        message = network.messages[user.user_id][0]

        assert message.sender == dummy_user_1.user_id
        assert message.receiver == user.user_id
        assert message.content == "Hello, everyone!"


def test_broad_cast_message_except_sender():
    dummy_user_1 = dummy_user(uuid.uuid4())
    dummy_user_2 = dummy_user(uuid.uuid4())
    dummy_user_3 = dummy_user(uuid.uuid4())

    user_handler = dummy_user_handler(
        [dummy_user_1, dummy_user_2, dummy_user_3]
    )
    network = Network_Simulator(user_handler)

    network.broad_cast_message_except_sender(dummy_user_1, "Hello, others!")

    assert dummy_user_1.user_id not in network.messages

    for user in [dummy_user_2, dummy_user_3]:
        message = network.messages[user.user_id][0]

        assert message.sender == dummy_user_1.user_id
        assert message.receiver == user.user_id
        assert message.content == "Hello, others!"


def test_receive_message():
    dummy_user_1 = dummy_user(uuid.uuid4())
    dummy_user_2 = dummy_user(uuid.uuid4())

    user_handler = dummy_user_handler([dummy_user_1, dummy_user_2])
    network = Network_Simulator(user_handler)

    network.send_message(dummy_user_1, dummy_user_2, "First message")
    network.send_message(dummy_user_1, dummy_user_2, "Second message")

    received_messages = network.receive_message(dummy_user_2)

    assert len(received_messages) == 2
    assert received_messages[0].content == "First message"
    assert received_messages[1].content == "Second message"

    assert network.messages[dummy_user_2.user_id] == []


def test_receive_message_when_no_messages_exist():
    dummy_user_1 = dummy_user(uuid.uuid4())

    user_handler = dummy_user_handler([dummy_user_1])
    network = Network_Simulator(user_handler)

    received_messages = network.receive_message(dummy_user_1)

    assert received_messages == []