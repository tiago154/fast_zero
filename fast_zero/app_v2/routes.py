from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter()


# Definição global para a resposta 400
BAD_REQUEST_CREATE_USER_RESPONSE = {
    400: {
        'description': 'Invalid input data',
        'content': {
            'application/json': {
                'examples': {
                    'username_exists': {
                        'summary': 'User with this username already exists',
                        'value': {
                            'detail': 'User with this username already exists'
                        },
                    },
                    'email_exists': {
                        'summary': 'User with this email already exists',
                        'value': {
                            'detail': 'User with this email already exists'
                        },
                    },
                }
            }
        },
    }
}

# Definição global para a resposta 404, reutilizada em várias rotas
USER_NOT_FOUND_RESPONSE = {
    404: {
        'description': 'User not found',
        'content': {
            'application/json': {'example': {'detail': 'User not found'}}
        },
    }
}

USER_NOT_ENOUGH_PERMISSION_RESPONSE = {
    400: {
        'description': 'Not enough permission',
        'content': {
            'application/json': {'example': {'detail': 'Not enough permission'}}
        },
    }
}


# Rota de exemplo, resposta simples com um JSON
@router.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    # Retorna uma resposta simples de "Hello World"
    return {'message': 'hello World'}


@router.post(
    '/users',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={**BAD_REQUEST_CREATE_USER_RESPONSE},
)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='User with this username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='User with this email already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


# Rota GET para listar todos os usuários
@router.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(limit: int = 10, skip: int = 0, session=Depends(get_session)):
    users = session.scalars(select(User).limit(limit).offset(skip))

    return {'users': users}


# Rota GET para consultar um usuário específico pelo ID
@router.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        **USER_NOT_FOUND_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def read_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return user


# Rota PUT para atualizar os dados de um usuário
@router.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        **USER_NOT_ENOUGH_PERMISSION_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def update_user(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Not enough permission',
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


# Rota DELETE para deletar um usuário
@router.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={
        **USER_NOT_ENOUGH_PERMISSION_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Not enough permission',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted successfully'}


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session),
):
    user = session.scalar(select(User).where(User.username == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'Bearer'}
