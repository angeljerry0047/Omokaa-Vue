from django.urls import include,path
from rest_framework.routers import DefaultRouter
from accounts.api import views as views

from rest_framework.authtoken.views import ObtainAuthToken

router = DefaultRouter()
router.register(r"help-message", views.HelpMessageViewset)
router.register(r"feedback", views.FeedbackViewset)
router.register(r"account", views.AccountViewset)

urlpatterns = [
    path("", include(router.urls)),
    path('login/', views.CustomObtainAuthToken.as_view(), name="login"),
    path('account/activate/<uidb64>/<token>/',views.activate, name='activate_user'),
]