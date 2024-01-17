from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


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
    'reverse_url, parametrized_client, status',
    (
        (pytest.lazy_fixture('url_edit'), pytest.lazy_fixture(
            'author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_edit'), pytest.lazy_fixture(
            'admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('url_delete'), pytest.lazy_fixture(
            'author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_delete'), pytest.lazy_fixture(
            'admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('url_home'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_detail'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:signup'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (reverse('users:login'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:logout'), pytest.lazy_fixture('client'), HTTPStatus.OK)
    )
)
def test_avalible_for_anonym_and_edit_delete(
        reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status
