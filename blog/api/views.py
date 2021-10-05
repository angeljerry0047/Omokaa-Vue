from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response # use DRF's response class
from rest_framework import status
from rest_framework.decorators import action
from blog.api.serializers import * 


class CommentViewset(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['POST'])
    def reply(self, request):
        commentid = request.POST.get('commentid')
        comment_text = request.POST.get('comment')
        comment = Comment.objects.get(id=commentid)
        new_comment = Comment(article=comment.article, author=request.user, comment=comment_text,parent=comment)
        new_comment.save()
        comments = Comment.objects.all().filter(article__id=comment.article.id)

        return Response(status=status.HTTP_200_OK)


class ArticleViwsets(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
