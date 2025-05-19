from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.dependencies import get_filters
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    Message,
    TodoFilters,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[Session, Depends(get_session)]
T_User = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
def create_todo(todo: TodoSchema, session: T_Session, user: T_User):
    db_todo = Todo(user_id=user.id, **todo.model_dump())

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(
    session: T_Session,
    user: T_User,
    filters: Annotated[TodoFilters, Depends(get_filters)],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if filters.title:
        query = query.where(Todo.title.contains(filters.title))
    if filters.description:
        query = query.where(Todo.description.contains(filters.description))
    if filters.state:
        query = query.where(Todo.state == filters.state)

    todos = session.scalars(
        query.offset(filters.offset).limit(filters.limit)
    ).all()

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    todo_id: int,
    session: T_Session,
    user: T_User,
):
    query = select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)

    todo = session.scalar(query)

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    session.delete(todo)
    session.commit()

    return {'message': 'Task has been deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def update_todo(todo_id: int, session: T_Session, user: T_User, todo: TodoUpdate):
    db_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
