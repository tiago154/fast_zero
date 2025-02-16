from pydantic import BaseModel, EmailStr


# Modelo para mensagens genéricas de resposta
class Message(BaseModel):
    message: str


# Schema para entrada de dados de um usuário (utilizado no cadastro)
class UserSchema(BaseModel):
    username: str  # Nome de usuário
    email: EmailStr  # E-mail (validação automática do formato pelo Pydantic)
    password: str  # Senha do usuário


# Modelo representando um usuário armazenado no banco de dados
class UserDB(UserSchema):
    id: int  # Identificador único do usuário


# Modelo para resposta pública de usuário (evita expor senha)
class UserPublic(BaseModel):
    id: int  # Identificador único do usuário
    username: str  # Nome de usuário
    email: EmailStr  # E-mail do usuário


# Modelo para representar uma lista de usuários públicos
class UserList(BaseModel):
    users: list[UserPublic]  # Lista de usuários sem informações sensíveis
