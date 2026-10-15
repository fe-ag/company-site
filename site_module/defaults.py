"""'Restore default' helpers used by the management panel and by seed_demo.

* Colors, fonts, text sizes, layout and image settings: the default is the default= value
  written in site_module/models.py (ThemeSetting).
* Site pictures (logo, hero, intro, about): the default pictures live in static/default_images/.
"""
from django.conf import settings
from django.core.files import File

from .models import ThemeSetting

DEFAULT_IMAGES_DIR = settings.BASE_DIR / 'static' / 'default_images'

SITE_IMAGE_FILES = {
    'logo': 'logo.png',
    'hero_image': 'hero.jpg',
    'intro_image': 'intro.jpg',
    'about_image': 'about.jpg',
}


def _names(*prefixes, exact=()):
    return [f.name for f in ThemeSetting._meta.fields
            if f.name != 'id' and (f.name.startswith(prefixes) or f.name in exact)]


# key -> (label shown in the panel, theme field names). 'site_images' is handled separately.
RESET_GROUPS = {
    'colors': ('Colors', _names('color_')),
    'fonts': ('Fonts (family and weight)', ['font_body', 'font_heading', 'weight_body', 'weight_heading']),
    'text_sizes': ('Text sizes, line height and letter spacing',
                   ['size_body', 'size_h1', 'size_h2', 'size_h3', 'size_button', 'size_menu', 'size_footer',
                    'line_height', 'letter_spacing']),
    'layout': ('Layout and spacing',
               ['content_width', 'section_padding', 'heading_gap', 'hero_height', 'card_radius', 'card_gap']),
    'image_settings': ('Image sizes, shapes and fit',
                       ['logo_height', 'card_image_height'] + _names('hero_image_', 'intro_image_', 'article_image_')),
    'site_images': ('Site pictures (logo, hero, intro, about) - back to the default pictures', []),
}


def reset_theme_groups(theme, keys):
    """Sets every field of the chosen groups back to its default value and saves."""
    for key in keys:
        for name in RESET_GROUPS[key][1]:
            setattr(theme, name, ThemeSetting._meta.get_field(name).get_default())
    theme.save()


def restore_default_images(site, only_missing=False):
    """Puts the default pictures back on the site settings. Returns how many were set."""
    count = 0
    for field_name, filename in SITE_IMAGE_FILES.items():
        path = DEFAULT_IMAGES_DIR / filename
        current = getattr(site, field_name)
        if not path.exists() or (only_missing and current):
            continue
        if current:
            current.delete(save=False)  # remove the replaced file from disk
        with open(path, 'rb') as fh:
            getattr(site, field_name).save(filename, File(fh), save=False)
        count += 1
    site.save()
    return count
