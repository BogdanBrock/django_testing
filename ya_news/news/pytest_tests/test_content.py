import pytest

from django.conf import settings
from django.urls import reverse
from news.models import News

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(admin_client, count_news):
    """Проверяем, что количество записей не больше 10."""
    News.objects.bulk_create(count_news)
    url = reverse('news:home')
    response = admin_client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(admin_client):
    """Проверяем сортировку записей."""
    url = reverse('news:home')
    response = admin_client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(admin_client, id_for_args_news):
    """Проверяем сортировку комментариев."""
    url = reverse('news:detail', args=(id_for_args_news))
    response = admin_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_args_news):
    """Проверяем, что содержится ли форма в контексте."""
    url = reverse('news:detail', args=(id_for_args_news))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, id_for_args_news):
    """Проверяем, что является ли форма объектом класса CommentForm."""
    url = reverse('news:detail', args=(id_for_args_news))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
