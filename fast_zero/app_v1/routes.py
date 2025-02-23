from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

# Criando um router
router = APIRouter()

# Banco de dados fictício (usado apenas como exemplo)
database = []

# Definição global para a resposta 404, reutilizada em várias rotas
USER_NOT_FOUND_RESPONSE = {
    404: {
        'description': 'User not found',
        'content': {
            'application/json': {'example': {'detail': 'User not found'}}
        },
    }
}


# Rota de exemplo, resposta simples com um JSON
@router.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    # Retorna uma resposta simples de "Hello World"
    return {'message': 'hello World'}


# Rota que retorna uma página HTML simples
@router.get('/hello_html', status_code=HTTPStatus.OK)
def hello_html():
    # Retorna uma resposta HTML como exemplo
    return """
    <html>
      <head>
        <title> Nosso olá mundo!</title>
      </head>
      <body>
        <h1>Hello World</h1>
      </body>
    </html>"""


# Rota POST para criar um novo usuário
@router.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    # O operador ** desempacota o dicionário retornado por user.model_dump()
    # e o usa como parâmetros
    # Isso evita a necessidade de passar cada chave manualmente
    # (ex: username, email, password)
    user_with_id = UserDB(
        id=len(database) + 1, **user.model_dump()
    )  # Criação do usuário com ID

    # Adiciona o novo usuário ao banco de dados simulado
    database.append(user_with_id)

    # Retorna o usuário criado, agora com um ID
    return user_with_id


# Rota GET para listar todos os usuários
@router.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def list_users():
    # A função print aqui é apenas para debug, pode ser removida em produção
    print(database)
    # Retorna a lista de usuários no formato esperado pela resposta
    return {'users': database}


# Rota GET para consultar um usuário específico pelo ID
@router.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        **USER_NOT_FOUND_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def read_user(user_id: int):
    # Verifica se o ID do usuário é válido, ou seja, se existe no banco de dados
    if user_id < 1 or user_id > len(database):
        # Se o ID não for válido, levanta uma exceção HTTP com código 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    # Retorna o usuário encontrado pelo ID
    return database[user_id - 1]


# Rota PUT para atualizar os dados de um usuário
@router.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        **USER_NOT_FOUND_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def update_user(user_id: int, user: UserSchema):
    # Verifica se o ID do usuário é válido, ou seja, se existe no banco de dados
    if user_id < 1 or user_id > len(database):
        # Se o ID não for válido, levanta uma exceção HTTP com código 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    # Atualiza os dados do usuário. O **user.model_dump() desempacota
    # o modelo UserSchema e passa para UserDB
    user_with_id = UserDB(id=user_id, **user.model_dump())
    # Substitui o usuário no banco de dados pelo atualizado
    database[user_id - 1] = user_with_id

    # Retorna o usuário atualizado
    return user_with_id


# Rota DELETE para deletar um usuário
@router.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={
        **USER_NOT_FOUND_RESPONSE
    },  # Resposta de erro personalizada se o usuário não for encontrado
)
def delete_user(user_id: int):
    # Verifica se o ID do usuário é válido, ou seja, se existe no banco de dados
    if user_id < 1 or user_id > len(database):
        # Se o ID não for válido, levanta uma exceção HTTP com código 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    # Remove o usuário do banco de dados
    database.pop(user_id - 1)

    # Retorna uma mensagem confirmando que o usuário foi deletado
    return {'message': 'User deleted'}
