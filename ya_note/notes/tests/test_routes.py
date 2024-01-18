from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='author'
        )
        cls.user = User.objects.create(
            username='user'
        )
        cls.notes = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='1',
            author=cls.author
        )

    def test_pages(self):
        urls = ('notes:home',
                'users:login',
                'users:logout',
                'users:signup')
        for reverse_url in urls:
            with self.subTest(reverse_url=reverse_url):
                url = reverse(reverse_url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_success_add_for_loginus(self):
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )
        self.client.force_login(self.author)
        for reverse_url in urls:
            with self.subTest(reverse_url=reverse_url):
                url = reverse(reverse_url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_delete_for_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
        )
        urls = (
            ('notes:detail'),
            ('notes:edit'),
            ('notes:delete'),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for reverse_urls in urls:
                with self.subTest(user=user, reverse_urls=reverse_urls):
                    url = reverse(reverse_urls, args=(self.notes.slug))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous(self):
        urls = (
            ('notes:edit', (self.notes.slug)),
            ('notes:delete', (self.notes.slug)),
            ('notes:detail', (self.notes.slug)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for reverse_url, args in urls:
            with self.subTest(reverse_url=reverse_url, args=args):
                login_url = reverse('users:login')
                url = reverse(reverse_url, args=args)
                next_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, next_url)
