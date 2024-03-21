from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


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
        cls.url_detail = reverse('notes:detail', args=(cls.notes.slug,))
        cls.url_list = reverse('notes:list')

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_anonymous_client_has_no_form(self):
        response = self.not_author_client.get(self.url_detail)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.url_create)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
