from uuid import UUID
from typing import List

from fastapi import APIRouter, status, HTTPException
import json
from app.daos.tasks import *
from app.models import Task, TaskInput, TaskDetailed, Queue

router = APIRouter(
    prefix="/nfl_data/v1/tasks",
    tags=["tasks"],
)

@router.get(
    "/",
    summary="List all tasks",
    response_model=List[Task],
    status_code=status.HTTP_200_OK,
    tags=['tasks']
)
async def list_tasks() -> List[Task]:
    tasks = await get_tasks()

    return tasks

@router.get(
    "/{task_id}",
    summary="Retrieve a task",
    #response_model=TaskDetailed,
    status_code=status.HTTP_200_OK,
    tags=['tasks']
)
async def get_task(task_id: UUID):
    task = await query_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Task {task_id} not found',
        )

    #
    # Get open steps
    open_steps = await get_open_step_count(task_id, task.data_type)
    print(open_steps)

    #
    # Get step list
    steps = await get_step_list(task_id, task.data_type)
    print(steps)
    #
    # Get total count of steps
    if steps is not None:
        total_steps = len(steps)
    else:
        total_steps = 0

    #
    # Create a more detailed task object
    task = task.to_detailed(open_steps, total_steps, steps)

    return task


@router.post(
    "/",
    summary="Create a new task",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=['tasks']
)
async def add_task(task: TaskInput) -> Task:
    task = await create_task(command=task.command, data_type=task.data_type)

    #
    # Add it to the task processing queue.
    queue = Queue('tasks')
    queue.connect()
    data = {
        'id': f"{task.id}",
        'command': task.command,
        'data_type': task.data_type,
    }
    queue.publish(json.dumps(data))

    return task