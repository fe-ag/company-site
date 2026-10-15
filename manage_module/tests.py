from django.contrib.auth import get_user_model
import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from article_module.models import Article
from portfolio_module.models import PortfolioItem
from site_module.models import SiteSetting, ThemeSetting, NavLink

PROTECTED = ['manage_dashboard', 'manage_article_list', 'manage_article_create', 'manage_media_list', 'manage_content',
             'manage_appearance', 'manage_navigation', 'manage_message_list', 'manage_account', 'manage_portfolio_list', 'manage_portfolio_create']


class AccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user('staff', password='pass12345!x', is_staff=True)
        User.objects.create_user('visitor', password='pass12345!x')

    def test_anonymous_redirected_to_login(self):
        for name in PROTECTED:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn('/manage/login/', response['Location'])

    def test_non_staff_forbidden(self):
        self.client.login(username='visitor', password='pass12345!x')
        for name in PROTECTED:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)

    def test_staff_can_open_everything(self):
        self.client.login(username='staff', password='pass12345!x')
        for name in PROTECTED:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_django_admin_not_available(self):
        self.assertEqual(self.client.get('/admin/').status_code, 404)


class PanelActionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user('staff', password='pass12345!x', is_staff=True)
        self.client.login(username='staff', password='pass12345!x')

    def test_article_lifecycle(self):
        data = {'title': 'T', 'slug': 't', 'excerpt': 'ex', 'content': 'body', 'status': 'draft',
                'published_at': '2020-01-01T10:00', 'seo_title': '', 'meta_description': ''}
        self.client.post(reverse('manage_article_create'), data)
        article = Article.objects.get(slug='t')
        self.assertEqual(self.client.get('/articles/t/').status_code, 404)
        self.client.post(reverse('manage_article_toggle', args=[article.pk]))
        self.assertEqual(self.client.get('/articles/t/').status_code, 200)
        self.client.post(reverse('manage_article_toggle', args=[article.pk]))
        self.assertEqual(self.client.get('/articles/t/').status_code, 404)
        self.assertEqual(self.client.get(reverse('manage_article_delete', args=[article.pk])).status_code, 200)
        self.assertTrue(Article.objects.filter(pk=article.pk).exists())  # GET only asks for confirmation
        self.client.post(reverse('manage_article_delete', args=[article.pk]))
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())

    def test_dangerous_link_rejected(self):
        self.client.post(reverse('manage_nav_create'), {'title': 'X', 'url': 'javascript:alert(1)', 'order': 0, 'is_active': 'on'})
        self.assertFalse(NavLink.objects.exists())

    def test_invalid_color_rejected(self):
        theme = ThemeSetting.load()
        response = self.client.get(reverse('manage_appearance'))
        data = {f.name: getattr(theme, f.name) for f in ThemeSetting._meta.fields if f.name != 'id'}
        data['color_primary'] = 'blue'
        response = self.client.post(reverse('manage_appearance'), data)
        self.assertEqual(response.status_code, 200)
        theme.refresh_from_db()
        self.assertEqual(theme.color_primary, '#1f5eff')


    def test_restore_defaults_only_chosen_groups(self):
        theme = ThemeSetting.load()
        theme.color_primary = '#000000'
        theme.size_body = 20
        theme.save()
        self.client.post(reverse('manage_appearance_reset'), {'groups': ['colors']})
        theme.refresh_from_db()
        self.assertEqual(theme.color_primary, '#1f5eff')  # restored
        self.assertEqual(theme.size_body, 20)  # not ticked, untouched

    def test_restore_without_choice_changes_nothing(self):
        theme = ThemeSetting.load()
        theme.color_primary = '#000000'
        theme.save()
        self.client.post(reverse('manage_appearance_reset'), {})
        theme.refresh_from_db()
        self.assertEqual(theme.color_primary, '#000000')

    def test_restore_default_pictures(self):
        tmp = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmp):
                self.client.post(reverse('manage_appearance_reset'), {'groups': ['site_images']})
                site = SiteSetting.load()
                self.assertTrue(site.hero_image)
                self.assertTrue(site.logo)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_portfolio_add_edit_delete(self):
        self.client.post(reverse('manage_portfolio_create'), {
            'title': 'Work A', 'slug': 'work-a', 'category': '', 'summary': 'sum', 'description': '',
            'project_url': '', 'order': 0, 'is_active': 'on'})
        item = PortfolioItem.objects.get(slug='work-a')
        self.client.post(reverse('manage_portfolio_edit', args=[item.pk]), {
            'title': 'Work B', 'slug': 'work-a', 'category': '', 'summary': 'sum', 'description': '',
            'project_url': '', 'order': 0, 'is_active': 'on'})
        item.refresh_from_db()
        self.assertEqual(item.title, 'Work B')
        self.client.post(reverse('manage_portfolio_delete', args=[item.pk]))
        self.assertFalse(PortfolioItem.objects.exists())
