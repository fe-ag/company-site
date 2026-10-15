from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Article


class ArticleVisibilityTests(TestCase):
    def setUp(self):
        self.pub = Article.objects.create(title='Pub', slug='pub', excerpt='e', content='c', status='published')
        self.draft = Article.objects.create(title='Draft', slug='draft', excerpt='e', content='c', status='draft')
        self.future = Article.objects.create(title='Future', slug='future', excerpt='e', content='c', status='published',
                                             published_at=timezone.now() + timedelta(days=3))

    def test_list_shows_only_published(self):
        response = self.client.get('/articles/')
        self.assertContains(response, 'Pub')
        self.assertNotContains(response, 'Draft')
        self.assertNotContains(response, 'Future')

    def test_detail(self):
        self.assertEqual(self.client.get('/articles/pub/').status_code, 200)
        self.assertEqual(self.client.get('/articles/draft/').status_code, 404)
        self.assertEqual(self.client.get('/articles/future/').status_code, 404)
