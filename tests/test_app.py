from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'hello World'}


def test_hello_html_deve_retornar_ola_mundo_em_html():
    client = TestClient(app)

    response = client.get('/hello_html')

    assert response.status_code == HTTPStatus.OK
    assert '<h1>Hello World</h1>' in response.text
