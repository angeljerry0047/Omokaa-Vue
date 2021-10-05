from django.urls import include,path
from rest_framework.routers import DefaultRouter
from blog.api import views as views

router = DefaultRouter()
router.register(r"comment", views.CommentViewset)
router.register(r"article", views.ArticleViwsets)


urlpatterns = [
    path("",include(router.urls))
]