from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='manage_dashboard'),
    path('login/', views.ManageLoginView.as_view(), name='manage_login'),
    path('logout/', views.manage_logout, name='manage_logout'),

    path('articles/', views.article_list, name='manage_article_list'),
    path('articles/new/', views.article_create, name='manage_article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='manage_article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='manage_article_delete'),
    path('articles/<int:pk>/toggle/', views.article_toggle, name='manage_article_toggle'),

    path('portfolio/', views.portfolio_list, name='manage_portfolio_list'),
    path('portfolio/new/', views.portfolio_edit, name='manage_portfolio_create'),
    path('portfolio/<int:pk>/edit/', views.portfolio_edit, name='manage_portfolio_edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='manage_portfolio_delete'),

    path('media/', views.media_list, name='manage_media_list'),
    path('media/<int:pk>/delete/', views.media_delete, name='manage_media_delete'),

    path('content/', views.content_settings, name='manage_content'),
    path('services/new/', views.service_edit, name='manage_service_create'),
    path('services/<int:pk>/edit/', views.service_edit, name='manage_service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='manage_service_delete'),

    path('appearance/', views.appearance, name='manage_appearance'),
    path('appearance/reset/', views.appearance_reset, name='manage_appearance_reset'),
    path('appearance/fonts/<int:pk>/delete/', views.font_delete, name='manage_font_delete'),

    path('navigation/', views.navigation, name='manage_navigation'),
    path('navigation/menu/new/', views.nav_edit, name='manage_nav_create'),
    path('navigation/menu/<int:pk>/edit/', views.nav_edit, name='manage_nav_edit'),
    path('navigation/menu/<int:pk>/delete/', views.nav_delete, name='manage_nav_delete'),
    path('navigation/columns/new/', views.column_edit, name='manage_column_create'),
    path('navigation/columns/<int:pk>/edit/', views.column_edit, name='manage_column_edit'),
    path('navigation/columns/<int:pk>/delete/', views.column_delete, name='manage_column_delete'),
    path('navigation/links/new/', views.footer_link_edit, name='manage_footer_link_create'),
    path('navigation/links/<int:pk>/edit/', views.footer_link_edit, name='manage_footer_link_edit'),
    path('navigation/links/<int:pk>/delete/', views.footer_link_delete, name='manage_footer_link_delete'),

    path('messages/', views.message_list, name='manage_message_list'),
    path('messages/<int:pk>/', views.message_detail, name='manage_message_detail'),
    path('messages/<int:pk>/status/', views.message_status, name='manage_message_status'),
    path('messages/<int:pk>/delete/', views.message_delete, name='manage_message_delete'),

    path('account/', views.account, name='manage_account'),
]
