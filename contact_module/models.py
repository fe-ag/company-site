from django.db import models


class ContactMessage(models.Model):
    STATUS_NEW = 'new'
    STATUS_READ = 'read'
    STATUS_REPLIED = 'replied'
    STATUS_CHOICES = [(STATUS_NEW, 'New'), (STATUS_READ, 'Read'), (STATUS_REPLIED, 'Replied')]

    full_name = models.CharField(max_length=150, verbose_name='Full name')
    email = models.EmailField(max_length=254, verbose_name='Email address')
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(max_length=5000, verbose_name='Message')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sent at')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='Status')
    reply_text = models.TextField(max_length=10000, blank=True, verbose_name='Reply')
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name='Replied at')
    reply_error = models.CharField(max_length=300, blank=True, verbose_name='Last email error')

    class Meta:
        ordering = ('-created_at', '-id')
        verbose_name = 'Contact message'
        verbose_name_plural = 'Contact messages'

    def __str__(self):
        return '%s - %s' % (self.full_name, self.subject)
