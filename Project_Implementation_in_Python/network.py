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
        self.sender = sender # using the id
        self.receiver = receiver # using the id
        self.content = content

"""
Simple network simulator. Takes the users from the user_handler
"""
class Network_Simulator:
    def __init__(self, user_handler):
        self.user_handler = user_handler
        self.messages = {}
    
    def send_message(self, sender, receiver, content):
        if self.messages.get(receiver) is None:
            self.messages[receiver] = [(sender, content)]
        else:
            self.messages[receiver].append((sender, content))

        
    def broad_cast_message(self, sender, content):
        for user in self.user_handler.getUsers():
                self.send_message(sender, user.user_id, content)
    
    def broad_cast_message_except_sender(self, sender, content):
        for user in self.user_handler.getUsers():
            if user.user_id != sender:
                self.send_message(sender, user.user_id, content)

    def receive_message(self, receiver):
        # Simulate receiving a message for the receiver, return a list of messages for the receiver, if there are no messages return an empty list
        if self.messages.get(receiver) is None:
            return []
        else:
            messages = self.messages[receiver]
            self.messages[receiver] = [] # Clear the messages
            return messages

    def send_message(self, sender, receiver, content):
        # Check if there is already a message for the receiver
        if self.messages.get(receiver) is None or len(self.messages[receiver]) == 0:
            self.messages[receiver] = [(sender, content)]
        else:
            self.messages[receiver].append((sender, content))
        pass