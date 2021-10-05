from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # blog views
    path('articles_list/', views.blog_list, name='articles_list'),
    path('blog-comment-reply/',views.article_comment_reply,name='article_comment_reply'),
    path('submit_comment',views.submit_comment,name='submit_comment'),
    path('<int:year>/<int:month>/<int:day>/<slug:article>/', views.blog_detail, name='article_detail'),
]