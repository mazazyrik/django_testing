from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_one = User.objects.create(
            username='user_one'
        )
        cls.user_two = User.objects.create(
            username='user_two'
        )
        cls.note_one = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.user_one
        )
        cls.note_two = Note.objects.create(
            title='title 2',
            text='text 2',
            slug='slug_2',
            author=cls.user_two
        )
        cls.user_one_client = Client()
        cls.user_two_client = Client()
        cls.user_one_client.force_login(cls.user_one)
        cls.user_two_client.force_login(cls.user_two)

    def test_edit_add_contains_form(self):
        reverses = (
            ('notes:edit', {'slug': self.note_one.slug}),
            ('notes:add', None)
        )
        for reverse_url, args in reverses:
            with self.subTest(reverse_url=reverse_url, args=args):
                url = reverse(reverse_url, args=args)
                response = self.user_one_client.get(url)
                self.assertIn('form', response.context)

    def test_notes_list_for_user_1(self):
        url = reverse('notes:list')
        response = self.user_one_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_one, object_list)
        self.assertNotIn(self.note_two, object_list)

    def test_notes_list_for_user_2(self):
        url = reverse('notes:list')
        response = self.user_two_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_two, object_list)
        self.assertNotIn(self.note_one, object_list)
