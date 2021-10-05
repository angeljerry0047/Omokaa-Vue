from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxLengthValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.db.models import Q,F
from io import BytesIO
from PIL import Image
import sys
from utils.compress import compressImage

NOTIFICATION_CHOICES = (
       ('postlike','postlike'),
       ('postdislike','postdislike'),
       ('commentdislike','commentdislike'),
       ('commentlike','commentlike'),
       ('postcomment','postcomment'),
       ('commentreply','commentreply'),
       ('rating','rating')
       )


def upload_location(instance, filename, **kwargs):
    file_path = 'posts/{author_id}/-{filename}'.format(
        author_id=str(instance.author.id), filename=filename)
    return file_path

def upload_location_new(instance, filename, **kwargs):
    file_path = 'posts/{author_id}/-{filename}'.format(
        author_id=str(instance.post.author.id), filename=filename)
    return file_path


class Type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    type = models.ManyToManyField(Type, related_name='category')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategory', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DefaultImage(models.Model):
    profile_image = models.ImageField(upload_to='defaultImg',)
    bg_image = models.ImageField(upload_to='defaultImg')



class Post(models.Model):
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    detail = models.TextField(max_length=800,null=False, blank=False)
    thumbnail = models.ImageField(blank=True, upload_to=upload_location)
    video =  models.FileField(upload_to='videos/', null=True, blank=True, verbose_name="post_video")
    location = models.CharField(max_length=500, null=False, blank=False)
    date_published = models.DateTimeField(auto_now=True, verbose_name='date published')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='date updated')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='post', on_delete=models.CASCADE)
    is_promotional = models.BooleanField(default=False)
    audience = models.CharField(max_length=100, null=True, blank=True)

    slug = models.SlugField(max_length=800, unique_for_date='date_published', null=True, blank=True)

    def __str__(self):
        return self.detail

    def profile_picture(self):
        return self.author.profile_pic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.detail[:500])
        print(self.thumbnail)
        if(self.thumbnail):
            new_image = compressImage(self.thumbnail)
            self.thumbnail =  new_image
        super(Post,self).save(*args,**kwargs)

    class Meta:
        ordering = ['-date_published']

    def get_absolute_url(self):
        return reverse('post_detail',
                       args=[self.id,
                             self.date_published.year,
                             self.date_published.month,
                             self.date_published.day, self.slug])

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='postimages',on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to=upload_location_new)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.image)





class PromotionalDetail(models.Model):
    package_type = models.CharField(choices=(('1000','1000'),('3000','3000')),max_length=20)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_type

# Buy Start
class BuyCommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs

class BuyProposals(models.Model):
    """
       Used when users create milestone to buy a product
       or say when user clicks on button of type sell
    """
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    currency = models.CharField(default='ksh',max_length=20)
    description = models.TextField()
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BuyCommentManager()

    class Meta:
        ordering = ['id']

    def children(self):
        """Return replies of a comment."""
        return BuyProposals.objects.filter(parent=self)
    
    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return self.description
# Buy End

# Sell Start
class SellCommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs


class SellProposals(models.Model):
    """
       Used when users bid to sell a product
       or say when user clicks on button of type Buy
    """
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    currency = models.CharField(default='ksh',max_length=20)
    description = models.TextField()
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SellCommentManager()

    class Meta:
        ordering = ['id']

    def children(self):
        """Return replies of a comment."""
        return SellProposals.objects.filter(parent=self)

    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return self.description
#  Sell End


# Hire Start
class HireCommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs

class HireComment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    description = models.TextField()
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = HireCommentManager()

    class Meta:
        ordering = ['id']

    def children(self):
        """Return replies of a comment."""
        return HireComment.objects.filter(parent=self)

    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return self.description
# Hire End


# Work Start
class WorkCommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs

class WorkProposal(models.Model):
    description = models.TextField()
    document = models.FileField(upload_to='documents/',null=True,blank=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkCommentManager()

    class Meta:
        ordering = ['id']

    def children(self):
        """Return replies of a comment."""
        return WorkProposal.objects.filter(parent=self)

    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return self.description
# Work End

class GroupPost(models.Model):
    description = models.TextField(max_length=500, null=False, blank=False)
    thumbnail = models.ImageField(null=True, blank=True, upload_to=upload_location)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey('UserGroup',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class UserInterest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_interests', on_delete=models.CASCADE)
    sub_category_id = models.IntegerField(null=True,blank=True)
    interest = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.user.username


class ReportedPost(models.Model):
    report_type = models.CharField(choices=(('FRAUD','FRAUD'),('SPAM','SPAM')),max_length=20)
    post = models.ForeignKey(Post,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING)


class ReportedGroupPost(models.Model):
    report_type = models.CharField(choices=(('FRAUD','FRAUD'),('SPAM','SPAM')),max_length=20)
    post = models.ForeignKey(GroupPost,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING)


class Gallery(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    images = models.FileField(upload_to=upload_location, null=True, blank=True)


class PostRating(models.Model):
    rating = models.IntegerField()
    feedback = models.TextField()
    post = models.ForeignKey(Post,related_name='ratings',on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class RatingFeedback(models.Model):
    userrating = models.ForeignKey(PostRating,related_name='rating_feedback',on_delete=models.CASCADE)
    feedback = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']


class GroupPostLikeDislikeParent(models.Model):
    post = models.ForeignKey(GroupPost,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class GroupPostLike(GroupPostLikeDislikeParent):
    pass

class GroupPostDislike(GroupPostLikeDislikeParent):
    pass


class CommentManager(models.Manager):
    """Model manager for `Comment` model."""
    
    def allComment(self):
        return super().all()

    def all(self):
        """Return results of instance with no parent (not a reply)."""
        qs = super().filter(parent=None)
        return qs


class Comment(models.Model):
    post = models.ForeignKey(GroupPost,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    message = models.TextField()
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ['id']

    def children(self):
        """Return replies of a comment."""
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        """Return `True` if instance is a parent."""
        if self.parent is not None:
            return False
        return True

    def __str__(self):
        return self.message

class CommentLikeDislikeParent(models.Model):
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
        
    class Meta:
        abstract = True

class CommentLike(CommentLikeDislikeParent):
    pass

class CommentDislike(CommentLikeDislikeParent):
    pass



class Notification(models.Model):
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='receiver')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='sender')
    action = models.CharField(choices=NOTIFICATION_CHOICES,max_length=100)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,null=True,blank=True)
    groupPost = models.ForeignKey(GroupPost,on_delete=models.CASCADE,null=True,blank=True)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,null=True,blank=True)
    is_opened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.name + " has done " +self.action

    class Meta:
        ordering = ['-id']


class UserGroup(models.Model):
    """
        It saves the group name and how many users are joined in a group
    """
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



