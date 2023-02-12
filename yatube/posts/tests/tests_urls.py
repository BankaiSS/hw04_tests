from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='slug',
            description='Тестовое описание',
        )
        user_ob = User.objects
        cls.author = user_ob.create_user(username='auth')
        cls.no_author = user_ob.create_user(username='noauth')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.url_edit_post = f'/posts/{str(cls.post.id)}/edit/'
        cls.url_expected_for_redirect = f'/posts/{cls.post.id}/'
        cls.url_404 = '/unexisting_page/'

        cls.templates_url_names_public = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }
        cls.templates_url_names_private = {
            cls.url_edit_post: 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            cls.url_edit_post: 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.no_author_client = Client()
        self.no_author_client.force_login(self.no_author)

    def test_url_uses_correct_redirect_for_edit_post_page(self):

        response = self.no_author_client.get(
            self.url_edit_post, follow=True
        )
        self.assertRedirects(
            response,
            expected_url=self.url_expected_for_redirect
        )

    def test_url_uses_correct_redirect(self):

        for url, template in self.templates_url_names_private.items():

            with self.subTest(url=url, user='anonymous'):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_urls_use_correct_template(self):

        for url, template in self.templates_url_names_public.items():
            with self.subTest(url=url, user='anon'):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

            with self.subTest(url=url, user='auth'):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_unexisting_page_404(self):
        """Проверка на несуществующую страницу."""

        response = self.guest_client.get(self.url_404)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates_url_names(self):
        """Проверка на доступнотсь ссылок авторизованному пользователю."""

        for url, template in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates_url_names_public(self):
        """Проверка на доступнотсь ссылок гостевому пользователю."""

        for url, template in self.templates_url_names_public.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
