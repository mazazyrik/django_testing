from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def news_count():
    ten_news = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость № {i}', text='ТЕКСТ')
        ten_news.append(news)
    News.objects.bulk_create(ten_news)


@pytest.fixture
def news_date():
    today = datetime.today()
    ten_news = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость № {i}',
            text='ТЕКСТ',
            date=today - timedelta(days=i)
        )
        ten_news.append(news)
    News.objects.bulk_create(ten_news)


@pytest.fixture
def author():
    return User.objects.create(username='test')


@pytest.fixture
def news():
    return News.objects.create(
        title='test',
        text='test'
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        text='test',
        news=news,
        author=author
    )


@pytest.fixture
def comment_date(author, news):
    now = timezone.now()
    for i in range(3):
        comment = Comment.objects.create(
            text=f'Комментарий № {i}',
            news=news,
            author=author
        )
        comment.created = now + timedelta(hours=i)
        comment.save()


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def news_id(news):
    return news.pk,


@pytest.fixture
def comment_id(comment):
    return comment.pk,


@pytest.fixture
def form_date():
    return {'text': 'ТЕКСТ'}
