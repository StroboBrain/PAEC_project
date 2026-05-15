"""
This module contains the Network class, which represents a network, could be repalaced by a real network
"""
class Network_Handler:
    def __init__(self, network: str, users: list):
        # Entry point to use different networks
        if network == "simulator":
            self.network = Network_Simulator(users)
        
        def send_message(self, sender, receiver, message):
            self.network.send_message(sender, receiver, message)

class Message:
    def __init__(self, sender, receiver, content):
        self.sender = sender
        self.receiver = receiver
        self.content = content

"""
Simple network simulator
"""
class Network_Simulator:
    def __init__(self, users):
        self.user_list = users
        self.message_queue = []
    
    def send_message(self, sender, receiver, message):
        # Check if there is already a message for the receiver, if not create a new list, if yes append the message to the list
        if self.message_storage.get(receiver) is None:
            self.message_storage[receiver] = [message]
        else:
            self.message_storage[receiver].append((sender, message))
        pass

    def broad_cast_message(self, sender, message):

        pass

    def receive_message(self, receiver):
        pass

    def add_user(self, name):
        # Simulate adding a user to the network
        pass

    def send_message(self, sender, receiver, message):
        # Simulate sending a message from sender to receiver
        pass

    def receive_message(self, receiver):
        # Simulate receiving a message for the receiver
        pass