from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Bogdan')
        cls.reader = User.objects.create(username='NoBogdan')
        cls.notes = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='waking',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.reader)
        cls.url_create = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.notes.slug,))
        cls.url_list = reverse('notes:list')

    def test_note_in_list_(self):
        """Проверяем есть ли заметка в объектном листе."""
        users = (
            (self.author_client, True),
            (self.not_author_client, False)
        )
        for user, expected_result in users:
            with self.subTest(user=user):
                response = user.get(self.url_list)
                object_list = response.context['object_list']
                self.assertIs(self.notes in object_list, expected_result)

    def test_author_client_has_form(self):
        """Проверяем есть ли форма в контексте,
        а так же является ли форма объектом класса NoteForm.
        """
        urls = (
            (self.url_create), (self.url_edit)
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
