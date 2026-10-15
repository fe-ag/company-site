from django.test import TestCase

from .models import PortfolioItem


class PortfolioVisibilityTests(TestCase):
    def test_inactive_items_hidden(self):
        PortfolioItem.objects.create(title='Shown one', slug='shown', summary='s', is_active=True)
        PortfolioItem.objects.create(title='Hidden one', slug='hidden', summary='s', is_active=False)
        response = self.client.get('/portfolio/')
        self.assertContains(response, 'Shown one')
        self.assertNotContains(response, 'Hidden one')
        self.assertEqual(self.client.get('/portfolio/shown/').status_code, 200)
        self.assertEqual(self.client.get('/portfolio/hidden/').status_code, 404)
