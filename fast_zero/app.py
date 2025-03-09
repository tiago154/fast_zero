from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, users
from fast_zero.schemas import Message

app = FastAPI()

app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    # Retorna uma resposta simples de "Hello World"
    return {'message': 'hello World'}
