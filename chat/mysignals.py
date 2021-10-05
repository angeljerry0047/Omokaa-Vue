from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from chat.models import Chat,ChatMessage,ChatNotification


# Creating notification for receiver if user sends a message.
@receiver(post_save,sender=ChatMessage)
def save_comment(sender, instance, created, **kwargs):
    if created:
        # One who sends the message
        msg_sender = instance.sender
        chat = instance.chat
        # Check who is the receiver
        if instance.chat.user1 == msg_sender:
        	msg_receiver = instance.chat.user2
        else:
        	msg_receiver = instance.chat.user1

        # Check if there is already an instance of chatNotification created between them.
        chat_notification = ChatNotification.objects.filter(chat=chat,msg_sender=msg_sender,msg_receiver=msg_receiver)
        if len(chat_notification):
        	chat_notification = chat_notification[0]
        	chat_notification.msg_counter += 1
        	chat_notification.is_checked = False
        	chat_notification.save()
        else:
        	new_chat_notification = ChatNotification(chat=chat,msg_sender=msg_sender,msg_receiver=msg_receiver)
        	new_chat_notification.save()

        # mark as read to the old notification of sender
        # old_chat_notification = ChatNotification.objects.filter(chat=chat,msg_receiver=msg_sender)
        # if len(old_chat_notification):
        # 	old_chat_notification = old_chat_notification[0]
        # 	if not old_chat_notification.is_checked:
        # 		old_chat_notification.is_checked = True
        # 		old_chat_notification.msg_counter = 0
        # 		old_chat_notification.save()