import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_data():
    return {
        'username': 'user1',
        'email': 'teste@teste.com',
        'password': '123456',
    }
