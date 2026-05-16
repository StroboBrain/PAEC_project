"""
Implements messages, message contents, and the possible message actions.
"""

from enum import Enum


class MessageAction(Enum):
    ADD_ITEM = "add_item"
    REQUEST_QUANTITY_INCREASE = "request_quantity_increase"
    REQUEST_QUANTITY_DECREASE = "request_quantity_decrease"
    ACCEPT_REQUEST = "accept_request"
    DENY_REQUEST = "deny_request"
    DELETE_ITEM = "delete_item"
    REINSTATE_ITEM = "reinstate_item"
    MERGE_ITEM = "merge_item"
    MERGE_REQUEST = "merge_request"
    MERGE_REPLICA = "merge_replica"


class Content:
    def __init__(self, action: MessageAction, content):
        assert isinstance(action, MessageAction), "Action must be an instance of MessageAction Enum"
        self.action = action
        self.content = content

class Message:
    def __init__(self, sender, receiver, content: Content):
        self.sender = sender      # sender ID
        self.receiver = receiver  # receiver ID
        self.content = content

class MessageParser:
    @staticmethod
    def parse_message(message, user):
        assert isinstance(message, Message), "Input should be of type Message"
        assert isinstance(message.content, Content), "Message content should be of type Content"

        return message