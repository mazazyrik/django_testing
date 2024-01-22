from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

TITLE = 'title'
TEXT = 'text'
SLUG = 'new-slug'

NOTES_ADD = 'notes:add'
NOTES_SUCCESS = 'notes:success'
NOTES_EDIT = 'notes:edit'
NOTES_DELETE = 'notes:delete'
NOTES_HOME = 'notes:home'
NOTES_LIST = 'notes:list'
NOTES_DETAIL = 'notes:detail'

USERS_LOGOUT = 'users:logout'
USERS_SIGNUP = 'users:signup'
USERS_LOGIN = 'users:login'


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.form_data = {
            'title': TITLE,
            'text': TEXT,
            'slug': SLUG
        }
        cls.user = User.objects.create(username='user')
        cls.author_client = Client()
        cls.user_client = Client()
        cls.author_client.force_login(cls.author)

    def test_anonymous_user_cant_create_notes(self):
        url = reverse(NOTES_ADD)
        notes_count_bef = Note.objects.count()
        response = self.client.post(url, data=self.form_data)
        login_url = reverse(USERS_LOGIN)
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_bef)

    def test_user_can_create_notes(self):
        url = reverse(NOTES_ADD)
        notes_count_bef = Note.objects.count()
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count_bef + 1, notes_count)
        notes = Note.objects.last()
        self.assertEqual(notes.text, TEXT)
        self.assertEqual(notes.title, TITLE)
        self.assertEqual(notes.slug, SLUG)
        self.assertEqual(notes.author, self.author)

    def test_not_unique_slug(self):
        self.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        url = reverse(NOTES_ADD)
        notes_count_bef = Note.objects.count()
        self.form_data['slug'] = self.notes.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(
            self.notes.slug + WARNING))
        self.assertEqual(notes_count_bef, Note.objects.count())

    def test_empty_slug(self):
        url = reverse(NOTES_ADD)
        notes_count_bef = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS))
        self.assertEqual(notes_count_bef + 1, Note.objects.count())
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestLogicEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.form_data = {
            'title': TITLE,
            'text': TEXT,
            'slug': SLUG
        }
        cls.user = User.objects.create(username='user')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.author_client = Client()
        cls.user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)

    def test_author_can_edit_note(self):
        url = reverse(NOTES_EDIT, args={'slug': self.note.slug})
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
        self.assertEqual(self.note.title, TITLE)
        self.assertEqual(self.note.slug, SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_note(self):
        url = reverse(NOTES_EDIT, args={'slug': self.note.slug})
        response = self.user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        url = reverse(NOTES_DELETE, args={'slug': self.note.slug})
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse(NOTES_SUCCESS))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note(self):
        url = reverse(NOTES_EDIT, args={'slug': self.note.slug})
        notes_count_bef = Note.objects.count()
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_bef, Note.objects.count())
