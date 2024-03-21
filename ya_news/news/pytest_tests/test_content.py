import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from news.models import News
from news.forms import CommentForm


def test_news_count(author_client):
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
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    print(news_count)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(author_client):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(not_author_client, id_for_args_news):
    url = reverse('news:detail', args=(id_for_args_news))
    response = not_author_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_args_news):
    url = reverse('news:detail', args=(id_for_args_news))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, id_for_args_news):
    url = reverse('news:detail', args=(id_for_args_news))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
