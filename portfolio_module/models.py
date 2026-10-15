from django.db import models
from django.urls import reverse

from utils.validators import validate_image_file, validate_safe_url


class PortfolioItem(models.Model):
    title = models.CharField(max_length=150, verbose_name='Title')
    slug = models.SlugField(max_length=170, unique=True, verbose_name='Slug (URL name)')
    category = models.CharField(max_length=60, blank=True, verbose_name='Category (optional)')
    summary = models.TextField(max_length=300, verbose_name='Short description')
    description = models.TextField(blank=True, verbose_name='Full description')
    image = models.ImageField(upload_to='portfolio/', blank=True, validators=[validate_image_file], verbose_name='Image')
    project_url = models.CharField(max_length=300, blank=True, validators=[validate_safe_url], verbose_name='Project link (optional)')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Visible on the website')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order', '-id')
        verbose_name = 'Portfolio item'
        verbose_name_plural = 'Portfolio items'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portfolio_detail', kwargs={'slug': self.slug})

    def delete(self, *args, **kwargs):
        image = self.image
        super().delete(*args, **kwargs)
        if image:
            image.delete(save=False)
