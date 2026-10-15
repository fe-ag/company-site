from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from article_module.models import Article, ArticleMedia
from contact_module.forms import ReplyForm
from contact_module.models import ContactMessage
from portfolio_module.models import PortfolioItem
from site_module.models import (
    SiteSetting, ThemeSetting, Service, NavLink, FooterColumn, FooterLink, CustomFont,
)
from utils.email_service import send_reply_email
from .forms import (
    ManageLoginForm, ArticleForm, ArticleMediaForm, SiteSettingForm, ServiceForm, ThemeSettingForm,
    CustomFontForm, NavLinkForm, FooterColumnForm, FooterLinkForm, PortfolioItemForm, ResetDefaultsForm,
)
from .permissions import manager_required, is_manager


# ---------------------------------------------------------------- auth
class ManageLoginView(LoginView):
    template_name = 'manage/login.html'
    authentication_form = ManageLoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return self.get_redirect_url() or reverse('manage_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if is_manager(request.user):
            return redirect('manage_dashboard')
        return super().dispatch(request, *args, **kwargs)


@require_POST
def manage_logout(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('manage_login')


# ---------------------------------------------------------------- dashboard
@manager_required
def dashboard(request):
    context = {
        'article_total': Article.objects.count(),
        'article_published': Article.objects.filter(status=Article.STATUS_PUBLISHED).count(),
        'article_drafts': Article.objects.filter(status=Article.STATUS_DRAFT).count(),
        'message_new': ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW).count(),
        'message_total': ContactMessage.objects.count(),
        'media_total': ArticleMedia.objects.count(),
        'portfolio_total': PortfolioItem.objects.count(),
        'latest_messages': ContactMessage.objects.all()[:5],
        'latest_articles': Article.objects.all()[:5],
    }
    return render(request, 'manage/dashboard.html', context)


# ---------------------------------------------------------------- articles
@manager_required
def article_list(request):
    status = request.GET.get('status', '')
    queryset = Article.objects.select_related('author')
    if status in (Article.STATUS_DRAFT, Article.STATUS_PUBLISHED):
        queryset = queryset.filter(status=status)
    page = Paginator(queryset, 15).get_page(request.GET.get('page'))
    return render(request, 'manage/article_list.html', {'page': page, 'status': status})


@manager_required
def article_create(request):
    form = ArticleForm(request.POST or None, request.FILES or None, initial={'published_at': timezone.now()})
    if request.method == 'POST' and form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        messages.success(request, 'Article saved. You can now add images, video or audio.')
        return redirect('manage_article_edit', pk=article.pk)
    return render(request, 'manage/article_form.html', {'form': form, 'article': None})


@manager_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    media_form = ArticleMediaForm()
    if request.method == 'POST':
        if request.POST.get('action') == 'add_media':
            media_form = ArticleMediaForm(request.POST, request.FILES)
            form = ArticleForm(instance=article)
            if media_form.is_valid():
                media = media_form.save(commit=False)
                media.article = article
                media.save()
                messages.success(request, 'Media added.')
                return redirect('manage_article_edit', pk=article.pk)
        else:
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                form.save()
                messages.success(request, 'Article updated.')
                return redirect('manage_article_edit', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'manage/article_form.html', {
        'form': form, 'article': article, 'media_form': media_form, 'media_items': article.media.all(),
    })


@manager_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        for media in article.media.all():
            media.delete()  # also removes the files from disk
        featured = article.featured_image
        article.delete()
        if featured:
            featured.delete(save=False)
        messages.success(request, 'Article deleted.')
        return redirect('manage_article_list')
    return render(request, 'manage/confirm_delete.html', {
        'object_name': article.title, 'kind': 'article', 'cancel_url': reverse('manage_article_edit', args=[pk]),
        'warning': 'All media attached to this article will be deleted too.',
    })


@manager_required
@require_POST
def article_toggle(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.is_published:
        article.status = Article.STATUS_DRAFT
        messages.success(request, 'Article unpublished (now a draft).')
    else:
        article.status = Article.STATUS_PUBLISHED
        messages.success(request, 'Article published.')
    article.save(update_fields=['status', 'updated_at'])
    return redirect(request.POST.get('next') if request.POST.get('next', '').startswith('/manage/') else 'manage_article_list')


# ---------------------------------------------------------------- media
@manager_required
def media_list(request):
    media_type = request.GET.get('type', '')
    queryset = ArticleMedia.objects.select_related('article').order_by('-created_at')
    if media_type in ('image', 'video', 'audio'):
        queryset = queryset.filter(media_type=media_type)
    page = Paginator(queryset, 24).get_page(request.GET.get('page'))
    return render(request, 'manage/media_list.html', {'page': page, 'media_type': media_type})


@manager_required
def media_delete(request, pk):
    media = get_object_or_404(ArticleMedia, pk=pk)
    if request.method == 'POST':
        article_pk = media.article_id
        media.delete()
        messages.success(request, 'Media deleted.')
        nxt = request.POST.get('next', '')
        return redirect(nxt if nxt.startswith('/manage/') else reverse('manage_article_edit', args=[article_pk]))
    return render(request, 'manage/confirm_delete.html', {
        'object_name': str(media), 'kind': 'media file',
        'cancel_url': request.META.get('HTTP_REFERER') or reverse('manage_media_list'),
        'next': request.GET.get('next', ''),
    })


# ---------------------------------------------------------------- simple CRUD helpers
def _edit(request, form_class, instance, template, title, success_url, extra=None):
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Saved.')
        return redirect(success_url)
    context = {'form': form, 'title': title, 'cancel_url': success_url}
    context.update(extra or {})
    return render(request, template, context)


def _delete(request, model, pk, kind, success_url, warning=''):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '%s deleted.' % kind.capitalize())
        return redirect(success_url)
    return render(request, 'manage/confirm_delete.html', {
        'object_name': str(obj), 'kind': kind, 'cancel_url': success_url, 'warning': warning,
    })


# ---------------------------------------------------------------- website content
@manager_required
def content_settings(request):
    site = SiteSetting.load()
    form = SiteSettingForm(request.POST or None, request.FILES or None, instance=site)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Website content saved.')
        return redirect('manage_content')
    return render(request, 'manage/content.html', {'form': form, 'services': Service.objects.all()})


@manager_required
def service_edit(request, pk=None):
    instance = get_object_or_404(Service, pk=pk) if pk else None
    return _edit(request, ServiceForm, instance, 'manage/simple_form.html',
                 'Edit service' if pk else 'Add service', reverse('manage_content'))


@manager_required
def service_delete(request, pk):
    return _delete(request, Service, pk, 'service', reverse('manage_content'))


# ---------------------------------------------------------------- appearance
@manager_required
def appearance(request):
    theme = ThemeSetting.load()
    form = ThemeSettingForm(request.POST or None, instance=theme)
    font_form = CustomFontForm()
    if request.method == 'POST':
        if request.POST.get('action') == 'upload_font':
            font_form = CustomFontForm(request.POST, request.FILES)
            form = ThemeSettingForm(instance=theme)
            if font_form.is_valid():
                font_form.save()
                messages.success(request, 'Font uploaded. You can now choose it in the font lists.')
                return redirect('manage_appearance')
        elif form.is_valid():
            form.save()
            messages.success(request, 'Appearance saved. The public site now uses the new settings.')
            return redirect('manage_appearance')
    return render(request, 'manage/appearance.html', {
        'form': form, 'font_form': font_form, 'fonts': CustomFont.objects.all(), 'reset_form': ResetDefaultsForm(),
    })


@manager_required
def font_delete(request, pk):
    font = get_object_or_404(CustomFont, pk=pk)
    if request.method == 'POST':
        file = font.file
        font.delete()
        file.delete(save=False)
        messages.success(request, 'Font deleted.')
        return redirect('manage_appearance')
    return render(request, 'manage/confirm_delete.html', {
        'object_name': font.name, 'kind': 'font', 'cancel_url': reverse('manage_appearance'),
        'warning': 'Places that used this font will fall back to the system font.',
    })


@manager_required
@require_POST
def appearance_reset(request):
    """Restores only the groups the admin ticked (colors, fonts, sizes, layout, image settings, pictures)."""
    from site_module.defaults import RESET_GROUPS, reset_theme_groups, restore_default_images
    form = ResetDefaultsForm(request.POST)
    keys = form.cleaned_data['groups'] if form.is_valid() else []
    if not keys:
        messages.error(request, 'Tick at least one group to restore.')
        return redirect('manage_appearance')
    theme_keys = [k for k in keys if k != 'site_images']
    if theme_keys:
        reset_theme_groups(ThemeSetting.load(), theme_keys)
    if 'site_images' in keys:
        restore_default_images(SiteSetting.load())
    labels = ', '.join(RESET_GROUPS[k][0].split(' - ')[0] for k in keys)
    messages.success(request, 'Restored to defaults: %s.' % labels)
    return redirect('manage_appearance')


# ---------------------------------------------------------------- portfolio
@manager_required
def portfolio_list(request):
    page = Paginator(PortfolioItem.objects.all(), 20).get_page(request.GET.get('page'))
    return render(request, 'manage/portfolio_list.html', {'page': page})


@manager_required
def portfolio_edit(request, pk=None):
    instance = get_object_or_404(PortfolioItem, pk=pk) if pk else None
    return _edit(request, PortfolioItemForm, instance, 'manage/simple_form.html',
                 'Edit portfolio item' if pk else 'Add portfolio item', reverse('manage_portfolio_list'))


@manager_required
def portfolio_delete(request, pk):
    return _delete(request, PortfolioItem, pk, 'portfolio item', reverse('manage_portfolio_list'))


# ---------------------------------------------------------------- navigation and footer
@manager_required
def navigation(request):
    return render(request, 'manage/navigation.html', {
        'nav_links': NavLink.objects.all(),
        'columns': FooterColumn.objects.prefetch_related('links'),
    })


@manager_required
def nav_edit(request, pk=None):
    instance = get_object_or_404(NavLink, pk=pk) if pk else None
    return _edit(request, NavLinkForm, instance, 'manage/simple_form.html',
                 'Edit menu link' if pk else 'Add menu link', reverse('manage_navigation'))


@manager_required
def nav_delete(request, pk):
    return _delete(request, NavLink, pk, 'menu link', reverse('manage_navigation'))


@manager_required
def column_edit(request, pk=None):
    instance = get_object_or_404(FooterColumn, pk=pk) if pk else None
    return _edit(request, FooterColumnForm, instance, 'manage/simple_form.html',
                 'Edit footer column' if pk else 'Add footer column', reverse('manage_navigation'))


@manager_required
def column_delete(request, pk):
    return _delete(request, FooterColumn, pk, 'footer column', reverse('manage_navigation'),
                   warning='All links in this column will be deleted too.')


@manager_required
def footer_link_edit(request, pk=None):
    instance = get_object_or_404(FooterLink, pk=pk) if pk else None
    if not FooterColumn.objects.exists():
        messages.error(request, 'Create a footer column first.')
        return redirect('manage_navigation')
    return _edit(request, FooterLinkForm, instance, 'manage/simple_form.html',
                 'Edit footer link' if pk else 'Add footer link', reverse('manage_navigation'))


@manager_required
def footer_link_delete(request, pk):
    return _delete(request, FooterLink, pk, 'footer link', reverse('manage_navigation'))


# ---------------------------------------------------------------- contact messages
@manager_required
def message_list(request):
    status = request.GET.get('status', '')
    queryset = ContactMessage.objects.all()
    if status in (ContactMessage.STATUS_NEW, ContactMessage.STATUS_READ, ContactMessage.STATUS_REPLIED):
        queryset = queryset.filter(status=status)
    page = Paginator(queryset, 20).get_page(request.GET.get('page'))
    return render(request, 'manage/message_list.html', {'page': page, 'status': status})


@manager_required
def message_detail(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if contact.status == ContactMessage.STATUS_NEW and request.method == 'GET':
        contact.status = ContactMessage.STATUS_READ
        contact.save(update_fields=['status'])

    form = ReplyForm(initial={'reply_text': contact.reply_text})
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply_text = form.cleaned_data['reply_text']
            # 1) Store the reply first, so nothing is lost if the email fails.
            contact.reply_text = reply_text
            contact.save(update_fields=['reply_text'])
            # 2) Send the email.
            ok, error = send_reply_email(contact, SiteSetting.load())
            if ok:
                contact.status = ContactMessage.STATUS_REPLIED
                contact.replied_at = timezone.now()
                contact.reply_error = ''
                contact.save(update_fields=['status', 'replied_at', 'reply_error'])
                messages.success(request, 'Reply sent to %s.' % contact.email)
                return redirect('manage_message_detail', pk=contact.pk)
            contact.reply_error = error[:300]
            contact.save(update_fields=['reply_error'])
            messages.error(request, 'The reply was saved but the email was NOT sent. %s You can try again.' % error)
    return render(request, 'manage/message_detail.html', {'contact': contact, 'form': form})


@manager_required
@require_POST
def message_status(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    new_status = request.POST.get('status')
    if new_status in (ContactMessage.STATUS_NEW, ContactMessage.STATUS_READ):
        contact.status = new_status
        contact.save(update_fields=['status'])
        messages.success(request, 'Status changed.')
    else:
        messages.error(request, 'A message becomes "Replied" only after an email reply is sent.')
    return redirect('manage_message_detail', pk=pk)


@manager_required
def message_delete(request, pk):
    return _delete(request, ContactMessage, pk, 'message', reverse('manage_message_list'))


# ---------------------------------------------------------------- account
@manager_required
def account(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed.')
        return redirect('manage_account')
    return render(request, 'manage/account.html', {'form': form})
