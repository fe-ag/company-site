from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from article_module.models import Article, ArticleMedia
from portfolio_module.models import PortfolioItem
from site_module.defaults import DEFAULT_IMAGES_DIR, restore_default_images
from site_module.models import SiteSetting, ThemeSetting, NavLink, FooterColumn, FooterLink, Service

ARTICLES = [
    ('plan-a-project-that-finishes-on-time', 'How to Plan a Project That Finishes on Time',
     'A simple way to break work into small steps, agree on priorities and keep everyone informed.',
     'Good projects start with a clear goal. Write down, in one or two sentences, what "done" looks like.\n\n'
     'Next, break the work into small pieces that can be finished in a few days. Small pieces are easier to estimate, easier to hand over and easier to check.\n\n'
     'Finally, agree on a regular rhythm for updates. A short weekly summary of what is finished, what is next and what is blocked prevents most surprises.',
     'article-1.jpg'),
    ('habits-of-effective-teams', 'Five Habits of Effective Teams',
     'Clear roles, honest feedback and short meetings: small habits that make teams faster and calmer.',
     'Effective teams are rarely the ones with the most talent. They are the ones that agree on how they work together.\n\n'
     'Make roles clear so that everybody knows who decides what. Give feedback early and kindly. Keep meetings short and end each one with a written list of next steps.\n\n'
     'Review how the team works every few weeks and change one thing at a time.',
     'article-2.jpg'),
    ('why-clear-communication-matters', 'Why Clear Communication Matters',
     'Most delays come from misunderstandings. Here is how to write messages that get the right answer the first time.',
     'A clear message states the goal, the context and the question in the first few lines.\n\n'
     'Say what you need and by when. Use plain words instead of internal jargon. When a topic is complicated, add a short example.\n\n'
     'Read your message once more before sending it and ask yourself: could someone who joined today act on this?',
     'article-3.jpg'),
    ('getting-started-with-digital-tools', 'Getting Started with Digital Tools',
     'You do not need many tools. Pick a few, learn them well and write down how your team uses them.',
     'Adding a new tool is easy. Getting a team to use it well is the hard part.\n\n'
     'Start from a real problem, such as tasks getting lost or files being hard to find, and choose the simplest tool that solves it.\n\n'
     'Write a one-page guide that explains what goes where. Revisit it after a month and remove anything nobody uses.',
     'article-4.jpg'),
]

PORTFOLIO = [
    ('brand-website-redesign', 'Brand Website Redesign', 'Website', 'portfolio-1.jpg'),
    ('customer-portal', 'Customer Portal', 'Web application', 'portfolio-2.jpg'),
    ('mobile-app-concept', 'Mobile App Concept', 'Design', 'portfolio-3.jpg'),
    ('marketing-campaign-site', 'Marketing Campaign Site', 'Website', 'portfolio-4.jpg'),
    ('internal-dashboard', 'Internal Dashboard', 'Web application', 'portfolio-5.jpg'),
    ('online-storefront', 'Online Storefront', 'E-commerce', 'portfolio-6.jpg'),
]


def attach(field, filename):
    """Saves one of the default pictures into a model's ImageField."""
    path = DEFAULT_IMAGES_DIR / filename
    if path.exists():
        with open(path, 'rb') as fh:
            field.save(filename, File(fh), save=False)
        return True
    return False


class Command(BaseCommand):
    help = ('Creates default settings, menu, footer, sample services, articles, portfolio items and pictures. '
            'Existing content is never overwritten; run it again any time to add what is missing.')

    def handle(self, *args, **options):
        site = SiteSetting.load()
        ThemeSetting.load()
        restore_default_images(site, only_missing=True)

        for order, (title, url) in enumerate([('Home', '/'), ('About Us', '/about-us/'), ('Articles', '/articles/'), ('Contact Us', '/contact-us/')]):
            NavLink.objects.get_or_create(url=url, defaults={'title': title, 'order': order})
        NavLink.objects.get_or_create(url='/portfolio/', defaults={'title': 'Our Work', 'order': 1})

        column = FooterColumn.objects.first() or FooterColumn.objects.create(title='Company', order=0)
        for order, (title, url) in enumerate([('About Us', '/about-us/'), ('Our Work', '/portfolio/'), ('Articles', '/articles/'), ('Contact Us', '/contact-us/')]):
            FooterLink.objects.get_or_create(column=column, url=url, defaults={'title': title, 'order': order})

        if not Service.objects.exists():
            for order, (title, text, icon) in enumerate([
                ('Service One', 'Describe your first service here. This is placeholder text.', '★'),
                ('Service Two', 'Describe your second service here. This is placeholder text.', '◆'),
                ('Service Three', 'Describe your third service here. This is placeholder text.', '●'),
            ]):
                Service.objects.create(title=title, description=text, icon=icon, order=order)

        created_articles = 0
        for slug, title, excerpt, content, image in ARTICLES:
            article, created = Article.objects.get_or_create(slug=slug, defaults={
                'title': title, 'excerpt': excerpt, 'content': content,
                'status': Article.STATUS_PUBLISHED, 'published_at': timezone.now(),
            })
            if created:
                created_articles += 1
                attach(article.featured_image, image)
                article.save()

        first = Article.objects.filter(slug=ARTICLES[0][0]).first()
        if first and not first.media.exists():
            for order, (filename, caption) in enumerate([('gallery-1.jpg', 'Sample gallery image 1'), ('gallery-2.jpg', 'Sample gallery image 2')]):
                media = ArticleMedia(article=first, media_type='image', title=caption, order=order)
                if attach(media.file, filename):
                    media.save()

        created_items = 0
        for order, (slug, title, category, image) in enumerate(PORTFOLIO):
            item, created = PortfolioItem.objects.get_or_create(slug=slug, defaults={
                'title': title, 'category': category, 'order': order,
                'summary': 'Sample portfolio entry. Replace this text and the image with your real project.',
                'description': 'This is a sample entry so you can see how the portfolio looks.\n\nEdit or delete it in /manage/portfolio/.',
            })
            if created:
                created_items += 1
                attach(item.image, image)
                item.save()

        self.stdout.write(self.style.SUCCESS(
            'Done. New sample articles: %d, new portfolio items: %d.' % (created_articles, created_items)))
