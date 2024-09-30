from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from apphw.backend.bd_depends import get_bd
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from apphw.models import Task, User
from apphw.schemas import CreateTask, UpdateTask
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_task(bd: Annotated[Session, Depends(get_bd)]):
    tasks = bd.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(bd: Annotated[Session, Depends(get_bd)], task_id: int):
    task = bd.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        return task
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')


@router.post('/create')
async def create_task(bd: Annotated[Session, Depends(get_bd)], create_task: CreateTask, user_id: int):
    user = bd.scalar(select(User).where(User.id == user_id))
    if user is not None:
        bd.execute(insert(Task).values(title=create_task.title,
                                       content=create_task.content,
                                       priority=create_task.priority,
                                       user_id=user_id,
                                       slug=slugify(create_task.title.lower())))
        bd.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')


@router.put('/update')
async def update_task(bd: Annotated[Session, Depends(get_bd)], update_task: UpdateTask, task_id: int):
    task = bd.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        bd.execute(update(Task).where(Task.id == task_id).values(title=update_task.title,
                                                                 content=update_task.content,
                                                                 priority=update_task.priority,
                                                                 slug=slugify(update_task.title.lower())))
        bd.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')


@router.delete('/delete')
async def delete_task(bd: Annotated[Session, Depends(get_bd)], task_id: int):
    task = bd.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        bd.execute(delete(Task).where(Task.id == task_id))
        bd.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task delete is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task was not found')
