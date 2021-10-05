from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save,pre_save
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from posts.models import Post,PostRating,Comment,CommentLike,CommentDislike,GroupPostLike,GroupPostDislike,Notification, BuyProposals, WorkProposal, SellProposals, HireComment


@receiver(post_save,sender=Post)
def save_post(sender,instance,created,**kwargs): 
    instance.slug  = str(instance.id) + str(instance.detail[:500])


@receiver(pre_save,sender=Post)
def pre_save_post(sender,instance,**kwargs):
    if(instance.author.email == 'Lizawanjau@gmail.com'):
        Post.objects.filter(author=instance.author).update(is_promotional=False)
        instance.is_promotional = True


# Creating notification if user submits a comment on Post or Comment
@receiver(post_save,sender=Comment)
def save_comment(sender, instance, created, **kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.user
        post = instance.post
        if instance.parent:
        	notification = Notification(receiver=receiver,sender=sender,action='commentreply',comment=instance.parent)
        else:
        	notification = Notification(receiver=receiver,sender=sender,action='postcomment',groupPost=instance.post)
        notification.save()


@receiver(post_save,sender=GroupPostLike)
def post_like(sender, instance, created, **kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.user
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='postlike',groupPost=post)
        notification.save()


@receiver(post_save,sender=GroupPostDislike)
def post_dislike(sender, instance, created, **kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.user
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='postdislike',groupPost=post)
        notification.save()


@receiver(post_save,sender=CommentLike)
def comment_like(sender, instance, created, **kwargs):
    if created:
        receiver = instance.comment.user 
        sender = instance.user
        comment = instance.comment
        notification = Notification(receiver=receiver,sender=sender,action='commentlike',comment=comment)
        notification.save()


@receiver(post_save,sender=CommentDislike)
def comment_dislike(sender, instance, created, **kwargs):
    if created:
        receiver = instance.comment.user 
        sender = instance.user
        comment = instance.comment
        notification = Notification(receiver=receiver,sender=sender,action='commentdislike',comment=comment)
        notification.save()
        

@receiver(post_save,sender=PostRating)
def post_rating(sender,instance,created,**kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.user
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='rating',post=post)
        notification.save()


@receiver(post_save,sender=BuyProposals)
def buy_proposal(sender,instance,created,**kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.bidder
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='proposal',post=post)
        notification.save()


@receiver(post_save,sender=SellProposals)
def sell_proposal(sender,instance,created,**kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.bidder
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='proposal',post=post)
        notification.save()


@receiver(post_save,sender=HireComment)
def hire_comment(sender,instance,created,**kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.bidder
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='proposal',post=post)
        notification.save()


@receiver(post_save,sender=WorkProposal)
def work_proposal(sender,instance,created,**kwargs):
    if created:
        receiver = instance.post.author 
        sender = instance.bidder
        post = instance.post
        notification = Notification(receiver=receiver,sender=sender,action='proposal',post=post)
        notification.save()