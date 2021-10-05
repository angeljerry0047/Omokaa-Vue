from rest_framework import serializers
from posts.models import *
from accounts.models import Account
from django.contrib.sites.models import Site
from django.conf import settings

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'



class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class ReportedGroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedGroupPost
        fields = '__all__'


class GroupPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPost
        fields = '__all__'


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'


class PromotionalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionalDetail
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    count_post = serializers.SerializerMethodField()
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'username', 'profile_pic', 'bio', 'count_post', 'img_url', 'date_joined']

    def get_img_url(self, obj):
        if obj.profile_pic:
            return obj.profile_pic.url
        return settings.STATIC_URL + 'accounts/images/profile.png'

    def get_count_post(self, obj):
        return obj.post.count()


class RatingFeedbackSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    class Meta:
        model = RatingFeedback
        fields = '__all__'


class PostRatingSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    rating_feedback = RatingFeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = PostRating
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    author = AccountSerializer(read_only=True)
    ratings = PostRatingSerializer(many=True, read_only=True)
    count_reviews = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    postimages = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = ['slug']

    def get_count_reviews(self, obj):
        return obj.ratings.count()

    def get_avg_rating(self, obj):
        avg = 0
        total = 0
        for item in obj.ratings.all():
            total += item.rating
        if obj.ratings.count():
            return round(total / obj.ratings.count())
        return 0


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class BuyProposalsSerializer(serializers.ModelSerializer):
    bidder = AccountSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)
    
    class Meta:
        model = BuyProposals
        fields = '__all__'


class SellProposalsSerializer(serializers.ModelSerializer):
    bidder = AccountSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)
    # post = PostRatingSerializer(read_only=True)
    # parent = PostSerializer(read_only=True)

    class Meta:
        model = SellProposals
        fields = '__all__'


class WorkProposalSerializer(serializers.ModelSerializer):
    bidder = AccountSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = WorkProposal
        fields = '__all__'


class HireCommentSerializer(serializers.ModelSerializer):
    bidder = AccountSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)

    class Meta:
        model = HireComment
        fields = '__all__'


class DefaultImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultImage
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    subcategory = SubCategorySerializer(many=True)
    class Meta:
        model = Category
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = Type
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    receiver = AccountSerializer(read_only=True)
    sender = AccountSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = '__all__'


class ReportedPostSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    class Meta:
        model = ReportedPost
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    class Meta:
        model = UserInterest
        fields = ['user', 'id']
        read_only_fields = ['id']