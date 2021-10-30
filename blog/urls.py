from django.urls import path
from .views import post_list, post_detail, post_create, post_edit, post_delete, post_share, post_search
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    path('post/create/', post_create, name='post_create'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('post/edit/<int:pk>/', post_edit, name='post_edit'),
    path('post/delete/<int:pk>/', post_delete, name='post_delete'),
    path('', post_list, name='post_list'),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', post_list, name='post_list_by_tag'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('search/', post_search, name='post_search'),
]