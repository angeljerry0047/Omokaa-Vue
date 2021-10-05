from django.urls import include,path
from rest_framework.routers import DefaultRouter
from posts.api import views

router = DefaultRouter()
router.register(r"post", views.PostViewset, basename='Post')
router.register(r"type", views.TypeViewset)
router.register(r"category", views.CategoryViewset)
router.register(r"sub-category", views.SubCategoryViewset)
router.register(r"post-rating", views.PostRatingViewset)
router.register(r"buy-proposals", views.BuyProposalsViewset)
router.register(r"sell-proposals", views.SellProposalsViewset)
router.register(r"work-proposals", views.WorkProposalViewset)
router.register(r"hire-proposals", views.HireCommentViewset)
router.register(r"rating-feedback", views.RatingFeedbackViewset)
router.register(r"report-post", views.ReportedPostViewset)
router.register(r"notifications", views.NotificationViewset)
router.register(r"interests", views.UserInterestViewset)
# router.register(r"promotional-detail", views.PromotionalDetailViewset)
# router.register(r"currency", views.CurrencyViewset)
# router.register(r"default-image", views.DefaultImageViewset)
# router.register(r"user-group", views.UserGroupViewset)
# router.register(r"comment", views.CommentViewset)
# router.register(r"gallery", views.GalleryViewset)
# router.register(r"reported-grouppost", views.ReportedGroupPostViewset)
# router.register(r"group-post", views.GroupPostViewset)


urlpatterns = [
    path("",include(router.urls)),
]