from network import Network_Simulator
from user_handler import UsersHandler


# Singleton user handler
user_handler = UsersHandler()
# Singleteon network handler
network_handler = Network_Simulator(user_handler.getUsers())
