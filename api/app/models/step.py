from uuid import UUID

from pydantic import BaseModel

class Step(BaseModel):
    id : int
    url: str
    status: str