import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import News, Comment


def test_user_can_create_news(
    author_client,
    author,
    news,
    form_data,
    id_for_args_news
):
    url = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_news = Comment.objects.get()
    assert new_news.text == form_data['text']
    assert new_news.author == author
    assert new_news.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_news(client, form_data, id_for_args_news):
    url = reverse('news:detail', args=id_for_args_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, id_for_args_news):
    url = reverse('news:detail', args=id_for_args_news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_note(
    author_client, form_data,
    comment, id_for_args_comment,
    id_for_args_news
):
    url = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(reverse(
        'news:edit',
        args=(id_for_args_comment)),
        form_data
    )
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(
    not_author_client, form_data,
    news, id_for_args_comment
):
    url = reverse('news:edit', args=id_for_args_comment)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = News.objects.get(id=news.id)
    assert news.text == note_from_db.text


def test_author_can_delete_note(
    author_client,
    id_for_args_comment,
    id_for_args_news
):
    url_delete = reverse('news:delete', args=id_for_args_comment)
    url_detail = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(
    not_author_client,
    form_data,
    id_for_args_comment
):
    url = reverse('news:delete', args=id_for_args_comment)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
