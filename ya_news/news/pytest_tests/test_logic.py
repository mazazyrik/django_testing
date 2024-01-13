from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_user_create_comment(author_client, form_date, news_id):
    cnt_before_comment = Comment.objects.count()
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_date)
    cnt_after_comment = Comment.objects.count()
    assertRedirects(response, url + '#comments')
    assert cnt_before_comment != cnt_after_comment


def test_anonymus_create_comment(client, form_date, news_id):
    cnt_before_comment = Comment.objects.count()
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_date)
    cnt_after_comment = Comment.objects.count()
    login_url = reverse('users:login')
    assertRedirects(response, f'{login_url}?next={url}')
    assert cnt_before_comment == cnt_after_comment


def test_create_comment_with_bad_word(author_client, news_id):
    url = reverse('news:detail', args=news_id)
    for word in BAD_WORDS:
        bad_word_text = {
            'text': word
        }
        response = author_client.post(url, data=bad_word_text)
        assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_edit_comment(
        author_client, comment_id, form_date, comment, news_id
):
    url = reverse('news:edit', args=comment_id)
    response = author_client.post(url, data=form_date)
    assertRedirects(response, reverse(
        'news:detail', args=news_id) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_date['text']


def test_author_can_delete_comment(
        author_client, comment_id, news_id, comment
):
    url = reverse('news:delete', args=comment_id)
    cnt_before_delete = Comment.objects.count()
    response = author_client.post(url)
    assertRedirects(response, reverse(
        'news:detail', args=news_id) + '#comments')
    cnt_after_delete = Comment.objects.count()
    assert cnt_before_delete != cnt_after_delete


def test_other_cant_edit_comment(
        admin_client, comment_id, form_date, comment
):
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url, data=form_date)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_other_cant_delete_comment(
        admin_client, comment_id, comment
):
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
