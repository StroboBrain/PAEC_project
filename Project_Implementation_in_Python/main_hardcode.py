"""
Development class, to run with preset data
"""

from network import Network_Handler
from user_handler import UsersHandler

# Singleton user handler
user_handler = UsersHandler()
user_handler.add_user("Alice")
user_handler.add_user("Bob")

# Singleteon network handler with the users from the user handler
network = network_handler = Network_Handler("simulator", user_handler)



print("main_hardcode.py: has run")