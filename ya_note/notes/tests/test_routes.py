from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_client = User.objects.create(username='Bogdan')
        cls.not_author_client = User.objects.create(
            username='Читатель простой'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Waking',
            author=cls.author_client
        )

    def test_pages_availability(self):
        """Проверяем доступность всех страниц."""
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author_client)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_page_edit_and_delete(self):
        """Проверяем, что автор может редактировать и удалять запись,
        а чужой пользователь не может.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяем, что мы получаем нужный нам переход на другую страницу."""
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_auth_user(self):
        """Проверяем доступность всех страниц."""
        names = (
            ('notes:list'), ('notes:add'), ('notes:success')
        )
        for url in names:
            with self.subTest(url=url):
                url = reverse(url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
