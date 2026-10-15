import os
import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')
SAFE_URL_SCHEMES = ('http://', 'https://', 'mailto:', 'tel:')


def validate_hex_color(value):
    if not COLOR_RE.match(value or ''):
        raise ValidationError('Enter a color like #1a2b3c.')


def validate_safe_url(value):
    """Allow site paths (/about-us/), anchors (#x) and http/https/mailto/tel only."""
    value = (value or '').strip()
    if any(ch in value for ch in ('\n', '\r', '\t', ' ', '<', '>', '"', "'")):
        raise ValidationError('The link contains invalid characters.')
    if value.startswith('/') and not value.startswith('//'):
        return
    if value.startswith('#'):
        return
    if value.lower().startswith(SAFE_URL_SCHEMES):
        return
    raise ValidationError('Use a path like /about-us/ or a link starting with http://, https://, mailto: or tel:.')


@deconstructible
class FileValidator:
    """Checks extension and size of an uploaded file.

    It is a class (not a nested function) so Django can write it into migration files.
    """

    def __init__(self, allowed_extensions, max_mb):
        self.allowed_extensions = tuple(allowed_extensions)
        self.max_mb = max_mb

    def __call__(self, file):
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError('Unsupported file type. Allowed: %s.' % ', '.join(self.allowed_extensions))
        if file.size > self.max_mb * 1024 * 1024:
            raise ValidationError('File is too large (max %d MB).' % self.max_mb)

    def __eq__(self, other):
        return (isinstance(other, FileValidator)
                and self.allowed_extensions == other.allowed_extensions and self.max_mb == other.max_mb)


validate_image_file = FileValidator(('.jpg', '.jpeg', '.png', '.gif', '.webp'), 5)
validate_video_file = FileValidator(('.mp4', '.webm', '.ogv'), 100)
validate_audio_file = FileValidator(('.mp3', '.wav', '.ogg', '.m4a'), 30)
validate_font_file = FileValidator(('.woff', '.woff2', '.ttf', '.otf'), 2)


def validate_font_signature(file):
    """Check the first bytes so a random file can't be renamed to .woff."""
    head = file.read(4)
    file.seek(0)
    if head not in (b'wOFF', b'wOF2', b'\x00\x01\x00\x00', b'OTTO', b'true'):
        raise ValidationError('This does not look like a valid font file.')
