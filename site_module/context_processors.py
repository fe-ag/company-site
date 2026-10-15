from .models import SiteSetting, ThemeSetting, NavLink, FooterColumn
from .theme import build_theme_css


def site_context(request):
    """Makes site settings, theme CSS, menu and footer available in every template.
    Everything is read from the database on each request, so panel changes show immediately."""
    site = SiteSetting.load()
    theme = ThemeSetting.load()
    return {
        'site': site,
        'theme_css': build_theme_css(theme),
        'nav_links': NavLink.objects.filter(is_active=True),
        'footer_columns': FooterColumn.objects.filter(is_active=True).prefetch_related('links'),
    }
