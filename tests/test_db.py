from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User, time=datetime(2025, 2, 23)) as time:
        user = User(
            username='user_test', email='email@test.com', password='password_test'
        )

        session.add(user)
        session.commit()

    result = session.scalar(select(User).where(User.username == 'user_test'))

    assert asdict(result) == {
        'id': 1,
        'username': 'user_test',
        'password': 'password_test',
        'email': 'email@test.com',
        'created_at': time,
        'updated_at': time,
    }
