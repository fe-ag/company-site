from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from article_module.models import Article
from portfolio_module.models import PortfolioItem
from site_module.models import Service


class HomeView(TemplateView):
    template_name = 'home_module/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        context['latest_articles'] = Article.objects.published()[:3]
        context['portfolio_items'] = PortfolioItem.objects.filter(is_active=True)[:3]
        return context


class AboutView(TemplateView):
    template_name = 'home_module/about.html'


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_500(request):
    # Rendered without a request, so no database access is needed to show the error page.
    return HttpResponseServerError(render_to_string('errors/500.html'))
