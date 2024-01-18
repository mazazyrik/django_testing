from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify
TITLE = 'title'
TEXT = 'text'
SLUG = 'new-slug'


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

    def test_anonymous_user_cant_create_notes(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_notes(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        notes = Note.objects.get()
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
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.form_data['slug'] = self.notes.slug
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(
            self.notes.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
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

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args={'slug': self.note.slug})
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
        self.assertEqual(self.note.title, TITLE)
        self.assertEqual(self.note.slug, SLUG)

    def test_user_cant_edit_note(self):
        self.client.force_login(self.user)
        url = reverse('notes:edit', args={'slug': self.note.slug})
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args={'slug': self.note.slug})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note(self):
        self.client.force_login(self.user)
        url = reverse('notes:edit', args={'slug': self.note.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
