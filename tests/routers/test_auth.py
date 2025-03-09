from http import HTTPStatus


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


def test_get_token_invalid(client, register_user):
    response = client.post(
        '/api/auth/token',
        data={'username': register_user.username, 'password': 'invalid'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect username or password'}
