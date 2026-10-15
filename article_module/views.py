from django.views.generic import DetailView, ListView

from .models import Article


class ArticleListView(ListView):
    model = Article
    paginate_by = 9
    template_name = 'article_module/article_list.html'

    def get_queryset(self):
        # published() hides drafts and articles scheduled in the future
        return Article.objects.published().select_related('author')


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_module/article_detail.html'

    def get_queryset(self):
        return Article.objects.published().select_related('author').prefetch_related('media')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = [m for m in self.object.media.all() if m.media_type == 'image']
        context['videos'] = [m for m in self.object.media.all() if m.media_type == 'video']
        context['audios'] = [m for m in self.object.media.all() if m.media_type == 'audio']
        return context
