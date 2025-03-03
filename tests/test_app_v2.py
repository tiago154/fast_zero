from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/api/v2')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello World'}


def test_create_user(client, user_data):
    response = client.post(
        '/api/v2/users',
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
        '/api/v2/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User with this username already exists'}


def test_create_user_with_same_email(client, user_data, register_user):
    user_data['username'] = 'user2'
    response = client.post(
        '/api/v2/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User with this email already exists'}


def test_read_user(client, user_data):
    response = client.get('/api/v2/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users(client, user_data):
    response = client.get('/api/v2/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_user_with_user(client, user_data, register_user):
    response = client.get('/api/v2/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': user_data['email'],
        'username': user_data['username'],
    }


def test_read_user_nao_encontrado_deve_retornar_not_found(client):
    response = client.get('/api/v2/users/150')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users_with_users(client, user_data, register_user):
    user_schema = UserPublic.model_validate(register_user).model_dump()
    response = client.get('/api/v2/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user_data, register_user, token):
    update_user_data = {
        'username': user_data['username'],
        'email': 'teste1@teste.com',
        'password': 'testPassword',
    }

    response = client.put(
        f'/api/v2/users/{register_user.id}',
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
        '/api/v2/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json=update_user_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permission'}


def test_delete_user(client, register_user, token):
    response = client.delete(
        f'/api/v2/users/{register_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_com_usuario_errado(client, register_user, token):
    response = client.delete(
        '/api/v2/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permission'}


def test_get_token(client, register_user):
    response = client.post(
        '/api/v2/token',
        data={
            'username': register_user.username,
            'password': register_user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_invalid(client, register_user):
    response = client.post(
        '/api/v2/token',
        data={'username': register_user.username, 'password': 'invalid'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}
