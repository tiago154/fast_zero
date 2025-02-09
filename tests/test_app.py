from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello World'}


def test_hello_html_deve_retornar_ola_mundo_em_html(client):
    response = client.get('/hello_html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Hello World</h1>' in response.text


def test_create_user(client, user_data):
    response = client.post(
        '/users',
        json=user_data,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': user_data['email'],
        'username': user_data['username'],
    }


def test_read_user(client, user_data):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': user_data['email'],
        'username': user_data['username'],
    }


def test_read_user_nao_encontrado_deve_retornar_not_found(client):
    response = client.get('/users/150')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users(client, user_data):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'email': user_data['email'],
                'username': user_data['username'],
            }
        ]
    }


def test_update_user(client, user_data):
    update_user_data = {
        'username': user_data['username'],
        'email': 'teste1@teste.com',
        'password': 'testPassword',
    }

    response = client.put('/users/1', json=update_user_data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': update_user_data['email'],
        'username': user_data['username'],
    }


def test_update_user_nao_encontrado_deve_retornar_not_found(client, user_data):
    response = client.put('/users/150', json=user_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_nao_encontrado_deve_retornar_not_found(client):
    response = client.delete('/users/150')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
