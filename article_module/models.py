from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from utils.validators import validate_image_file, validate_video_file, validate_audio_file


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Article.STATUS_PUBLISHED, published_at__lte=timezone.now())


class Article(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [(STATUS_DRAFT, 'Draft'), (STATUS_PUBLISHED, 'Published')]

    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=220, unique=True, verbose_name='Slug (URL name)')
    excerpt = models.TextField(max_length=500, verbose_name='Short description')
    content = models.TextField(verbose_name='Main content')
    featured_image = models.ImageField(upload_to='articles/featured/', blank=True, validators=[validate_image_file], verbose_name='Featured image')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Author')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='Publication date')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name='Status')
    seo_title = models.CharField(max_length=70, blank=True, verbose_name='SEO title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta description')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ('-published_at', '-id')
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED


class ArticleMedia(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'
    TYPE_CHOICES = [(TYPE_IMAGE, 'Image'), (TYPE_VIDEO, 'Video'), (TYPE_AUDIO, 'Audio')]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='media', verbose_name='Article')
    media_type = models.CharField(max_length=5, choices=TYPE_CHOICES, verbose_name='Type')
    file = models.FileField(upload_to='articles/media/', verbose_name='File')
    title = models.CharField(max_length=150, blank=True, verbose_name='Title / caption')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Article media'
        verbose_name_plural = 'Article media'

    def __str__(self):
        return self.title or self.file.name

    def delete(self, *args, **kwargs):
        file = self.file
        super().delete(*args, **kwargs)
        if file:
            file.delete(save=False)
