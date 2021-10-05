from django.shortcuts import render,get_object_or_404
from . models import Article, Comment
from . forms import CommentForm
from django.db.models import Count
from django.http import HttpResponse,JsonResponse

# Create your views here.
def blog_list(request):
    articles = Article.published.all()
    return render(request,
                  'blog/articles_list.html',
                  {'articles': articles})


def blog_detail(request, year, month, day, article):
    article = get_object_or_404(Article, slug=article,
                            status='published',
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    comments = Comment.objects.all().filter(article=article)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.article = article
            new_comment.save()
    else:
        comment_form = CommentForm()

    article_tags_ids = article.tags.values_list('id', flat=True)
    related_articles = Article.published.filter(tags__in=article_tags_ids).exclude(id=article.id)
    related_articles = related_articles.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/article_detail.html', {'article': article,
                                                        'comments': comments,
                                                        'new_comment': new_comment,
                                                        'comment_form': comment_form,
                                                        'related_articles': related_articles})


def article_comment_reply(request):
    commentid = request.POST.get('commentid')
    comment_text = request.POST.get('comment')
    comment = Comment.objects.get(id=commentid)
    new_comment = Comment(article=comment.article,author=request.user,comment=comment_text,parent=comment)
    new_comment.save()
    comments = Comment.objects.all().filter(article__id=comment.article.id)
    return render(request,'snippets/blog_comments.html',{'comments':comments})


def submit_comment(request):
    comment_text = request.POST.get('comment')
    articleid = request.POST.get('articleid')
    article = Article.objects.get(id=articleid)
    new_comment = Comment(article=article,author=request.user,comment=comment_text)
    new_comment.save()
    comments = Comment.objects.all().filter(article__id=articleid)
    return render(request,'snippets/blog_comments.html',{'comments':comments})
    