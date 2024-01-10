import pytest
from news.models import News, Comment
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

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
