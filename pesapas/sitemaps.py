from django.contrib.sitemaps import Sitemap
from blog.models import Article
from posts.models import Post
from accounts.models import Account


class PostSitemap(Sitemap):
    changefreq = 'always'
    priority = 1

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.date_updated


class ArticleSitemap(Sitemap):
    changefreq = 'always'
    priority = 0.9

    def items(self):
        return Article.published.all()

    def lastmod(self, obj):
        return obj.updated


class AccountSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Account.objects.all()

    def lastmod(self, obj):
        return obj.date_updated
