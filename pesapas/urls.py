"""omokaa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap, PostSitemap, AccountSitemap
# from mpesa.urls import mpesa_urls
sitemaps = {
    'posts': PostSitemap,
    'articles': ArticleSitemap,
    'accounts': AccountSitemap
    }


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('chat/', include('chat.urls')),
    # path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('password_reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    # path('blog/', include('blog.urls', namespace='blog')),
    # path('', include('accounts.urls')),
    # path('', include('posts.urls')),

    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    #API
    path('accounts/api/', include('accounts.api.urls')),
    path('blog/api/', include('blog.api.urls')),
    path('chat/api/', include('chat.api.urls')),
    path('posts/api/', include('posts.api.urls')),

    path('paypal/', include('paypal.standard.ipn.urls')),
    # path('payments/', include('payments.urls')),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
