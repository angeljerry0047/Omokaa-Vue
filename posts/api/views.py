from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response # use DRF's response class
from rest_framework import status
from posts.api.serializers import * 
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from posts.models import Category

from django.http import HttpResponse,JsonResponse
from django.db.models import Sum
from posts.models import RatingFeedback,WorkProposal,HireComment,SellProposals,BuyProposals,PromotionalDetail,DefaultImage,ReportedGroupPost,UserGroup,GroupPost,UserInterest,ReportedPost,Post, Gallery,Type, PostRating, Category, SubCategory, GroupPostLike, GroupPostDislike, Comment, CommentLike, CommentDislike, Notification
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

class Postspagination(PageNumberPagination):
    page_size = 5


class PostViewset(viewsets.ModelViewSet):
    pagination_class = Postspagination
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            interests = UserInterest.objects.filter(user=self.request.user.id)
            sub_category_list = []
            if len(interests) == 0:
                sub_category_list = SubCategory.objects.all()
            else:
                for elem in interests:
                    sub_category_list.append(elem.sub_category_id)
            country_code = ''
            if (self.request.GET.get('selectedCountryCode', '')):
                country_code = self.request.GET['selectedCountryCode']
                user = Account.objects.get(id=int(self.request.user.id))
                user.explore_locations = country_code
                user.save()
            return Post.objects.filter(sub_category__in=sub_category_list, audience__contains=country_code)
        else:
            type_id = self.request.GET.get('type','')
            if type_id:
                type_id=[type_id]
            else: 
                type_id=Type.objects.all()

            category_id = self.request.GET.get('category', '')
            if category_id:
                category_id=[category_id]
            else: 
                category_id=Category.objects.all()
            
            sub_category_id = self.request.GET.get('sub_category', '')
            if sub_category_id:
                sub_category_id=[sub_category_id]
            else:
                sub_category_id=SubCategory.objects.all()
            location = self.request.GET.get('location','')

            text = self.request.GET.get('q', '')
            results = Post.objects.filter(type_id__in=type_id, category_id__in=category_id,sub_category_id__in=sub_category_id, location__contains=location, detail__contains=text)

            return results

    def create(self, request, *args, **kwargs):
        instance = Post(
            type_id=request.POST['type'],
            sub_category_id=request.POST['sub_category'],
            category_id=request.POST['category'],
            location=request.POST['location'],
            detail=request.POST['detail'],
            author=request.user,
            audience=request.POST['audience']
        )
        instance.save()
        images = request.FILES.getlist('images')
        for image in images:
            PostImage.objects.create(image=image,post=instance)

        serializer = PostSerializer(instance, many=False)
        return JsonResponse(serializer.data, safe=False)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticatedOrReadOnly])
    def get_by_user(self, request, pk):
        results = Post.objects.filter(author=pk)
        serializer = PostSerializer(results, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def filter_by_keywords(self, request):
        search_type = request.POST['search_type']
        searched_keyword = request.POST['keyword']
        if search_type == 'bio':
            results = Account.objects.filter(bio__icontains=searched_keyword)
            serializer = AccountSerializer(results, many=True)
            return JsonResponse(serializer.data, safe=False)
        elif search_type == 'people':
            results = Account.objects.filter(Q(Q(name__icontains=searched_keyword) | Q(username__icontains=searched_keyword)), Q(user_type=1) | Q(user_type=None))
            serializer = AccountSerializer(results, many=True)
            return JsonResponse(serializer.data, safe=False)
        elif search_type == 'merchant':
            results = Account.objects.filter(Q(Q(name__icontains=searched_keyword) | Q(username__icontains=searched_keyword)),user_type=2)
            serializer = AccountSerializer(results, many=True)
            return JsonResponse(serializer.data, safe=False)
        elif search_type == 'post':
            type_id=request.POST.get('type', '')
            if type_id:
                type_id=[type_id]
            else:
                type_id=Type.objects.all()
            category_id=request.POST.get('category', '')
            if category_id:
                category_id=[category_id]
            else:
                category_id=Category.objects.all()
            sub_category_id=request.POST.get('sub_category', '')
            if sub_category_id:
                sub_category_id=[sub_category_id]
            else:
                sub_category_id=SubCategory.objects.all()
            location=request.POST.get('location','')
            if (self.request.user.is_authenticated):
                audience = self.request.user.explore_locations
                results = Post.objects.filter(type_id__in=type_id, category_id__in=category_id,sub_category_id__in=sub_category_id, location__contains=location, detail__contains=searched_keyword, audience__contains=audience)
                serializer = PostSerializer(results, many=True)
                return JsonResponse(serializer.data, safe=False)
            else:
                results = Post.objects.filter(type_id__in=type_id, category_id__in=category_id,sub_category_id__in=sub_category_id, location__contains=location, detail__contains=searched_keyword)
                serializer = PostSerializer(results, many=True)
                return JsonResponse(serializer.data, safe=False)


class PostRatingViewset(viewsets.ModelViewSet):
    serializer_class = PostRatingSerializer
    queryset = PostRating.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def assign(self, request, pk):
        postid = request.POST.get('post')
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating')
        post = Post.objects.get(id=postid)
        #check if user has already submitted a feedback for the same post.
        post_rating  = PostRating.objects.filter(user=request.user, post_id=post.id)
        if post_rating:
            post_rating = post_rating.latest('id')
        else:
            post_rating = PostRating(post=post,user=request.user)
        post_rating.rating = rating
        post_rating.feedback = feedback
        post_rating.save()
        return Response(status=status.HTTP_200_OK)


class BuyProposalsViewset(viewsets.ModelViewSet):
    serializer_class = BuyProposalsSerializer
    queryset = BuyProposals.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)

    @action(detail=False, methods=['POST'])
    def get_by_post(self, request):
        post_id = request.POST['postid']
        data = BuyProposals.objects.filter(post=post_id, parent=None)
        serializer = BuyProposalsSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['POST'])
    def feedback(self, request):
        proposal_id = request.POST['proposal_id']
        feedback = request.POST['feedback']
        proposal = BuyProposals.objects.get(id=proposal_id)
        post_id = proposal.post_id
        data = {'description': feedback, 'parent': proposal_id, 'post': proposal.post_id}
        serializer = BuyProposalsSerializer(data=data)
        serializer.is_valid()
        serializer.save(bidder=self.request.user)

        return Response(status=status.HTTP_200_OK)

class SellProposalsViewset(viewsets.ModelViewSet):
    serializer_class = SellProposalsSerializer
    queryset = SellProposals.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)

    @action(detail=False, methods=['POST'])
    def get_by_post(self, request):
        post_id = request.POST['postid']
        data = SellProposals.objects.filter(post=post_id, parent=None)
        serializer = SellProposalsSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['POST'])
    def feedback(self, request):
        proposal_id = request.POST['proposal_id']
        feedback = request.POST['feedback']
        proposal = SellProposals.objects.get(id=proposal_id)
        post_id = proposal.post_id
        data = {'description': feedback, 'parent': proposal_id, 'post': proposal.post_id}
        serializer = SellProposalsSerializer(data=data)
        serializer.is_valid()
        serializer.save(bidder=self.request.user)
        return Response(status=status.HTTP_200_OK)


class WorkProposalViewset(viewsets.ModelViewSet):
    serializer_class = WorkProposalSerializer
    queryset = WorkProposal.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)

    @action(detail=False, methods=['POST'])
    def get_by_post(self, request):
        post_id = request.POST['postid']
        data = WorkProposal.objects.filter(post=post_id, parent=None)
        serializer = WorkProposalSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['POST'])
    def feedback(self, request):
        proposal_id = request.POST['proposal_id']
        feedback = request.POST['feedback']
        proposal = WorkProposal.objects.get(id=proposal_id)
        post_id = proposal.post_id
        data = {'description': feedback, 'parent': proposal_id, 'post': proposal.post_id}
        serializer = WorkProposalSerializer(data=data)
        serializer.is_valid()
        serializer.save(bidder=self.request.user)
        return Response(status=status.HTTP_200_OK)

class HireCommentViewset(viewsets.ModelViewSet):
    serializer_class = HireCommentSerializer
    queryset = HireComment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)

    @action(detail=False, methods=['POST'])
    def get_by_post(self, request):
        post_id = request.POST['postid']
        data = HireComment.objects.filter(post=post_id, parent=None)
        serializer = HireCommentSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['POST'])
    def feedback(self, request):
        proposal_id = request.POST['proposal_id']
        feedback = request.POST['feedback']
        proposal = HireComment.objects.get(id=proposal_id)
        post_id = proposal.post_id
        data = {'description': feedback, 'parent': proposal_id, 'post': proposal.post_id}
        serializer = HireCommentSerializer(data=data)
        serializer.is_valid()
        serializer.save(bidder=self.request.user)
        return Response(status=status.HTTP_200_OK)


class SubCategoryViewset(viewsets.ModelViewSet):
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()


class CategoryViewset(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class TypeViewset(viewsets.ModelViewSet):
    serializer_class = TypeSerializer
    queryset = Type.objects.all()
    permission_classes = [AllowAny]


class UserGroupViewset(viewsets.ModelViewSet):
    serializer_class = UserGroupSerializer
    queryset = UserGroup.objects.all()
    # permission_classes = [IsAuthenticated]


class NotificationViewset(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'])
    def messages(self, request):
        user_id = request.POST['user_id']
        data = Notification.objects.filter(receiver_id=user_id)
        serializer = NotificationSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    @action(detail=True, methods=['POST'])
    def open(self, request, pk):
        instance = self.get_object()
        data = {'is_opened': True}
        serializer = NotificationSerializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CommentViewset(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    # permission_classes = [IsAuthenticated]


class RatingFeedbackViewset(viewsets.ModelViewSet):
    serializer_class = RatingFeedbackSerializer
    queryset = RatingFeedback.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GalleryViewset(viewsets.ModelViewSet):
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all()
    # permission_classes = [IsAuthenticated]


class ReportedGroupPostViewset(viewsets.ModelViewSet):
    serializer_class = ReportedGroupPostSerializer
    queryset = ReportedGroupPost.objects.all()
    # permission_classes = [IsAuthenticated]


class ReportedGroupPostViewset(viewsets.ModelViewSet):
    serializer_class = ReportedGroupPostSerializer
    queryset = ReportedGroupPost.objects.all()
    # permission_classes = [IsAuthenticated]


class ReportedPostViewset(viewsets.ModelViewSet):
    serializer_class = ReportedPostSerializer
    queryset = ReportedPost.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserInterestViewset(viewsets.ModelViewSet):
    serializer_class = UserInterestSerializer
    queryset = UserInterest.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'])
    def multi_create(self, serializer):
        interest_ids = self.request.POST.get('sub_ids',[])
        interest_ids = json.loads(interest_ids)
        UserInterest.objects.filter(user=self.request.user).delete()
        for sub_id in interest_ids:
            item, created = UserInterest.objects.update_or_create(sub_category_id=sub_id, user=self.request.user)
            item.save()
        return Response(status=status.HTTP_200_OK)


class GroupPostViewset(viewsets.ModelViewSet):
    serializer_class = GroupPostSerializer
    queryset = GroupPost.objects.all()
    # permission_classes = [IsAuthenticated]


class PromotionalDetailViewset(viewsets.ModelViewSet):
    serializer_class = PromotionalDetailSerializer
    queryset = PromotionalDetail.objects.all()
    # permission_classes = [IsAuthenticated]


class DefaultImageViewset(viewsets.ModelViewSet):
    serializer_class = DefaultImageSerializer
    queryset = DefaultImage.objects.all()
    # permission_classes = [IsAuthenticated]


class CurrencyViewset(viewsets.ModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    # permission_classes = [IsAuthenticated]

