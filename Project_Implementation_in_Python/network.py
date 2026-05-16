"""
This module contains the Network classes, which represent a network.
The simulator could later be replaced by a real network.
"""

from message import Message

class Network_Handler:
    def __init__(self, network: str, user_handler):
        # Entry point to use different networks
        if network == "simulator":
            self.network = Network_Simulator(user_handler)
        else:
            raise ValueError(f"Unknown network type: {network}")

class Network_Simulator:
    """
    Simple network simulator. Takes the users from the user_handler.
    """

    def __init__(self, user_handler):
        self.user_handler = user_handler
        self.messages = {}  # receiver_id: [Message, Message, ...]

    def _get_user_id(self, user):
        """
        Accept either a user object or a raw user ID.
        """
        return user.user_id if hasattr(user, "user_id") else user

    def send_message(self, sender, receiver, content):
        sender_id = self._get_user_id(sender)
        receiver_id = self._get_user_id(receiver)

        new_message = Message(sender_id, receiver_id, content)
        self.messages.setdefault(receiver_id, []).append(new_message)

    def broad_cast_message(self, sender, content):
        sender_id = self._get_user_id(sender)

        for user in self.user_handler.getUsers():
            receiver_id = self._get_user_id(user)

            new_message = Message(sender_id, receiver_id, content)
            self.messages.setdefault(receiver_id, []).append(new_message)

    def broad_cast_message_except_sender(self, sender, content):
        sender_id = self._get_user_id(sender)

        for user in self.user_handler.getUsers():
            receiver_id = self._get_user_id(user)

            if receiver_id != sender_id:
                new_message = Message(sender_id, receiver_id, content)
                self.messages.setdefault(receiver_id, []).append(new_message)

    def receive_message(self, receiver):
        """
        Return all messages for the receiver and clear their inbox.
        """
        receiver_id = self._get_user_id(receiver)

        received_messages = self.messages.get(receiver_id, [])
        self.messages[receiver_id] = []

        return received_messages

    def receive_message_from_sender(self, receiver, sender):
        """
        Return only messages for receiver that came from sender.
        Messages from other senders remain in the inbox.
        """
        receiver_id = self._get_user_id(receiver)
        sender_id = self._get_user_id(sender)

        inbox = self.messages.get(receiver_id, [])

        received_messages = [
            message
            for message in inbox
            if message.sender == sender_id
        ]

        self.messages[receiver_id] = [
            message
            for message in inbox
            if message.sender != sender_id
        ]

        return received_messages