from pydantic import BaseModel

class Step(BaseModel):
    """
    A Step that belongs to a Task.
    """
    id : int
    url: str
    status: str