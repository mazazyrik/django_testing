from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None)
    )
)
def test_pages_for_anonym(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id'))
    )
)
def test_comment_edit_delete_redirect(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    login = reverse('users:login')
    assertRedirects(response, f'{login}?next={url}')


@pytest.mark.parametrize(
    'custom_client, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id'))
    )
)
def test_edit_delete_for_different_roles_users(
    custom_client,
    status,
    name,
    args
):
    url = reverse(name, args=args)
    response = custom_client.get(url)
    assert response.status_code == status
