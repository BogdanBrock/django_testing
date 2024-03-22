from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
    author_client,
    author,
    news,
    form_data,
    id_for_args_news
):
    """Проверяем, что автор может создавать комментарии."""
    url = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_news = Comment.objects.get()
    assert new_news.text == form_data['text']
    assert new_news.author == author
    assert new_news.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    form_data,
    id_for_args_news
):
    """Проверяем, что анонимный пользователь не может создавать комментарии."""
    url = reverse('news:detail', args=id_for_args_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'bad_words',
    (BAD_WORDS)
)
def test_user_cant_use_bad_words(author_client, bad_words, id_for_args_news):
    """Проверяем, что автор не может создавать комментарии,
    в которых содержатся слова из запрещенного списка.
    """
    url = reverse('news:detail', args=id_for_args_news)
    bad_words_data = {'text': f'Какой-то текст, {bad_words}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author,
    author_client,
    form_data,
    news,
    comment,
    id_for_args_comment,
    id_for_args_news
):
    """Проверяем, что автор может изменять комменатрии."""
    url = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(reverse(
        'news:edit',
        args=(id_for_args_comment)),
        form_data
    )
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_other_user_cant_edit_news(
    author,
    form_data,
    comment,
    id_for_args_comment,
    admin_client,
    news
):
    """Проверяем, анонимный пользователь не может изменять комменатрии."""
    url = reverse('news:edit', args=id_for_args_comment)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_text = comment.text
    comment.refresh_from_db()
    assert comment.text == comment_text
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_news(
    author_client,
    id_for_args_comment,
    id_for_args_news
):
    """Проверяем, что автор может удалять комменатрии."""
    url_delete = reverse('news:delete', args=id_for_args_comment)
    url_detail = reverse('news:detail', args=id_for_args_news)
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_news(
    admin_client,
    form_data,
    id_for_args_comment
):
    """Проверяем, анонимный пользователь не может удалять комменатрии."""
    url = reverse('news:delete', args=id_for_args_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
