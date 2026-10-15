from django.db import models

from utils.validators import (
    validate_hex_color, validate_safe_url, validate_image_file, validate_font_file, validate_font_signature,
)


class SingletonModel(models.Model):
    """Only one row (pk=1) is ever used."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSetting(SingletonModel):
    site_name = models.CharField(max_length=100, default='Your Company', verbose_name='Site name')
    tagline = models.CharField(max_length=200, blank=True, default='Solutions that move your business forward', verbose_name='Tagline')
    logo = models.ImageField(upload_to='site/', blank=True, validators=[validate_image_file], verbose_name='Logo')
    email = models.EmailField(blank=True, default='info@example.com', verbose_name='Contact email')
    phone = models.CharField(max_length=50, blank=True, default='+00 000 000 0000', verbose_name='Phone')
    address = models.CharField(max_length=250, blank=True, default='Your street address, City, Country', verbose_name='Address')

    header_button_text = models.CharField(max_length=40, blank=True, default='Contact Us', verbose_name='Header button text')
    header_button_url = models.CharField(max_length=300, blank=True, default='/contact-us/', validators=[validate_safe_url], verbose_name='Header button link')

    hero_title = models.CharField(max_length=150, default='Welcome to Your Company', verbose_name='Hero title')
    hero_subtitle = models.TextField(max_length=400, blank=True, default='A short sentence that explains what your company does and who it helps.', verbose_name='Hero subtitle')
    hero_button_text = models.CharField(max_length=40, blank=True, default='Learn More', verbose_name='Hero button text')
    hero_button_url = models.CharField(max_length=300, blank=True, default='/about-us/', validators=[validate_safe_url], verbose_name='Hero button link')
    hero_image = models.ImageField(upload_to='site/', blank=True, validators=[validate_image_file], verbose_name='Hero image')

    intro_title = models.CharField(max_length=150, default='Who We Are', verbose_name='Introduction title')
    intro_text = models.TextField(default='Write a short introduction to your company here. You can edit this text from the management panel.', verbose_name='Introduction text')
    intro_image = models.ImageField(upload_to='site/', blank=True, validators=[validate_image_file], verbose_name='Introduction image')

    services_title = models.CharField(max_length=150, default='Our Services', verbose_name='Services title')
    services_text = models.TextField(blank=True, default='A brief description of the services you offer.', verbose_name='Services text')

    portfolio_title = models.CharField(max_length=150, default='Our Work', verbose_name='Portfolio title')
    portfolio_text = models.TextField(blank=True, default='A selection of projects we are proud of.', verbose_name='Portfolio text')
    portfolio_button_text = models.CharField(max_length=40, blank=True, default='View All Work', verbose_name='Portfolio button text')

    articles_title = models.CharField(max_length=150, default='Latest Articles', verbose_name='Articles section title')
    articles_text = models.TextField(blank=True, default='News and insights from our team.', verbose_name='Articles section text')
    articles_button_text = models.CharField(max_length=40, blank=True, default='View All Articles', verbose_name='Articles button text')

    contact_title = models.CharField(max_length=150, default='Get in Touch', verbose_name='Contact title')
    contact_text = models.TextField(blank=True, default='Have a question? Send us a message and we will get back to you.', verbose_name='Contact text')
    contact_button_text = models.CharField(max_length=40, default='Send Message', verbose_name='Contact form button text')
    contact_success_message = models.CharField(max_length=250, default='Thank you! Your message has been sent. We will reply by email soon.', verbose_name='Contact success message')

    about_title = models.CharField(max_length=150, default='About Us', verbose_name='About page title')
    about_text = models.TextField(default='Tell visitors about your company, your mission and your values.', verbose_name='About page text')
    about_image = models.ImageField(upload_to='site/', blank=True, validators=[validate_image_file], verbose_name='About page image')

    footer_text = models.TextField(max_length=500, blank=True, default='A short description of your company for the footer.', verbose_name='Footer text')
    copyright_text = models.CharField(max_length=200, default='© Your Company. All rights reserved.', verbose_name='Copyright text')

    class Meta:
        verbose_name = 'Site setting'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return self.site_name


class Service(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    description = models.TextField(max_length=400, verbose_name='Description')
    icon = models.CharField(max_length=4, blank=True, verbose_name='Icon (one emoji or symbol)')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title


class NavLink(models.Model):
    title = models.CharField(max_length=50, verbose_name='Text')
    url = models.CharField(max_length=300, validators=[validate_safe_url], verbose_name='Link')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Menu link'
        verbose_name_plural = 'Menu links'

    def __str__(self):
        return self.title


class FooterColumn(models.Model):
    title = models.CharField(max_length=80, verbose_name='Column title')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Footer column'
        verbose_name_plural = 'Footer columns'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name='links', verbose_name='Column')
    title = models.CharField(max_length=80, verbose_name='Text')
    url = models.CharField(max_length=300, validators=[validate_safe_url], verbose_name='Link')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Footer link'
        verbose_name_plural = 'Footer links'

    def __str__(self):
        return self.title


class CustomFont(models.Model):
    """Fonts uploaded from the panel. Only .woff/.woff2/.ttf/.otf, checked by signature."""
    name = models.CharField(max_length=40, unique=True, verbose_name='Font name')
    file = models.FileField(upload_to='fonts/', validators=[validate_font_file, validate_font_signature], verbose_name='Font file')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Custom font'
        verbose_name_plural = 'Custom fonts'

    def __str__(self):
        return self.name

    @property
    def css_format(self):
        ext = self.file.name.rsplit('.', 1)[-1].lower()
        return {'woff': 'woff', 'woff2': 'woff2', 'ttf': 'truetype', 'otf': 'opentype'}.get(ext, 'truetype')


FONT_CHOICES = [
    ('system', 'System default (Segoe UI / Roboto / Arial)'),
    ('arial', 'Arial / Helvetica'),
    ('verdana', 'Verdana'),
    ('trebuchet', 'Trebuchet MS'),
    ('georgia', 'Georgia (serif)'),
    ('times', 'Times New Roman (serif)'),
    ('courier', 'Courier New (monospace)'),
]
FONT_STACKS = {
    'system': "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
    'arial': "Arial, Helvetica, sans-serif",
    'verdana': "Verdana, Geneva, sans-serif",
    'trebuchet': "'Trebuchet MS', Helvetica, sans-serif",
    'georgia': "Georgia, 'Times New Roman', serif",
    'times': "'Times New Roman', Times, serif",
    'courier': "'Courier New', Courier, monospace",
}
WEIGHT_CHOICES = [(str(w), str(w)) for w in (300, 400, 500, 600, 700, 800)]
FIT_CHOICES = [('cover', 'Cover (fill, may crop)'), ('contain', 'Contain (show whole image)')]
RATIO_CHOICES = [('auto', 'Original'), ('1 / 1', '1:1'), ('4 / 3', '4:3'), ('3 / 2', '3:2'), ('16 / 9', '16:9'), ('21 / 9', '21:9')]


def _color(default, label):
    return models.CharField(max_length=7, default=default, validators=[validate_hex_color], verbose_name=label)


def _px(default, label, lo, hi):
    from django.core.validators import MinValueValidator, MaxValueValidator
    return models.PositiveIntegerField(default=default, validators=[MinValueValidator(lo), MaxValueValidator(hi)],
                                       verbose_name='%s (px, %d-%d)' % (label, lo, hi))


class ThemeSetting(SingletonModel):
    # Colors
    color_primary = _color('#1f5eff', 'Primary color')
    color_secondary = _color('#0b1f4d', 'Secondary color')
    color_background = _color('#ffffff', 'Page background')
    color_section_bg = _color('#f4f6fb', 'Section background')
    color_text = _color('#1b2333', 'Main text')
    color_text_muted = _color('#5b6578', 'Secondary text')
    color_link = _color('#1f5eff', 'Links')
    color_link_hover = _color('#0b3fc4', 'Links on hover')
    color_button = _color('#1f5eff', 'Buttons')
    color_button_text = _color('#ffffff', 'Button text')
    color_border = _color('#dde3ef', 'Borders')
    color_header = _color('#ffffff', 'Header background')
    color_footer = _color('#0b1f4d', 'Footer background')
    color_footer_text = _color('#d6def0', 'Footer text')
    color_menu_link = _color('#1b2333', 'Menu links')
    color_menu_link_hover = _color('#1f5eff', 'Menu links on hover')

    # Typography
    font_body = models.CharField(max_length=60, default='system', verbose_name='Main font')
    font_heading = models.CharField(max_length=60, default='system', verbose_name='Heading font')
    size_body = _px(16, 'Body text size', 12, 24)
    size_h1 = _px(44, 'Main heading size', 24, 80)
    size_h2 = _px(30, 'Section heading size', 18, 56)
    size_h3 = _px(20, 'Subheading size', 14, 36)
    size_button = _px(16, 'Button text size', 12, 24)
    size_menu = _px(15, 'Menu text size', 12, 24)
    size_footer = _px(14, 'Footer text size', 11, 22)
    weight_body = models.CharField(max_length=3, choices=WEIGHT_CHOICES, default='400', verbose_name='Body font weight')
    weight_heading = models.CharField(max_length=3, choices=WEIGHT_CHOICES, default='700', verbose_name='Heading font weight')
    line_height = models.DecimalField(max_digits=3, decimal_places=2, default=1.6, verbose_name='Line height (1.0-2.4)')
    letter_spacing = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name='Letter spacing (px, -1 to 4)')

    # Layout
    content_width = _px(1140, 'Content width', 800, 1600)
    section_padding = _px(72, 'Section top/bottom spacing', 16, 200)
    heading_gap = _px(16, 'Gap between heading and text', 0, 80)
    hero_height = _px(520, 'Hero minimum height', 240, 900)
    card_radius = _px(14, 'Card corner radius', 0, 40)
    card_gap = _px(24, 'Gap between article cards', 8, 64)
    card_image_height = _px(200, 'Card image height', 100, 400)

    # Images
    logo_height = _px(40, 'Logo height', 16, 120)
    hero_image_fit = models.CharField(max_length=10, choices=FIT_CHOICES, default='cover', verbose_name='Hero image fit')
    hero_image_ratio = models.CharField(max_length=10, choices=RATIO_CHOICES, default='4 / 3', verbose_name='Hero image ratio')
    hero_image_max_width = _px(560, 'Hero image max width', 200, 1200)
    hero_image_radius = _px(16, 'Hero image corner radius', 0, 80)
    hero_image_margin = _px(0, 'Hero image outer spacing', 0, 80)
    intro_image_fit = models.CharField(max_length=10, choices=FIT_CHOICES, default='cover', verbose_name='Intro / About image fit')
    intro_image_ratio = models.CharField(max_length=10, choices=RATIO_CHOICES, default='3 / 2', verbose_name='Intro / About image ratio')
    intro_image_max_width = _px(520, 'Intro / About image max width', 200, 1200)
    intro_image_radius = _px(16, 'Intro / About image corner radius', 0, 80)
    article_image_fit = models.CharField(max_length=10, choices=FIT_CHOICES, default='cover', verbose_name='Article image fit')
    article_image_radius = _px(12, 'Article image corner radius', 0, 80)

    class Meta:
        verbose_name = 'Theme setting'
        verbose_name_plural = 'Theme settings'

    def __str__(self):
        return 'Theme settings'
