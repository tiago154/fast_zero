from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='user_test', email='email@test.com', password='password_test'
    )

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.username == 'user_test'))

    assert result.id == 1
