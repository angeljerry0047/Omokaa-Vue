from rest_framework import serializers
from blog.models import *
from accounts.models import *
from django.contrib.sites.models import Site
from django.conf import settings

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class AccountSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'username', 'profile_pic', 'img_url']

    def get_img_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return settings.STATIC_URL + 'accounts/images/profile.png'


class CommentSerializer(serializers.ModelSerializer):
    author = AccountSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        exclude = ['active']


class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        fields = '__all__'