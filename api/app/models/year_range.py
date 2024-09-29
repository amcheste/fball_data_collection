from pydantic import BaseModel

class YearRange(BaseModel):
    start: int
    end: int