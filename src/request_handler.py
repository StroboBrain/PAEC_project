import uuid
from dataclasses import dataclass, asdict
from typing import Dict
from storage_provider import get_backend

@dataclass
class Request:
    rrid: str
    name: str
    sender: str
    iid: str
    change_amount: int
    processed: bool

    def __str__(self):
        status = "Processed" if self.processed else "Pending"
        return (
            f"  Request '{self.name}' (id={self.rrid})\n"
            f"  Sender: {self.sender}\n"
            f"  Change amount: {self.change_amount:+}\n"
            f"  Status: {status}\n"
        )

class RequestHandler:
    """
    Handles Request creation and processing.
    """

    @staticmethod
    def create_request(sender: str, iid: str, item_name: str, request_name: str, change_amount: int):
        backend = get_backend()
        rrid = str(uuid.uuid4())
        
        new_request = Request(
            rrid=rrid, 
            name=request_name, 
            sender=sender, 
            iid=iid, 
            change_amount=change_amount, 
            processed=False
        )
        request_as_dict = asdict(new_request)
        backend.write_request(sender, request_as_dict)
        return (rrid, f"[RequestHandler] Successfully created new request '{request_name}'")
    
    @staticmethod
    def process_request(actor: str, rrid: str, accept: bool):
        backend = get_backend()
        request = backend.get_request(actor, rrid)
        if not request:
            return (-1, f"[RequestHandler] Request {rrid} does not exist.")

        iid = request.get("iid")
        item = backend.get_item(actor, iid)

        if not item:
            return (-1, f"[RequestHandler] Item {iid} does not exist.")
        if not item.get("creator") == actor:
            return (-1, f"[RequestHandler] User {actor} is not the creator and cannot process this.")
        if request.get("processed"):
            return (-1, f"[RequestHandler] Request {rrid} is already processed.")
        if item.get("quantity") - request.get("change_amount") >= 0:
            return (-1, f"[RequestHandler] Cannot process request {rrid} as the item quantity would become negative")
        
        # If user chooses to deny it, we mark it processed without altering the item
        if not accept:
            request["processed"] = True
            backend.write_request(actor, request)
            return (rrid, f"[RequestHandler] Request '{request.get('name')}' was denied.")
        
        
        request["processed"] = True
        item["quantity"] += request.get("change_amount")
        item["version"] += 1
        
        backend.write_request(actor, request)
        backend.write_item(actor, item)
        return (rrid, f"[RequestHandler] Successfully applied request '{request.get('name')}'")
