from django.urls import include,path
from rest_framework.routers import DefaultRouter
from chat.api import views as views

router = DefaultRouter()
router.register(r"chat-notification",views.ChatNotificationViewset)
router.register(r"chat-message",views.ChatMessageViewset)
router.register(r"chats",views.ChatViewset)


urlpatterns = [
    path("",include(router.urls))

]