import pytest
from http import HTTPStatus


from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args_news')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
)
def test_pages_availability_for_anonymous_user(admin_client, name, args):
    """Проверяем, что мы можем зайти на ссылку."""
    url = reverse(name, args=args)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',

    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, id_for_args_comment, expected_status
):
    """Проверяем запрос сервера для автора новости и другого пользователя."""
    url = reverse(name, args=(id_for_args_comment))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_args_comment')),
    ),
)
def test_redirects_comment(client, name, args):
    """Проверяем, что анонимный пользователь перенаправляется на
    страницу для того, чтобы войти в учетную запись.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
