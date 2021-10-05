from rest_framework import serializers
from accounts.models import *
from posts.models import UserInterest
from django.contrib.sites.models import Site
from django.conf import settings

class HelpMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpMessage
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterest
        fields = '__all__'
        read_only_fields = ['id']


class AccountSerializer(serializers.ModelSerializer):
    count_post = serializers.SerializerMethodField()
    img_url = serializers.SerializerMethodField()
    user_interests = UserInterestSerializer(read_only=True, many=True)

    class Meta:
        model = Account
        exclude = ['slug','date_updated','last_login','is_admin', 'is_staff','is_superuser','is_verified']

    def get_count_post(self, obj):
        return obj.post.count()
    
    def get_img_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return settings.STATIC_URL + 'accounts/images/profile.png'


    def create(self, validated_data):
        """ Creates and returns a new user """
        # Validating Data
        user = Account(
            name=validated_data['name'],
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            country_code=validated_data['country_code'],
            is_email_public=validated_data['is_email_public'],
            is_phone_public=validated_data['is_phone_public']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = Account
        fields = [ 'name' , 'username', 'email', 'phone', 'password', 'password2']
        extra_kwargs = {
             'password': {'write_only': True}
        }
    def  save(self):
            account = Account(
                name = self.validated_data['name'],
                username=self.validated_data['username'],
                email=self.validated_data['email'],
                phone=self.validated_data['phone'],


            )
            password = self.validated_data['password']
            password2 = self.validated_data['password2']

            if password != password2:
                raise serializers.ValidationError({'password : Passwords must match!'})
                
            account.set_password(password)
            account.save()
            return account


class FeedbackSerialiazer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    class Meta:
        model = Feedback
        fields = '__all__'
