from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('home_module.urls')),
    path('articles/', include('article_module.urls')),
    path('portfolio/', include('portfolio_module.urls')),
    path('contact-us/', include('contact_module.urls')),
    path('manage/', include('manage_module.urls')),
]

handler404 = 'home_module.views.error_404'
handler500 = 'home_module.views.error_500'
handler403 = 'home_module.views.error_403'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
