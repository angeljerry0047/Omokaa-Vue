import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import ChatMessage, Chat
from asgiref.sync import sync_to_async
from accounts.models import Account
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		# accept connection
		self.user = self.scope['user']
		self.user_id = self.scope['url_route']['kwargs']['user_id']

		#accept connection
		await self.accept()

		self.joined_rooms = await get_rooms(self.user_id)
		for room in self.joined_rooms:
			await self.channel_layer.group_add(
				'group_' + room,
				self.channel_name
				)

	async def disconnect(self, close_code):
		for room in self.joined_rooms:
			await self.channel_layer.group_discard(
				'group_' + room,
				self.channel_name
				)
		return

 	# receive message from WebSocket
	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		chatid = text_data_json['chatid']
		msgType = text_data_json['msgType']
		filename = text_data_json['filename']
		# chat =  await fetchChat(chatid)
		await createMessageInstance(sender_id=self.user_id,message=message,chat_id=chatid,msgType=msgType,filename=filename)
		now = timezone.now()
		# send message to room group
		await self.channel_layer.group_send(
			'group_' + str(chatid),
			{
				'type': 'chat_message',
				'message': message,
				'userid': self.user_id,
				'chatId': chatid,
				'datetime': now.isoformat(),
				'msgType':msgType,
				'filename':filename
			}
		)

	# receive message from room group
	async def chat_message(self, event):
		# Send message to WebSocket
		await self.send(text_data=json.dumps(event))

@sync_to_async
def fetchChat(chatid):
 	return Chat.objects.get(id=chatid)

@sync_to_async
def createMessageInstance(sender_id,message,chat_id,msgType,filename):
	chatmessage  = ChatMessage(sender_id=sender_id,message=message,chat_id=chat_id)
	if msgType == 'file':
		chatmessage.is_file = True
		chatmessage.filename = filename
	chatmessage.save()
	return

@sync_to_async
def get_rooms(user_id):
	chats = Chat.objects.filter(Q(user1_id=user_id) | Q(user2_id=user_id))
	roomList = []
	for elem in chats:
		roomList.append(str(elem.id))

	return roomList
