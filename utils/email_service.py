import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger('contact_module')


def send_reply_email(contact, site):
    """Sends the admin's reply to the visitor.

    Returns (True, '') on success or (False, 'readable error') on failure.
    It never raises, so the caller can keep the message and the reply text.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    if not from_email:
        return False, 'Email is not configured: set EMAIL_HOST_USER / DEFAULT_FROM_EMAIL in your .env file.'

    context = {'contact': contact, 'site': site}
    subject = 'Re: %s' % contact.subject.replace('\r', ' ').replace('\n', ' ')
    # Django templates escape variables by default, so visitor input cannot inject HTML.
    text_body = render_to_string('emails/reply.txt', context)
    html_body = render_to_string('emails/reply.html', context)

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email='%s <%s>' % (site.site_name.replace('<', '').replace('>', '').replace(',', ''), from_email),
            to=[contact.email],  # the visitor's address is only ever a recipient
            reply_to=[site.email] if site.email else None,
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)
    except Exception as exc:  # smtplib / socket / auth errors
        logger.exception('Could not send reply email for contact message %s', contact.pk)
        return False, 'Email could not be sent (%s: %s).' % (exc.__class__.__name__, str(exc)[:150])
    return True, ''
