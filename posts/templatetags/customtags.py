from django import template
from django.db.models import Sum,Count
from posts.models import GroupPostLike,GroupPostDislike,Notification,PostRating, BuyProposals, SellProposals, WorkProposal, HireComment
from chat.models import ChatNotification
from accounts.models import Account
import os


register = template.Library()

@register.simple_tag
def setvar(val=None):
  return val

@register.filter
def filename(value):
	return os.path.basename(value.file.name)

@register.filter
def averageRating(postid):
	"""
		method to calculate rating of a post
		Formula used:
		    (5*252 + 4*124 + 3*40 + 2*29 + 1*33) / (252+124+40+29+33) = 4.11
		stackoverflowlink: https://stackoverflow.com/questions/10196579/algorithm-used-to-calculate-5-star-ratings
	"""
	ratings = PostRating.objects.filter(post_id=postid).order_by('rating').values('rating').annotate(rate_total=Sum('rating'))
	rating = 0
	numerator = 0
	denominator = 0
	for rate in ratings:
		numerator = numerator + (int(rate['rating']) * int(rate['rate_total']))
		denominator = denominator + int(rate['rate_total'])
	if denominator:
		rating = numerator/denominator
	return round(rating,1)

@register.filter
def isLikedDisliked(postLikes,userId):
	return len(postLikes.filter(user_id=userId))

@register.filter
def isTypeChecked(userInterest,typeid):
	if userInterest:
		for interest in userInterest:
			if interest['types'][0] == str(typeid):
				return True
		return False
	else:
		return False


@register.filter
def hasReviewed(userId,postId):
	review = PostRating.objects.filter(user_id=userId,post_id=postId)
	if review:
		return True
	return False

@register.filter
def one_more(userInterest,categoryid):
	return userInterest,categoryid

@register.filter
def hasOffered(one_more_arguments,offer_type):
	userid,postid = one_more_arguments
	proposal = False
	if offer_type.lower() == 'buy':
		proposal = SellProposals.objects.filter(bidder__id = userid,post__id=postid).count()
	elif offer_type.lower() == 'sell':
		proposal = BuyProposals.objects.filter(bidder__id = userid,post__id=postid).count()
	elif offer_type.lower() == 'hire':
		proposal = WorkProposal.objects.filter(bidder__id = userid,post__id=postid).count()
	elif offer_type.lower() == 'work':
		proposal = HireComment.objects.filter(bidder__id = userid,post__id=postid).count()
	if proposal:
		return True
	return False

@register.filter
def isCategoryChecked(one_more_arguments,typeid):
	userInterest,categoryid = one_more_arguments
	if userInterest:
		for interest in userInterest:
			if interest['types'][0] == str(typeid):
				for category in interest['categories']:
					if category['category'][0] == str(categoryid):
						return True 
		return False
	else:
		return False

@register.filter
def isSubCategoryChecked(one_more_arguments,typeid):
	userInterest,subcategoryid = one_more_arguments
	if userInterest:
		for interest in userInterest:
			if interest['types'][0] == str(typeid):
				for category in interest['categories']:
					if str(subcategoryid) in category['sub_categories']:
						return True 
		return False
	else:
		return False



@register.filter
def totalLikesDislikes(postLikes):
	return len(postLikes)

@register.filter
def totalComments(posts):
	return len(posts)

@register.filter
def totalQuery(posts):
	return len(posts)

@register.filter
def totalNotifications(userId):
	return Notification.objects.filter(receiver_id=userId,is_opened=False).exclude(sender_id=userId).count()

@register.filter
def totalChatNotifications(userId):
	return ChatNotification.objects.filter(msg_receiver_id=userId,is_checked=False).count()

@register.filter
def singleNotification(conversation,receiverId):
	return ChatNotification.objects.filter(chat_id=conversation.id,msg_receiver_id=receiverId,is_checked=False).count()
