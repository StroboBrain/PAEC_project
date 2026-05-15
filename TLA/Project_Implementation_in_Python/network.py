"""
This module contains the Network class, which represents a network, could be repalaced by a real network
"""



class Network_Handler:
    def __init__(self, network: str):
        # Entry point to use different networks
        if network == "simulator":
            self.network = Network_Simulator()
        

    
    def setup_network(self):
        # Simulate setting up the network based on the configuration
        pass


class Message:
    def __init__(self, sender, receiver, content):
        self.sender = sender
        self.receiver = receiver
        self.content = content


"""
Simple network simulator
"""
class Network_Simulator:
    def __init__(self):
        self.user_list = []
        self.message_queue = []


    def add_user(self, name):
        # Simulate adding a user to the network
        pass

    def send_message(self, sender, receiver, message):
        # Simulate sending a message from sender to receiver
        pass

    def receive_message(self, receiver):
        # Simulate receiving a message for the receiver
        pass