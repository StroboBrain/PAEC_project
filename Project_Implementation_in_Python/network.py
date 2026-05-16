"""
This module contains the Network classes, which represent a network.
The simulator could later be replaced by a real network.
"""
class Network_Handler:
    def __init__(self, network: str, user_handler):
        # Entry point to use different networks
        if network == "simulator":
            self.network = Network_Simulator(user_handler)

class Message:
    def __init__(self, sender, receiver, content):
        self.sender = sender      # sender ID
        self.receiver = receiver  # receiver ID
        self.content = content

"""
Simple network simulator. Takes the users from the user_handler.
"""
class Network_Simulator:
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

        message = Message(sender_id, receiver_id, content)

        self.messages.setdefault(receiver_id, []).append(message)

    def broad_cast_message(self, sender, content):
        sender_id = self._get_user_id(sender)

        for user in self.user_handler.getUsers():
            receiver_id = user.user_id
            message = Message(sender_id, receiver_id, content)

            self.messages.setdefault(receiver_id, []).append(message)

    def broad_cast_message_except_sender(self, sender, content):
        sender_id = self._get_user_id(sender)

        for user in self.user_handler.getUsers():
            receiver_id = user.user_id

            if receiver_id != sender_id:
                message = Message(sender_id, receiver_id, content)

                self.messages.setdefault(receiver_id, []).append(message)

    def receive_message(self, receiver):
        receiver_id = self._get_user_id(receiver)

        messages = self.messages.get(receiver_id, [])
        self.messages[receiver_id] = []  # Clear inbox after receiving

        return messages