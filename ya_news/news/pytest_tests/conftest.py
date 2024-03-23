from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст',
        author=author,
        news=news
    )


@pytest.fixture
def id_for_args_news(news):
    return (news.id,)


@pytest.fixture
def id_for_args_comment(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }


@pytest.fixture
def count_news():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def count_comments(news, author):
    today = datetime.today()
    all_comments = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment(
            text=f'Комментарий {index}',
            created=today - timedelta(days=index),
            news=news,
            author=author
        )
        all_comments.append(comment)
    Comment.objects.bulk_create(all_comments)
