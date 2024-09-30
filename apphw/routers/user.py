from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from apphw.backend.bd_depends import get_bd
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from apphw.models import User, Task
from apphw.schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(bd: Annotated[Session, Depends(get_bd)]):
    users = bd.scalars(select(User)).all()
    return users


@router.get('/user_id/tasks')
async def tasks_by_user_id(bd: Annotated[Session, Depends(get_bd)], user_id: int):
    user = bd.scalar(select(User).where(User.id == user_id))
    if user is not None:
        all_tasks_user = bd.scalars(select(Task).where(Task.user_id == user_id)).all()
        return all_tasks_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task {user} was not found')


@router.get('/user_id')
async def user_by_id(bd: Annotated[Session, Depends(get_bd)], user_id: int):
    user = bd.scalar(select(User).where(User.id == user_id))
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')


@router.post('/create')
async def create_user(bd: Annotated[Session, Depends(get_bd)], create_user: CreateUser):
    bd.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))
    bd.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_user(bd: Annotated[Session, Depends(get_bd)], update_user: UpdateUser, user_id: int):
    user = bd.scalar(select(User).where(User.id == user_id))
    if user is not None:
        bd.execute(update(User).where(User.id == user_id).values(age=update_user.age,
                                                                 firstname=update_user.firstname,
                                                                 lastname=update_user.lastname))

        bd.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')


@router.delete('/delete')
async def delete_user(bd: Annotated[Session, Depends(get_bd)], user_id: int):
    user = bd.scalar(select(User).where(User.id == user_id))
    if user is not None:
        bd.execute(delete(User).where(User.id == user_id))
        bd.execute(delete(Task).where(Task.user_id == user_id))
        bd.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User delete is successful!'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User was not found')
