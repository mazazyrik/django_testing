from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(
            username='user_1'
        )
        cls.user_2 = User.objects.create(
            username='user_2'
        )
        cls.note_1 = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.user_1
        )
        cls.note_2 = Note.objects.create(
            title='title 2',
            text='text 2',
            slug='slug_2',
            author=cls.user_2
        )

    def test_edit_add_contains_form(self):
        reverses = (
            ('notes:edit', {'slug': self.note_1.slug}),
            ('notes:add', None)
        )
        for reverse_url, args in reverses:
            self.client.force_login(self.user_1)
            with self.subTest(reverse_url=reverse_url, args=args):
                url = reverse(reverse_url, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_notes_list_for_user_1(self):
        url = reverse('notes:list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_1, object_list)
        self.assertNotIn(self.note_2, object_list)

    def test_notes_list_for_user_2(self):
        url = reverse('notes:list')
        self.client.force_login(self.user_2)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_2, object_list)
        self.assertNotIn(self.note_1, object_list)
