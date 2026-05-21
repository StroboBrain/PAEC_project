import uuid
from dataclasses import dataclass, asdict
from typing import Dict
from storage_provider import get_backend

@dataclass
class Item:
    iid: str
    name: str
    creator: str
    quantity: int
    version: int
    deleted_counter: int

    def __str__(self):
        deleted_str = "Yes" if self.deleted_counter % 2 == 1 else "No"
        return (
            f"  Item '{self.name}' (id={self.iid})\n"
            f"  Creator: {self.creator}\n"
            f"  Quantity: {self.quantity}\n"
            f"  Version: {self.version}\n"
            f"  Deleted: {deleted_str}\n"
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class ItemHandler:
    """
    Handles Item creation and modification.
    """

    @staticmethod
    def create_item(creator: str, name: str, quantity: int):
        backend = get_backend()
        iid = str(uuid.uuid4())
        quantity = quantity
        version = 0
        deleted = 0
        
        new_item = Item(iid, name, creator, quantity, version, deleted)
        item_as_dict = asdict(new_item)
        backend.write_item(creator, item_as_dict)
        return (iid, "[ItemHandler] Succesfully created new item with id " + iid)

    @staticmethod
    def delete_item(actor: str, iid: str):
        backend = get_backend()
        item = backend.get_item(actor, iid)
        if not item:
            return (-1, "[ItemHandler] The item with id " + iid + " does not exist on user " + actor + " replica.")

        if item.get("deleted_counter") % 2 == 1:
            return (-1, "[ItemHandler] The item with id " + iid + " is already deleted.")
        
        item["deleted_counter"] += 1
        backend.write_item(actor, item)
        return (1, "[ItemHandler] Succesfully deleted item " + iid)
    
    @staticmethod
    def reinstate_item(actor: str, iid: str):
        backend = get_backend()
        item = backend.get_item(actor, iid)
        if not item:
            return (-1, "[ItemHandler] The item with id " + iid + " does not exist on user " + actor + " replica.")

        if item.get("deleted_counter") % 2 == 0:
            return (-1, "[ItemHandler] The item with id " + iid + " is already active.")
        
        item["deleted_counter"] += 1
        backend.write_item(actor, item)
        return (1, "[ItemHandler] Succesfully reinstated item " + iid)

        

