from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, register_user):
    response = client.post(
        '/api/auth/token',
        data={
            'username': register_user.username,
            'password': register_user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_invalid_password(client, register_user):
    response = client.post(
        '/api/auth/token',
        data={'username': register_user.username, 'password': 'invalid'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_token_invalid_username(client, register_user):
    response = client.post(
        '/api/auth/token',
        data={'username': 'invalid', 'password': register_user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_token_expired_after_time(client, register_user):
    with freeze_time('2025-03-11 12:00:00'):
        response = client.post(
            '/api/auth/token',
            data={
                'username': register_user.username,
                'password': register_user.clean_password,
            },
        )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token

    with freeze_time('2025-03-11 12:31:00'):
        response = client.put(
            f'/api/users/{register_user.id}',
            headers={'Authorization': f'Bearer {token["access_token"]}'},
            json={
                'username': 'wrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, token):
    response = client.post(
        '/api/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_refresh_token_invalid_token(client):
    response = client.post(
        '/api/auth/refresh_token',
        headers={'Authorization': 'Bearer token-invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token_expired(client, register_user):
    with freeze_time('2025-03-11 12:00:00'):
        response = client.post(
            '/api/auth/token',
            data={
                'username': register_user.username,
                'password': register_user.clean_password,
            },
        )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token

    with freeze_time('2025-03-11 12:31:00'):
        response = client.post(
            '/api/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
