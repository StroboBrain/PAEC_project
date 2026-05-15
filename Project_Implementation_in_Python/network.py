"""
This module contains the Network class, which represents a network, could be repalaced by a real network
"""
class Network_Handler:
    def __init__(self, network: str, user_handler):
        # Entry point to use different networks
        if network == "simulator":
            self.network = Network_Simulator(user_handler)
        
class Message:
    def __init__(self, sender, receiver, content):
        self.sender = sender
        self.receiver = receiver
        self.content = content

"""
Simple network simulator. Takes the users from the user_handler
"""
class Network_Simulator:
    def __init__(self, user_handler):
        self.user_handler = user_handler
        self.message_queue = []
    
    def send_message(self, sender, receiver, message):
        # Check if there is already a message for the receiver, if not create a new list, if yes append the message to the list
        if self.message_storage.get(receiver) is None:
            self.message_storage[receiver] = [message]
        else:
            self.message_storage[receiver].append((sender, message))
        pass

    def broad_cast_message(self, sender, message):
        for user in self.user_handler.getUsers():
                self.send_message(sender, user.user_id, message)
    
    def broad_cast_message_except_sender(self, sender, message):
        for user in self.user_handler.getUsers():
            if user.user_id != sender:
                self.send_message(sender, user.user_id, message)

    def receive_message(self, receiver):
        # Simulate receiving a message for the receiver, return a list of messages for the receiver, if there are no messages return an empty list
        if self.message_storage.get(receiver) is None:
            return []
        else:
            messages = self.message_storage[receiver]
            self.message_storage[receiver] = [] # Clear the messages
            return messages

    def send_message(self, sender, receiver, message):
        # Simulate sending a message from sender to receiver
        pass

    def receive_message(self, receiver):
        # Simulate receiving a message for the receiver
        pass