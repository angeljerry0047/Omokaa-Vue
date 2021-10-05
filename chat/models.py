from django.db import models
from posts.models import Post
from django.conf import settings
# Create your models here.



class Chat(models.Model):
	# user1 is the one who starts message,user2 is the author
	user1 = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user1')
	user2 = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user2')
	post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post')

	def lastmessage(self):
		try:
			return self.chatmessage_set.all().latest('id').message
		except IndexError:
			return None

	def lastmessagedate(self):
		try:
			return self.chatmessage_set.all().latest('id').created_at.date()
		except IndexError:
			return None


class ChatMessage(models.Model):
	sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	message = models.TextField()
	chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='msg')
	is_file = models.BooleanField(default=False)
	filename = models.CharField(max_length=250,null=True,blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message


class ChatNotification(models.Model):
	chat = models.ForeignKey(Chat,on_delete=models.CASCADE, related_name="notification")
	msg_sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='msg_sender')
	msg_receiver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='msg_receiver')
	msg_counter = models.IntegerField(default=0)
	is_checked = models.BooleanField(default=False)