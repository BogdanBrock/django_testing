# conftest.py
import pytest
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def id_for_args_news(news):
    return (news.id,)


@pytest.fixture
def id_for_args_comment(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
