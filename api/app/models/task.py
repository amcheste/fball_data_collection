import uuid
from copy import deepcopy
from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.models.step import Step

class TaskInput(BaseModel):
    command: str
    data_type: str



class Task(BaseModel):
    id: uuid.UUID
    command: str
    data_type: str
    status: str
    time_created: datetime
    time_modified: datetime

    def to_detailed(self, open_steps: int, total_steps: int, steps: List[Step]):
        return TaskDetailed(
            id=deepcopy(self.id),
            command=deepcopy(self.command),
            data_type=deepcopy(self.data_type),
            status=deepcopy(self.status),
            time_created=deepcopy(self.time_created),
            time_modified=deepcopy(self.time_modified),
            open_steps=open_steps,
            total_steps=total_steps,
            steps=steps
        )


class TaskDetailed(Task):
    open_steps: int
    total_steps: int
    steps: List[Step]