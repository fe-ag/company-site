from django import forms
from django.contrib.auth.forms import AuthenticationForm

from article_module.models import Article, ArticleMedia
from portfolio_module.models import PortfolioItem
from site_module.models import (
    SiteSetting, ThemeSetting, Service, NavLink, FooterColumn, FooterLink, CustomFont,
    FONT_CHOICES,
)
from utils.validators import validate_image_file, validate_video_file, validate_audio_file


class ManageLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError('This account is not allowed to use the management panel.', code='no_access')


class ArticleForm(forms.ModelForm):
    published_at = forms.DateTimeField(
        label='Publication date',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
    )

    class Meta:
        model = Article
        fields = ('title', 'slug', 'excerpt', 'content', 'featured_image', 'published_at', 'status', 'seo_title', 'meta_description')
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 16}),
        }


class ArticleMediaForm(forms.ModelForm):
    class Meta:
        model = ArticleMedia
        fields = ('media_type', 'file', 'title', 'order')

    def clean(self):
        cleaned = super().clean()
        file, media_type = cleaned.get('file'), cleaned.get('media_type')
        if file and media_type:
            validator = {'image': validate_image_file, 'video': validate_video_file, 'audio': validate_audio_file}[media_type]
            try:
                validator(file)
            except forms.ValidationError as exc:
                self.add_error('file', exc)
        return cleaned


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = '__all__'
        widgets = {
            'hero_subtitle': forms.Textarea(attrs={'rows': 3}),
            'intro_text': forms.Textarea(attrs={'rows': 5}),
            'services_text': forms.Textarea(attrs={'rows': 3}),
            'articles_text': forms.Textarea(attrs={'rows': 3}),
            'contact_text': forms.Textarea(attrs={'rows': 3}),
            'about_text': forms.Textarea(attrs={'rows': 10}),
            'footer_text': forms.Textarea(attrs={'rows': 3}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('title', 'description', 'icon', 'order', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


COLOR_FIELDS = [
    'color_primary', 'color_secondary', 'color_background', 'color_section_bg', 'color_text', 'color_text_muted',
    'color_link', 'color_link_hover', 'color_button', 'color_button_text', 'color_border', 'color_header',
    'color_footer', 'color_footer_text', 'color_menu_link', 'color_menu_link_hover',
]


class ThemeSettingForm(forms.ModelForm):
    font_body = forms.ChoiceField(label='Main font')
    font_heading = forms.ChoiceField(label='Heading font')

    class Meta:
        model = ThemeSetting
        fields = '__all__'
        widgets = {name: forms.TextInput(attrs={'type': 'color'}) for name in COLOR_FIELDS}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(FONT_CHOICES) + [('custom:%d' % f.pk, '%s (uploaded)' % f.name) for f in CustomFont.objects.all()]
        self.fields['font_body'].choices = choices
        self.fields['font_heading'].choices = choices

    def clean_line_height(self):
        value = self.cleaned_data['line_height']
        if not 1 <= value <= 2.4:
            raise forms.ValidationError('Use a value between 1.0 and 2.4.')
        return value

    def clean_letter_spacing(self):
        value = self.cleaned_data['letter_spacing']
        if not -1 <= value <= 4:
            raise forms.ValidationError('Use a value between -1 and 4.')
        return value

    # Fields shown in groups on the page
    @property
    def groups(self):
        def pick(prefixes):
            return [self[n] for n in self.fields if n.startswith(prefixes)]
        return [
            ('Colors', pick(('color_',))),
            ('Typography', pick(('font_', 'size_', 'weight_', 'line_height', 'letter_spacing'))),
            ('Layout and spacing', pick(('content_width', 'section_padding', 'heading_gap', 'hero_height', 'card_'))),
            ('Images', pick(('logo_height', 'hero_image', 'intro_image', 'article_image'))),
        ]


class CustomFontForm(forms.ModelForm):
    class Meta:
        model = CustomFont
        fields = ('name', 'file')

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not all(c.isalnum() or c in ' -' for c in name):
            raise forms.ValidationError('Use only letters, numbers, spaces and dashes.')
        return name


class NavLinkForm(forms.ModelForm):
    class Meta:
        model = NavLink
        fields = ('title', 'url', 'order', 'is_active')


class FooterColumnForm(forms.ModelForm):
    class Meta:
        model = FooterColumn
        fields = ('title', 'order', 'is_active')


class FooterLinkForm(forms.ModelForm):
    class Meta:
        model = FooterLink
        fields = ('column', 'title', 'url', 'order', 'is_active')


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ('title', 'slug', 'category', 'summary', 'description', 'image', 'project_url', 'order', 'is_active')
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 8}),
        }


class ResetDefaultsForm(forms.Form):
    """Which groups of appearance settings should go back to their default values."""
    groups = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from site_module.defaults import RESET_GROUPS
        self.fields['groups'].choices = [(key, label) for key, (label, _fields) in RESET_GROUPS.items()]
