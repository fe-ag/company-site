from django.views.generic import DetailView, ListView

from .models import PortfolioItem


class PortfolioListView(ListView):
    model = PortfolioItem
    paginate_by = 9
    template_name = 'portfolio_module/portfolio_list.html'

    def get_queryset(self):
        return PortfolioItem.objects.filter(is_active=True)


class PortfolioDetailView(DetailView):
    model = PortfolioItem
    template_name = 'portfolio_module/portfolio_detail.html'

    def get_queryset(self):
        return PortfolioItem.objects.filter(is_active=True)
