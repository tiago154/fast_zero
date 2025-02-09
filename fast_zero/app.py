from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database = []

# Definição global para a resposta 404
USER_NOT_FOUND_RESPONSE = {
    404: {
        'description': 'User not found',
        'content': {
            'application/json': {'example': {'detail': 'User not found'}}
        },
    }
}


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'hello World'}


@app.get('/hello_html', status_code=HTTPStatus.OK)
def hello_html():
    return """
    <html>
      <head>
        <title> Nosso olá mundo!</title>
      </head>
      <body>
        <h1>Hello World</h1>
      </body>
    </html>"""


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(id=len(database) + 1, **user.model_dump())

    database.append(user_with_id)

    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def list_users():
    print(database)
    return {'users': database}


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={**USER_NOT_FOUND_RESPONSE},
)
def read_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={**USER_NOT_FOUND_RESPONSE},
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(id=user_id, **user.model_dump())
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={**USER_NOT_FOUND_RESPONSE},
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    database.pop(user_id - 1)

    return {'message': 'User deleted'}
