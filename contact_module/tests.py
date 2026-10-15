from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage

EMAIL_OK = dict(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='site@example.com')


class ContactFormTests(TestCase):
    def test_valid_submission_is_saved(self):
        response = self.client.post('/contact-us/', {
            'full_name': 'Ann', 'email': 'ann@example.com', 'subject': 'Hello', 'message': 'A long enough message.', 'website': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().status, 'new')

    def test_invalid_email_and_honeypot(self):
        self.client.post('/contact-us/', {'full_name': 'A', 'email': 'bad', 'subject': 'S', 'message': 'long enough message'})
        self.client.post('/contact-us/', {'full_name': 'A', 'email': 'a@b.com', 'subject': 'S', 'message': 'long enough message', 'website': 'spam'})
        self.assertEqual(ContactMessage.objects.count(), 0)


@override_settings(**EMAIL_OK)
class ReplyTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user('boss', password='pass12345!x', is_staff=True)
        self.msg = ContactMessage.objects.create(full_name='Ann <b>X</b>', email='ann@example.com', subject='Hi', message='Original text here')
        self.client.login(username='boss', password='pass12345!x')

    def test_reply_sends_email_and_updates_status(self):
        url = reverse('manage_message_detail', args=[self.msg.pk])
        response = self.client.post(url, {'reply_text': 'Thanks for writing'})
        self.assertEqual(response.status_code, 302)
        self.msg.refresh_from_db()
        self.assertEqual(self.msg.status, 'replied')
        self.assertIsNotNone(self.msg.replied_at)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ['ann@example.com'])
        self.assertIn('Thanks for writing', sent.body)
        self.assertIn('Original text here', sent.body)
        html = sent.alternatives[0][0]
        self.assertNotIn('<b>X</b>', html)  # visitor input is escaped

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend', EMAIL_HOST='127.0.0.1', EMAIL_PORT=1, EMAIL_TIMEOUT=2)
    def test_failed_send_keeps_data_and_allows_retry(self):
        url = reverse('manage_message_detail', args=[self.msg.pk])
        self.client.post(url, {'reply_text': 'Draft reply'})
        self.msg.refresh_from_db()
        self.assertNotEqual(self.msg.status, 'replied')
        self.assertEqual(self.msg.reply_text, 'Draft reply')
        self.assertTrue(self.msg.reply_error)
        self.assertEqual(self.msg.message, 'Original text here')
