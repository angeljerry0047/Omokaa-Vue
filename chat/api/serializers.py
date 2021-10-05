from rest_framework import serializers
from chat.models import *
from accounts.models import *
from django.contrib.sites.models import Site
from django.conf import settings

class AccountSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'username', 'profile_pic', 'img_url']

    def get_img_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return settings.STATIC_URL + 'accounts/images/profile.png'


class ChatNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatNotification
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = AccountSerializer(read_only=True)
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    user1 = AccountSerializer(read_only=True)
    user2 = AccountSerializer(read_only=True)
    msg = ChatMessageSerializer(many=True, read_only=True)
    notification = ChatNotificationSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = '__all__'

