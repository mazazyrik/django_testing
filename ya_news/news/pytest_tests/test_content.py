import pytest
from django.urls import reverse
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_news_on_home_page(client, news_count):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_on_page = len(object_list)
    assert news_on_page == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_ordering(client, news_date):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_news = sorted(dates, reverse=True)
    assert dates == sorted_news


def test_comment_ordering(client, comment_date, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    news = response.context['news']
    comments = news.comment_set.all()
    assert (
        comments[0].created < comments[1].created < comments[2].created
    )


def test_comment_form_for_anonym(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    context = response.context
    assert 'form' not in context


def test_comment_form_for_login_user(client, news, author_client):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    context = response.context
    assert 'form' in context
