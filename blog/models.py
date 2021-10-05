from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager
from django.utils.text import slugify

# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Article (models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_query_name='blog_posts')
    created = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='draft')
    slug = models.SlugField(max_length=200, unique_for_date='publish')
    tags = TaggableManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        slug = self.title
        self.slug = slugify(slug)
        super(Article,self).save(*args,**kwargs)

    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # The custom manager

    def get_absolute_url(self):
        return reverse('blog:article_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])


class CommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs
 
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    comment = models.TextField()
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True,related_name='comment_reply')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    objects = CommentManager()

    class Meta:
        ordering = ('-created',)

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return str(self.author)+ str(self.article)
