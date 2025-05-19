from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post(
        '/api/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test description',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()

    assert data['id'] == 1
    assert data['title'] == 'Test todo'
    assert data['description'] == 'Test description'
    assert data['state'] == 'draft'

    assert 'created_at' in data
    assert 'updated_at' in data


def test_list_todos_should_return_5_todos(session, client, register_user, token):
    expected_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=register_user.id)
    )

    session.commit()

    response = client.get(
        '/api/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_list_todos_pagination_should_return_2_todos(
    session, client, register_user, token
):
    expected_todos = 2

    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=register_user.id)
    )

    session.commit()

    response = client.get(
        '/api/todos?limit=2&offset=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_list_todos_filter_title_should_return_3_todos(
    session, client, register_user, token
):
    expected_todos = 3

    session.bulk_save_objects(
        TodoFactory.create_batch(2, user_id=register_user.id, title='fake title')
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(3, user_id=register_user.id, title='Test todo')
    )

    session.commit()

    response = client.get(
        '/api/todos?title=Test todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_list_todos_filter_description_should_return_2_todos(
    session, client, register_user, token
):
    expected_todos = 2

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3, user_id=register_user.id, description='fake desc'
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            2, user_id=register_user.id, description='Test description'
        )
    )

    session.commit()

    response = client.get(
        '/api/todos?description=Test desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_list_todos_filter_state_should_return_4_todos(
    session, client, register_user, token
):
    expected_todos = 4

    session.bulk_save_objects(
        TodoFactory.create_batch(
            2, user_id=register_user.id, state=TodoState.draft
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            4, user_id=register_user.id, state=TodoState.doing
        )
    )

    session.commit()

    response = client.get(
        f'/api/todos?state={TodoState.doing.value}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_list_todos_filter_combined_should_return_3_todos(
    session, client, register_user, token
):
    expected_todos = 3

    session.bulk_save_objects(
        TodoFactory.create_batch(
            2,
            user_id=register_user.id,
            title='Test todo',
            description='Test desc',
            state=TodoState.draft,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=register_user.id,
            title='Test todo',
            description='Test desc',
            state=TodoState.doing,
        )
    )

    session.commit()

    response = client.get(
        '/api/todos?title=Test todo&description=Test desc&state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
    assert response.status_code == HTTPStatus.OK


def test_delete_todo(session, client, register_user, token):
    todo = TodoFactory(user_id=register_user.id)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(
        f'/api/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_delete_todo_error(client, token):
    response = client.delete(
        '/api/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_todo(session, client, register_user, token):
    todo = TodoFactory(user_id=register_user.id, state=TodoState.draft)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/api/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Updated title', 'description': 'Updated description'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['id'] == todo.id
    assert data['title'] == 'Updated title'
    assert data['description'] == 'Updated description'
    assert data['state'] == TodoState.draft.value

    assert 'created_at' in data
    assert 'updated_at' in data


def test_patch_todo_error(client, token):
    response = client.patch(
        '/api/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
