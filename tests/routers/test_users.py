from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user(client, user_data):
    response = client.post(
        '/api/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': user_data['email'],
        'username': user_data['username'],
    }


def test_create_user_with_same_username(client, user_data, register_user):
    response = client.post(
        '/api/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User with this username already exists'}


def test_create_user_with_same_email(client, user_data, register_user):
    user_data['username'] = 'user2'
    response = client.post(
        '/api/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User with this email already exists'}


def test_read_user(client):
    response = client.get('/api/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users(client, user_data):
    response = client.get('/api/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_user_with_user(client, user_data, register_user):
    response = client.get('/api/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': user_data['email'],
        'username': user_data['username'],
    }


def test_read_user_nao_encontrado_deve_retornar_not_found(client):
    response = client.get('/api/users/150')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users_with_users(client, user_data, register_user):
    user_schema = UserPublic.model_validate(register_user).model_dump()
    response = client.get('/api/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user_data, register_user, token):
    update_user_data = {
        'username': user_data['username'],
        'email': 'teste1@teste.com',
        'password': 'testPassword',
    }

    response = client.put(
        f'/api/users/{register_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=update_user_data,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': update_user_data['email'],
        'username': user_data['username'],
    }


def test_update_user_com_usuario_errado(client, user_data, register_user, token):
    update_user_data = {
        'username': user_data['username'],
        'email': 'teste1@teste.com',
        'password': 'testPassword',
    }

    response = client.put(
        '/api/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json=update_user_data,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_delete_user(client, register_user, token):
    response = client.delete(
        f'/api/users/{register_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_com_usuario_errado(client, register_user, token):
    response = client.delete(
        '/api/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}
