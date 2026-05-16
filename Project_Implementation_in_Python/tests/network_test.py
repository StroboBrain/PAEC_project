import uuid

from network import Network_Simulator


class DummyUser:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return self.user_id


class DummyUserHandler:
    def __init__(self, users):
        self.users = users

    def getUsers(self):
        return self.users


def test_send_message():
    sender = DummyUser(uuid.uuid4())
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender, receiver])
    network = Network_Simulator(user_handler)

    network.send_message(sender, receiver, "Hello!")

    assert receiver.user_id in network.messages
    assert len(network.messages[receiver.user_id]) == 1

    message = network.messages[receiver.user_id][0]

    assert message.sender == sender.user_id
    assert message.receiver == receiver.user_id
    assert message.content == "Hello!"


def test_send_multiple_messages_to_same_receiver():
    sender = DummyUser(uuid.uuid4())
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender, receiver])
    network = Network_Simulator(user_handler)

    network.send_message(sender, receiver, "First message")
    network.send_message(sender, receiver, "Second message")

    messages = network.messages[receiver.user_id]

    assert len(messages) == 2
    assert messages[0].content == "First message"
    assert messages[1].content == "Second message"


def test_broad_cast_message():
    sender = DummyUser(uuid.uuid4())
    receiver_1 = DummyUser(uuid.uuid4())
    receiver_2 = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender, receiver_1, receiver_2])
    network = Network_Simulator(user_handler)

    network.broad_cast_message(sender, "Broadcast message")

    for user in [sender, receiver_1, receiver_2]:
        assert user.user_id in network.messages
        assert len(network.messages[user.user_id]) == 1

        message = network.messages[user.user_id][0]

        assert message.sender == sender.user_id
        assert message.receiver == user.user_id
        assert message.content == "Broadcast message"


def test_broad_cast_message_except_sender():
    sender = DummyUser(uuid.uuid4())
    receiver_1 = DummyUser(uuid.uuid4())
    receiver_2 = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender, receiver_1, receiver_2])
    network = Network_Simulator(user_handler)

    network.broad_cast_message_except_sender(sender, "Message for others")

    assert sender.user_id not in network.messages

    for receiver in [receiver_1, receiver_2]:
        assert receiver.user_id in network.messages
        assert len(network.messages[receiver.user_id]) == 1

        message = network.messages[receiver.user_id][0]

        assert message.sender == sender.user_id
        assert message.receiver == receiver.user_id
        assert message.content == "Message for others"

def test_receive_message():
    sender = DummyUser(uuid.uuid4())
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender, receiver])
    network = Network_Simulator(user_handler)

    network.send_message(sender, receiver, "First message")
    network.send_message(sender, receiver, "Second message")

    received_messages = network.receive_message(receiver)

    assert len(received_messages) == 2
    assert received_messages[0].content == "First message"
    assert received_messages[1].content == "Second message"

    assert network.messages[receiver.user_id] == []


def test_receive_message_when_inbox_is_empty():
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([receiver])
    network = Network_Simulator(user_handler)

    received_messages = network.receive_message(receiver)

    assert received_messages == []
    assert network.messages[receiver.user_id] == []


def test_receive_message_from_sender():
    sender_1 = DummyUser(uuid.uuid4())
    sender_2 = DummyUser(uuid.uuid4())
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender_1, sender_2, receiver])
    network = Network_Simulator(user_handler)

    network.send_message(sender_1, receiver, "Message from sender 1")
    network.send_message(sender_2, receiver, "Message from sender 2")
    network.send_message(sender_1, receiver, "Another message from sender 1")

    received_messages = network.receive_message_from_sender(receiver, sender_1)

    assert len(received_messages) == 2
    assert received_messages[0].sender == sender_1.user_id
    assert received_messages[0].content == "Message from sender 1"
    assert received_messages[1].sender == sender_1.user_id
    assert received_messages[1].content == "Another message from sender 1"

    remaining_messages = network.messages[receiver.user_id]

    assert len(remaining_messages) == 1
    assert remaining_messages[0].sender == sender_2.user_id
    assert remaining_messages[0].receiver == receiver.user_id
    assert remaining_messages[0].content == "Message from sender 2"

def test_receive_message_from_sender_when_sender_has_no_messages():
    sender_1 = DummyUser(uuid.uuid4())
    sender_2 = DummyUser(uuid.uuid4())
    receiver = DummyUser(uuid.uuid4())

    user_handler = DummyUserHandler([sender_1, sender_2, receiver])
    network = Network_Simulator(user_handler)

    network.send_message(sender_2, receiver, "Message from sender 2")

    received_messages = network.receive_message_from_sender(receiver, sender_1)

    assert received_messages == []

    remaining_messages = network.messages[receiver.user_id]

    assert len(remaining_messages) == 1
    assert remaining_messages[0].sender == sender_2.user_id
    assert remaining_messages[0].content == "Message from sender 2"