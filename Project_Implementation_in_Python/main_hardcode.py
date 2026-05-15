"""
Development class, to run with preset data
"""

from user_handler import UsersHandler

# import data
from default_items import default_items, default_usernames

# Singleton user handler
user_handler = UsersHandler()



print("main_hardcode.py: has run")