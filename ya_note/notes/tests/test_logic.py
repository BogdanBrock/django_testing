from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreation(TestCase):
    TITLE = 'НеЗаголовок'
    TEXT = 'НеТекст'
    SLUG = 'NoWaking'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Bogdan')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.form_data['author'])


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'zagolovok'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Bogdan')
        cls.notes = Note.objects.create(
            title='НеЗаголовок',
            text='НеТекст',
            slug='nezagolovok',
            author=cls.user
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
            'author': cls.user
        }
        cls.url_edit = reverse('notes:edit', args=(cls.notes.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.notes.slug,))
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')

    def test_not_unique_slug(self):
        """Проверяем уникальность поля slug."""
        self.form_data['slug'] = self.notes.slug
        response = self.author_client.post(
            self.url_add,
            data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.notes.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Проверяем будет ли поле при пустом slug заполнено из поля text."""
        self.form_data.pop('slug', None)
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.first()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Проверяем может ли автор удалить запись."""
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверяем может ли другой пользователь удалить чужую запись."""
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Проверяем может ли автор редактировать запись."""
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_another_user(self):
        """Проверяем может ли другой
        пользователь редактировать чужую запись.
        """
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertNotEqual(self.notes.title, self.form_data['title'])
        self.assertNotEqual(self.notes.text, self.form_data['text'])
        self.assertNotEqual(self.notes.slug, self.form_data['slug'])
