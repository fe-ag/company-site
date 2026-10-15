from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from utils.validators import validate_safe_url, validate_hex_color
from .models import SiteSetting, ThemeSetting, NavLink
from .theme import build_theme_css


class ValidatorTests(TestCase):
    def test_javascript_url_rejected(self):
        for bad in ('javascript:alert(1)', 'data:text/html,x', '//evil.com', 'ftp://x'):
            with self.assertRaises(ValidationError):
                validate_safe_url(bad)

    def test_good_urls(self):
        for good in ('/about-us/', 'https://example.com', 'mailto:a@b.com', '#top'):
            validate_safe_url(good)

    def test_color(self):
        validate_hex_color('#aabbcc')
        with self.assertRaises(ValidationError):
            validate_hex_color('red; background:url(x)')


class ThemeTests(TestCase):
    def test_changes_reach_public_page(self):
        theme = ThemeSetting.load()
        theme.color_primary = '#123456'
        theme.save()
        self.assertIn('--primary:#123456', build_theme_css(theme))
        response = self.client.get('/')
        self.assertContains(response, '--primary:#123456')

    def test_menu_link_inactive_hidden(self):
        NavLink.objects.create(title='Hidden', url='/x/', is_active=False)
        NavLink.objects.create(title='Shown', url='/y/', is_active=True)
        response = self.client.get('/')
        self.assertContains(response, 'Shown')
        self.assertNotContains(response, 'Hidden')
