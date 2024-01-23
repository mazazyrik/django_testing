from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.tests.test_logic import (NOTES_ADD, NOTES_DELETE, NOTES_DETAIL,
                                    NOTES_EDIT, NOTES_HOME, NOTES_LIST,
                                    NOTES_SUCCESS, USERS_LOGIN, USERS_LOGOUT,
                                    USERS_SIGNUP)

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
        cls.author_client = Client()
        cls.user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)

    def test_pages(self):
        urls = (NOTES_HOME,
                USERS_LOGIN,
                USERS_LOGOUT,
                USERS_SIGNUP)
        for reverse_url in urls:
            with self.subTest(reverse_url=reverse_url):
                url = reverse(reverse_url)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_success_add_for_loginus(self):
        urls = (
            (NOTES_LIST),
            (NOTES_SUCCESS),
            (NOTES_ADD),
        )
        for reverse_url in urls:
            with self.subTest(reverse_url=reverse_url):
                url = reverse(reverse_url)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_delete_for_author(self):
        urls = (
            (NOTES_DETAIL),
            (NOTES_EDIT),
            (NOTES_DELETE),
        )
        for reverse_urls in urls:
            with self.subTest(user=self.author, reverse_urls=reverse_urls):
                url = reverse(reverse_urls, args=(self.notes.slug))
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_edit_delete_for_user(self):
        urls = (
            (NOTES_DETAIL),
            (NOTES_EDIT),
            (NOTES_DELETE),
        )
        for reverse_urls in urls:
            with self.subTest(user=self.user, reverse_urls=reverse_urls):
                url = reverse(reverse_urls, args=(self.notes.slug))
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous(self):
        urls = (
            (NOTES_EDIT, (self.notes.slug)),
            (NOTES_DELETE, (self.notes.slug)),
            (NOTES_DETAIL, (self.notes.slug)),
            (NOTES_LIST, None),
            (NOTES_SUCCESS, None),
            (NOTES_ADD, None),
        )
        for reverse_url, args in urls:
            with self.subTest(reverse_url=reverse_url, args=args):
                login_url = reverse(USERS_LOGIN)
                url = reverse(reverse_url, args=args)
                next_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, next_url)
