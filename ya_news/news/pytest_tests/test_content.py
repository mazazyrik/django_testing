import pytest
from django.conf import settings
from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_on_home_page(client, news_date, url_home):
    response = client.get(url_home)
    news_on_page = response.context['object_list'].count()
    assert news_on_page == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_ordering(client, news_date, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_news = sorted(dates, reverse=True)
    assert dates == sorted_news


def test_comment_ordering(client, comment_date, url_detail):
    response = client.get(url_detail)
    news = response.context['news']
    comments = news.comment_set.all()
    assert [
        comments[i].created < comments[i + 1].created for i in range(
            len(comments) - 1
        )
    ]


def test_comment_form_for_anonym(client, news, url_detail):
    response = client.get(url_detail)
    context = response.context
    assert 'form' not in context


def test_comment_form_for_login_user(news, author_client, url_detail):
    response = author_client.get(url_detail)
    context = response.context
    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
