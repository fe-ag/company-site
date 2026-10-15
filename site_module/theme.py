"""Turns the ThemeSetting row into CSS variables (and @font-face rules)."""
import re

from .models import FONT_STACKS, CustomFont

SYSTEM_STACK = FONT_STACKS['system']


def custom_font_family(font):
    # name is only ever inserted after stripping everything except letters, digits, space and dash
    return re.sub(r'[^A-Za-z0-9 \-]', '', font.name)


def font_stack(value, custom_fonts):
    """value is a key of FONT_STACKS or 'custom:<id>'. Anything else falls back to the system font."""
    if value in FONT_STACKS:
        return FONT_STACKS[value]
    if value.startswith('custom:'):
        for font in custom_fonts:
            if 'custom:%d' % font.pk == value:
                return "'%s', %s" % (custom_font_family(font), SYSTEM_STACK)
    return SYSTEM_STACK


def build_theme_css(theme):
    fonts = list(CustomFont.objects.all())
    parts = []
    for font in fonts:
        parts.append(
            "@font-face{font-family:'%s';src:url('%s') format('%s');font-display:swap;}"
            % (custom_font_family(font), font.file.url, font.css_format)
        )
    ratio = lambda v: v if v != 'auto' else 'auto'
    variables = {
        'primary': theme.color_primary,
        'secondary': theme.color_secondary,
        'bg': theme.color_background,
        'section-bg': theme.color_section_bg,
        'text': theme.color_text,
        'text-muted': theme.color_text_muted,
        'link': theme.color_link,
        'link-hover': theme.color_link_hover,
        'button': theme.color_button,
        'button-text': theme.color_button_text,
        'border': theme.color_border,
        'header-bg': theme.color_header,
        'footer-bg': theme.color_footer,
        'footer-text': theme.color_footer_text,
        'menu-link': theme.color_menu_link,
        'menu-link-hover': theme.color_menu_link_hover,
        'font-body': font_stack(theme.font_body, fonts),
        'font-heading': font_stack(theme.font_heading, fonts),
        'size-body': '%dpx' % theme.size_body,
        'size-h1': '%dpx' % theme.size_h1,
        'size-h2': '%dpx' % theme.size_h2,
        'size-h3': '%dpx' % theme.size_h3,
        'size-button': '%dpx' % theme.size_button,
        'size-menu': '%dpx' % theme.size_menu,
        'size-footer': '%dpx' % theme.size_footer,
        'weight-body': theme.weight_body,
        'weight-heading': theme.weight_heading,
        'line-height': str(theme.line_height),
        'letter-spacing': '%spx' % theme.letter_spacing,
        'content-width': '%dpx' % theme.content_width,
        'section-padding': '%dpx' % theme.section_padding,
        'heading-gap': '%dpx' % theme.heading_gap,
        'hero-height': '%dpx' % theme.hero_height,
        'card-radius': '%dpx' % theme.card_radius,
        'card-gap': '%dpx' % theme.card_gap,
        'card-image-height': '%dpx' % theme.card_image_height,
        'logo-height': '%dpx' % theme.logo_height,
        'hero-img-fit': theme.hero_image_fit,
        'hero-img-ratio': ratio(theme.hero_image_ratio),
        'hero-img-max': '%dpx' % theme.hero_image_max_width,
        'hero-img-radius': '%dpx' % theme.hero_image_radius,
        'hero-img-margin': '%dpx' % theme.hero_image_margin,
        'intro-img-fit': theme.intro_image_fit,
        'intro-img-ratio': ratio(theme.intro_image_ratio),
        'intro-img-max': '%dpx' % theme.intro_image_max_width,
        'intro-img-radius': '%dpx' % theme.intro_image_radius,
        'article-img-fit': theme.article_image_fit,
        'article-img-radius': '%dpx' % theme.article_image_radius,
    }
    body = ''.join('--%s:%s;' % (k, v) for k, v in variables.items())
    parts.append(':root{%s}' % body)
    return '\n'.join(parts)
