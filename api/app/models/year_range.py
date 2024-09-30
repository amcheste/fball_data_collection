from pydantic import BaseModel

class YearRange(BaseModel):
    """
    Range of years object.

    :param start: Starting year.
    :param end: Ending year.
    """
    start: int
    end: int