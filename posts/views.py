from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from chat.models import Chat,ChatMessage,ChatNotification
from posts.models import *
from posts.forms import CreatePostForm, CreateSearchForm, CreateResultForm, CreateUnAuthForm, CreateGroupPost
from accounts.models import Account
from accounts.forms import ProfilePicForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.db.models import Q,Sum,Count,Max,Case, When
import json
from django.conf import settings
from django.http import HttpResponseForbidden
import boto3, uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import datetime
 

NO_OF_POSTS = 5

def home(request):
    nointerest = True #use to check if user has any interest selected or not
    user = request.user

    form = CreatePostForm()
    profile_form = ProfilePicForm()
    interest = None
    types = Type.objects.all().order_by('name')

    if not user.is_authenticated:
        filter_form = CreateUnAuthForm()
        context = {
            'nointerest':nointerest,
            'types':types,
            'filter_form':filter_form,
            'post_form':form
        }
        return render(request,'posts/home.html', context)

    # fetching the interests of loggedin user
    userInterest = UserInterest.objects.filter(user=request.user)
    if userInterest:
        nointerest = False
        interest = userInterest[0].interest
    context = {'post_form': form,
               'interest_types':types,
               'userInterest':interest,
               'nointerest':nointerest,
               'types':types
               }

    return render(request, 'posts/home.html', context)


@login_required
def upload_chat_document(request):
    file = request.FILES.get('file')

    #Using Random file names
    filename = str(uuid.uuid4()) + file.name 
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    
    # Path to upload file
    file_path = settings.AWS_MEDIA_LOCATION + '/chatDocuments/' + filename
    file_object = bucket.put_object(Key=file_path,Body=file)
    
    #Access Link of submitted file
    file_url = '{}{}'.format(settings.AWS_FILE_URL,file_object.key)
    file_name = file.name
    return JsonResponse({'file_url':file_url,'file_name':file_name})


@login_required 
def create_ordinary_post(request):
    # images = request.FILES.getlist('thumbnail')
    # images = request.FILES['thumbnail']
    # print(images)
    # length = request.FILES['length']
    # print(length)
    image = request.FILES.getlist('thumbnail')
    
        # photo.save()
    
    # image1 = request.FILES.getlist('thumbnail')[0]
    # print(image1)
    # image2 = request.FILES.getlist('thumbnail')[1]
    # print(image2)

    
    form = CreatePostForm(request.POST,request.FILES)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        for photo in image:
            print(photo)
            PostImage.objects.create(image=photo,post=Post.objects.last())
            
    else:
        print(form.errors)
    return JsonResponse({'status':200})        


@login_required
def create_proposal(request):
    postid = request.POST.get('postid')
    offer = request.POST.get('offer')
    offerType = request.POST.get('offertype')
    post = Post.objects.get(id=postid)
    if offerType == 'buy':
        is_present = BuyProposals.objects.filter(post=post,bidder=request.user)
        if is_present.count():
            proposal = is_present.latest('-id')
            proposal.description = offer
        else:
            proposal = BuyProposals(post=post,description=offer,bidder=request.user)
    elif offerType == 'sell':
        is_present = SellProposals.objects.filter(post=post,bidder=request.user)
        if is_present.count():
            proposal = is_present.latest('-id')
            proposal.description = offer
        else:
            proposal = SellProposals(post=post,description=offer,bidder=request.user)
    elif offerType == 'work':
        is_present = WorkProposal.objects.filter(post=post,bidder=request.user)
        if is_present.count():
            proposal = is_present.latest('-id')
            proposal.description = offer
        else:
            proposal = WorkProposal(post=post,description=offer,bidder=request.user)
    elif offerType == 'hire':
        is_present = HireComment.objects.filter(post=post,bidder=request.user)
        if is_present.count():
            proposal = is_present.latest('-id')
            proposal.description = offer
        else:
            proposal = HireComment(post=post,bidder=request.user,description=offer)
    proposal.save()
    return JsonResponse({'offer':offer})

@login_required
def update_proposal(request):
   postid = request.GET.get('postid') 
   offerType = request.GET.get('offertype') 
   template_name = 'snippets/proposals.html'
   description = ''
   proposal = ''
   post = Post.objects.get(id=postid)
   if offerType == 'buy':
        proposal = BuyProposals.objects.filter(post__id=postid,bidder=request.user)
   elif offerType == 'sell':
        proposal = SellProposals.objects.filter(post__id=postid,bidder=request.user)
   elif offerType == 'work':
        proposal = WorkProposal.objects.filter(post__id=postid,bidder=request.user)
   elif offerType == 'hire':
        proposal = HireComment.objects.filter(post__id=postid,bidder=request.user)
   if proposal:
       proposal = proposal.latest('-id')
       description = proposal.description
   return render(request,template_name,{'proposal':proposal,'proposaltype':offerType,'description':description,'post':post,'show_form':True})

@login_required
def create_promotional_post(request):
    form = CreatePostForm(request.POST,request.FILES)
    package_type = request.POST.get('package_type')
    images = request.FILES.getlist('thumbnail')
    
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.is_promotional = True
        obj.save()     
        # for image in images:
            # Gallery.objects.create(author=request.user, post=obj, images=image)
        promotionalDetail = PromotionalDetail(package_type=package_type,post=obj)
        promotionalDetail.save()
    else:
        print(form.errors)
    return JsonResponse({'status':200})      

@login_required
def proposal_feedback(request):
    template_name = 'snippets/proposals.html'
    proposalid = request.POST.get('proposalid')
    offerType = request.POST.get('proposaltype')
    feedback = request.POST.get('feedback')
    proposal = ''
    if offerType == 'buy':
        proposal = BuyProposals.objects.get(id=proposalid)
        new_proposal = BuyProposals(post=proposal.post,description=feedback,bidder=request.user,parent=proposal)
        new_proposal.save()
    elif offerType == 'sell':
        proposal = SellProposals.objects.get(id=proposalid)
        new_proposal = SellProposals(post=proposal.post,description=feedback,bidder=request.user,parent=proposal)
        new_proposal.save()
    elif offerType == 'work':
        proposal = WorkProposal.objects.get(id=proposalid)
        new_proposal = WorkProposal(post=proposal.post,description=feedback,bidder=request.user,parent=proposal)
        new_proposal.save()
    elif offerType == 'hire':
        proposal = HireComment.objects.get(id=proposalid)
        new_proposal = HireComment(post=proposal.post,description=feedback,bidder=request.user,parent=proposal)
        new_proposal.save()
    return render(request,template_name,{'proposal':proposal,'proposaltype':offerType})


@login_required
def create_buy_proposal(request):
    postid = request.POST.get('postid')
    description = request.POST.get('description')
    currency = request.POST.get('currency')
    amount = request.POST.get('amount')
    post = Post.objects.get(id=postid)
    proposal = BuyProposals(post=post,description=description,currency=currency,amount=amount,bidder=request.user)
    proposal.save()
    return JsonResponse({'success':200})


@login_required
def create_sell_proposal(request):
    postid = request.POST.get('postid')
    description = request.POST.get('description')
    currency = request.POST.get('currency')
    amount = request.POST.get('amount')
    post = Post.objects.get(id=postid)
    proposal = SellProposals(post=post,description=description,currency=currency,amount=amount,bidder=request.user)
    proposal.save()
    return JsonResponse({'success':200})

@login_required
def hire_proposals(request,pk):
    post = get_object_or_404(Post,id=pk)
    proposals = HireComment.objects.all().filter(post=post)
    return render(request,'posts/proposal_page.html',{'posts':[post],'proposals':proposals,'show_form':False,'proposaltype':'hire'})

@login_required
def buy_proposals(request,pk):
    post = get_object_or_404(Post,id=pk)
    proposals = BuyProposals.objects.all().filter(post=post)
    return render(request,'posts/proposal_page.html',{'posts':[post],'proposals':proposals,'show_form':False,'proposaltype':'buy'})

@login_required
def sell_proposals(request,pk):
    post = get_object_or_404(Post,id=pk)
    proposals = SellProposals.objects.all().filter(post=post)
    return render(request,'posts/proposal_page.html',{'posts':[post],'proposals':proposals,'show_form':False,'proposaltype':'sell'})


@login_required
def work_proposals(request,pk):
    post = get_object_or_404(Post,id=pk)
    proposals = WorkProposal.objects.all().filter(post=post)
    return render(request,'posts/proposal_page.html',{'posts':[post],'proposals':proposals,'show_form':False,'proposaltype':'work'})

@login_required
def load_hire_comment_reply(request):
    comment_id = request.GET.get('commentId')
    comments = HireComment.objects.allComment().filter(parent_id=comment_id)
    return render(request,'comments/hire_comment_reply.html',{'comments':comments})

@login_required
def post_hire_comment(request):
    postId = request.POST.get('postId')
    message = request.POST.get('message')
    post = Post.objects.get(id=postId)
    comment = HireComment(post=post,user=request.user,message=message)
    comment.save()
    return JsonResponse({'status':200})

@login_required
def createHireReply(request):
    commentId = request.POST.get('commentId')
    message = request.POST.get('message')
    comment = HireComment.objects.get(id=commentId)
    post = Post.objects.get(id=comment.post_id)
    child_comment = HireComment(post=post,user=request.user,parent=comment,message=message)
    child_comment.save()
    return JsonResponse({'status':200})

@login_required
def create_work_proposal(request):
    postid = request.POST.get('postid')
    description = request.POST.get('description')
    document = request.FILES.get('document')
    post = Post.objects.get(id=postid)
    proposal = WorkProposal(post=post,description=description,document=document,user=request.user)
    proposal.save()
    return JsonResponse({'success':200})


def load_users_interest(request):
    if not request.user.is_authenticated:
        return render(request,'snippets/users_interest.html',{'userInterest':[]})
    types = Type.objects.all()
    userInterest = UserInterest.objects.filter(user=request.user)[0]
    return render(request,'snippets/users_interest.html',{'userInterest':userInterest.interest,'interest_types':types})



@login_required
def user_posts(request,pk):
   user = get_object_or_404(Account,id=pk)
   posts = Post.objects.filter(author=user)
   for post in posts:
       postImage = PostImage.objects.filter(post=post)
       print(postImage)
   return render(request,'posts/user_related_posts.html',{'posts':posts,'user':user,'postImage':postImage}) 

@login_required
def ajax_user_posts(request):
   userid = request.GET.get('userid')
   user = Account.objects.get(id=userid)
   posts = Post.objects.filter(author=user)
   for post in posts:
       postImage = PostImage.objects.filter(post=post)

   print(posts)
   return render(request,'snippets/post_link.html',{'posts':posts,'user':user,'postImage':postImage}) 


@login_required
def join_group(request):
    group_name = request.GET.get('group_name')
    group,created = UserGroup.objects.get_or_create(name=group_name)
    group.users.add(request.user)
    group.save()
    return render(request,'snippets/group_banner.html',{'group':group})

@login_required
def left_group(request):
    group_name = request.GET.get('group_name')
    group,created = UserGroup.objects.get_or_create(name=group_name)
    group.users.remove(request.user)
    group.save()
    return render(request,'snippets/group_banner.html',{'group':group})



@login_required
def feedback(request):
    rating = 0
    numerator = 0
    denominator = 0
    postid = request.POST.get('postid')
    feedback = request.POST.get('feedback')
    rating = int(request.POST.get('rating'))
    post = Post.objects.get(id=postid)
    #check if user has already submitted a feedback for the same post.
    post_rating  = PostRating.objects.filter(user=request.user,post_id=post.id)
    if post_rating:
        post_rating = post_rating.latest('id')        
    else:
        post_rating = PostRating(post=post,user=request.user)
    post_rating.rating = rating
    post_rating.feedback = feedback
    post_rating.save()
    
    postratings = PostRating.objects.filter(post_id=postid)
    ratings = postratings.order_by('rating').values('rating').annotate(rate_total=Sum('rating'))
    for rate in ratings:
        numerator = numerator + (int(rate['rating']) * int(rate['rate_total']))
        denominator = denominator + int(rate['rate_total'])
    if denominator:
        rating = numerator/denominator
    rating_count = postratings.count()
    return JsonResponse({'rating':round(rating,1),'rating_count':rating_count})

@login_required
def feedback_fetch(request):
    postid = request.GET.get('postid')
    review = PostRating.objects.filter(user_id=request.user.id,post_id=postid).values('rating','feedback').latest('id')
    return JsonResponse({'rating':review['rating'],'feedback':review['feedback']})



@login_required
def message_load(request):
    chatid = request.GET.get('chatid')
    chat_messages = ChatMessage.objects.filter(chat_id=chatid)
    return render(request,'snippets/chat_message.html',{'messages':chat_messages})


def load_post(request):
    today = datetime.today()
    if not request.user.is_authenticated:
        posts = Post.objects.order_by(Case(When(is_promotional=True,date_published__date=today.date(),then=0),default=1),'-date_published')
        page = request.GET.get('page', 1)
        paginator = Paginator(posts,NO_OF_POSTS)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request,'snippets/post_link.html',{'posts':posts})
    userInterest,created = UserInterest.objects.get_or_create(user=request.user)
    interest_types = []
    postList = []
    if created:
        userInterest.interest = []
        userInterest.save()
    if userInterest.interest and len(userInterest.interest):
        for types in userInterest.interest:
            type_id = types['types'][0]
            singlePost = Post.objects.filter(type_id=type_id).order_by(Case(When(is_promotional=True,date_published__date=today.date(),then=0),default=1),'-date_published')
            if types['categories']:
                for category in types['categories']:
                    category_id = category['category'][0]
                    singleCategory = singlePost.filter(category_id=category_id)
                    if category['sub_categories']:
                        sub_categories_list = category['sub_categories']
                        subCategories = singleCategory.filter(sub_category__in=sub_categories_list)
                        postList.append(subCategories)
                    else:
                        postList.append(singleCategory)
            else:
                postList.append(singlePost)
    if userInterest.interest and len(userInterest.interest):
        posts = postList[0]
        for post in postList[1:]:
            posts = posts | post
    else:
        posts = Post.objects.all().order_by(Case(When(is_promotional=True,date_published__date=today.date(),then=0),default=1),'-date_published')
        for post in posts:
            postImage = PostImage.objects.filter(post=post)
        interest_types = Type.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(posts,NO_OF_POSTS)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,'snippets/post_link.html', {'posts': posts,'interest_types':interest_types,'postImage':postImage})

@login_required
def single_group(request,pk):
    group = get_object_or_404(UserGroup,id=pk)
    posts = GroupPost.objects.filter(group=group).order_by('-id')
    form = CreateGroupPost()
    return render(request,'posts/single_group.html',{'posts':posts,'group':group,'post_form':form})

@login_required
def single_group_with_category(request,category):
    name = 'G/' + category
    group,created = UserGroup.objects.get_or_create(name=name)
    posts = GroupPost.objects.filter(group=group).order_by('-id')
    form = CreateGroupPost()
    return render(request,'posts/single_group.html',{'posts':posts,'group':group,'post_form':form})

@login_required
def single_group_with_sub_category(request,sub_category):
    name = 'g/' + sub_category
    group,created = UserGroup.objects.get_or_create(name=name)
    posts = GroupPost.objects.filter(group=group).order_by('-id')
    form = CreateGroupPost()
    return render(request,'posts/single_group.html',{'posts':posts,'group':group,'post_form':form})



@login_required
def load_group_post(request):
    group_name = request.GET.get('group_name','')
    group,created = UserGroup.objects.get_or_create(name=group_name)
    posts = GroupPost.objects.filter(group=group).order_by('-id')
    form = CreateGroupPost()
    return render(request,'snippets/group_posts.html',{'posts':posts,'group':group,'post_form':form})


@login_required
def load_group_default_post(request):
    group = request.user.usergroup_set.all().order_by('-id')
    posts = []
    if group:
        group = group[0]
        posts = GroupPost.objects.filter(group=group)
    else:
        group = ''
    form = CreateGroupPost()
    return render(request,'snippets/group_posts.html',{'posts':posts,'group':group,'post_form':form})

@login_required
def load_user_groups(request):
    return render(request,'snippets/user_groups.html')


@login_required
def save_group_post(request):
    description = request.POST.get('description')
    thumbnail = request.FILES.get('thumbnail','')
    group_id = request.POST.get('group_id')
    group = UserGroup.objects.get(id=group_id)
    post = GroupPost(description=description,author=request.user,group=group)
    if thumbnail:
        post.thumbnail = thumbnail
    post.save()    
    return JsonResponse({'status':200})


@login_required
def load_categories(request):
    typeid = request.GET.get('typeid')
    print(typeid)
    categories = Category.objects.filter(type__in=[typeid])
    return render(request,'snippets/category_types.html',{'categories':categories,'typeid':typeid})


@login_required
def load_sub_categories(request):
    categoryId = request.GET.get('categoryid')
    categories = SubCategory.objects.filter(category__in=[categoryId])
    return render(request,'snippets/sub_category_types.html',{'sub_categories':categories})


@login_required
def post_reload_url(request):
    interestList = request.POST.get('interestList',[])
    interestList = json.loads(interestList)
    postList = []
    for types in interestList:
        type_id = types['types'][0]
        singlePost = Post.objects.filter(type_id=type_id)
        if types['categories']:
            for category in types['categories']:
                category_id = category['category'][0]
                singleCategory = singlePost.filter(category_id=category_id)
                if category['sub_categories']:
                    sub_categories_list = category['sub_categories']
                    subCategories = singleCategory.filter(sub_category__in=sub_categories_list)
                    postList.append(subCategories)
                else:
                    postList.append(singleCategory)
        else:
            postList.append(singlePost)
    userInterest,created = UserInterest.objects.get_or_create(user=request.user)
    userInterest.interest = interestList
    userInterest.save()
    if interestList:
        posts = postList[0]
        for post in postList[1:]:
            posts = posts | post
    else:
        posts = Post.objects.all()
        for post in posts:
            postImage = PostImage.objects.filter(post=post)
            print(postImage)
        return JsonResponse({'location_redirect':True})
    page = request.GET.get('page', 1)
    paginator = Paginator(posts,NO_OF_POSTS)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,'snippets/post_link.html',{'posts':posts,'postImage':postImage})

def PostDetailView(request,pk,year,month,day,post):
    post = get_object_or_404(Post,id=pk,date_published__year=year,date_published__month=month,date_published__day=day,slug=post)
    return render(request,'posts/post_detail.html',{'posts':[post]})




class GroupPostDetailView(LoginRequiredMixin,DetailView):
    model = GroupPost
    template_name = 'posts/group_post_detail.html'
    login_url = 'index'
    context_object_name = 'posts'

    def get_object(self):
        obj = super().get_object()
        return [obj]

@login_required
def deletePost(request):
    postId = request.GET.get('postid')
    post = Post.objects.get(id=postId)
    if request.user == post.author:
        post.delete()
    return JsonResponse({'status':200})

@login_required
def deleteGroupPost(request):
    postId = request.GET.get('postid')
    post = GroupPost.objects.get(id=postId)
    if request.user == post.author:
        post.delete()
    return JsonResponse({'status':200})


@login_required
def reportPost(request):
    postId = request.GET.get('postid')
    report_type = request.GET.get('report_type')
    post = Post.objects.get(id=postId)
    if request.user != post.author:
        report = ReportedPost(report_type=report_type,post=post,user=request.user)
        report.save()
    return JsonResponse({'status':200})


@login_required
def reportGroupPost(request):
    postId = request.GET.get('postid')
    report_type = request.GET.get('report_type')
    post = GroupPost.objects.get(id=postId)
    if request.user != post.author:
        report = ReportedGroupPost(report_type=report_type,post=post,user=request.user)
        report.save()
    return JsonResponse({'status':200})


@login_required
def deleteComment(request):
    commentId = request.GET.get('commentId')
    comment = Comment.objects.get(id=postId)
    if request.user == comment.user:
        comment.delete()
    return JsonResponse({'status':200})


class CommentDetailView(LoginRequiredMixin,DetailView):
    queryset = Comment.objects.allComment()
    template_name = 'posts/comment_detail.html'
    login_url = 'index'
    context_object_name = 'comments'

    def get_object(self):
        obj = super().get_object()
        return [obj]


@login_required
def postComment(request):
    postId = request.POST.get('postId')
    message = request.POST.get('message')
    post = GroupPost.objects.get(id=postId)
    comment = Comment(post=post,user=request.user,message=message)
    comment.save()
    return JsonResponse({'status':200,'message':comment.message,'duration':comment.created_at})


@login_required
def createComment(request):
    commentId = request.POST.get('commentId')
    message = request.POST.get('message')
    comment = Comment.objects.get(id=commentId)
    post = GroupPost.objects.get(id=comment.post_id)
    child_comment = Comment(post=post,user=request.user,parent=comment,message=message)
    child_comment.save()
    return JsonResponse({'status':200,'message':child_comment.message,'duration':child_comment.created_at})

 
@login_required
def load_ratings(request):
    post_id = request.GET.get('postId')
    ratings = PostRating.objects.all().filter(post_id=post_id)
    return render(request,'feedbacks/index.html',{'ratings':ratings})


@login_required
def author_feedback(request):
    ratingid = request.POST.get('ratingid')
    feedback = request.POST.get('feedback')
    rating = PostRating.objects.get(id=ratingid)
    rating_feedback = RatingFeedback(userrating=rating,feedback=feedback,user=request.user)
    rating_feedback.save()
    return JsonResponse({'status':'success'})


@login_required
def load_post_comments(request):
    post_id = request.GET.get('postId')
    comments = Comment.objects.all().filter(post_id=post_id)
    return render(request,'comments/post_comments.html',{'comments':comments})


@login_required
def load_comment_comments(request):
    comment_id = request.GET.get('commentId')
    comments = Comment.objects.allComment().filter(parent_id=comment_id)
    return render(request,'comments/comment_comments.html',{'comments':comments})


def search(request, *args, **kwargs):
    user = request.user
    form = CreateSearchForm()
    context = {'search_form': form,}
    return render(request, "posts/search.html", context)


def results(request, *args, **kwargs):
    user = request.user
    form = CreateResultForm()    
    context = {'result_form': form}
    
    return render(request, "posts/results.html", context)


def load_results(request):
    type_id=request.GET.get('type','')
    if type_id:
        type_id=[type_id]
    else: 
        type_id=Type.objects.all()

    category_id=request.GET.get('category', '')
    if category_id:
        category_id=[category_id]
    else: 
        category_id=Category.objects.all()
    
    sub_category_id=request.GET.get('sub_category', '')
    if sub_category_id:
        sub_category_id=[sub_category_id]
    else: 
        sub_category_id=SubCategory.objects.all()
    location=request.GET.get('location','')

    text=request.GET.get('q', '')


    results = Post.objects.filter(type_id__in=type_id, category_id__in=category_id,sub_category_id__in=sub_category_id, location__contains=location, detail__contains=text)
    for post in results:
        postImage = PostImage.objects.filter(post=post)
        print('postImage')
    if not request.user.is_authenticated:
        page = request.GET.get('page', 1)
        paginator = Paginator(results,NO_OF_POSTS)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        return render(request,'snippets/post_link.html',{'posts':results})
    
    return render(request, "snippets/results_data.html",{'results':results,'query':text})



def load_bio_results(request):
    """
       Return the lists of bio which matches the user search keyword
    """
    searched_keyword = request.GET.get('searched_keyword')
    results = Account.objects.filter(bio__icontains=searched_keyword)
    return render(request,"snippets/users_bio_list.html",{"results":results,"searched_keyword":searched_keyword})


def load_people_results(request):
    """
      Return the lists of userprofiles which matches the user search keyword
    """
    searched_keyword = request.GET.get('searched_keyword')
    results = Account.objects.filter(Q(Q(name__icontains=searched_keyword) | Q(username__icontains=searched_keyword)), Q(user_type=1) | Q(user_type=None))
    print(results)
    print(Account.objects.filter(Q(name__icontains='') | Q(username__icontains='')))
    return render(request,"snippets/users_profile_list.html",{"results":results,"searched_keyword":searched_keyword})

def load_merchant_results(request):
    """
      Return the lists of userprofiles which matches the user search keyword
    """
    searched_keyword = request.GET.get('searched_keyword')
    results = Account.objects.filter(Q(Q(name__icontains=searched_keyword) | Q(username__icontains=searched_keyword)),user_type=2)
    return render(request,"snippets/users_profile_list.html",{"results":results,"searched_keyword":searched_keyword})


def load_category(request):
    type_id = request.GET.get('type')
    category_id = request.GET.get('category')
    category = Category.objects.filter(type__in=[type_id]).order_by('name')
    sub_category = SubCategory.objects.filter(category__in=[category_id]).order_by('name')
    return render(request, 'posts/category_options.html', {
        'category': category,
        'sub_category': sub_category,
    })


def notifications(request):
    if not request.user.is_authenticated:
        return render(request,'posts/notifications.html',{'notifications':[]})
    notifications = Notification.objects.filter(receiver=request.user).exclude(sender=request.user)
    return render(request, 'posts/notifications.html',{'notifications':notifications})

@login_required
def notification_open(request):
    notificationId = request.GET.get('notificationId')
    notification =  Notification.objects.get(id=notificationId)
    notification.is_opened = True
    notification.save()
    return JsonResponse({'status':200})

@login_required
def msg_notification_read(request):
    chatid = request.GET.get('chatid')
    try:
        notification =  ChatNotification.objects.get(chat_id=chatid,msg_receiver=request.user)
    except:
        return JsonResponse({'status':200})
    notification.is_checked = True
    notification.msg_counter = 0
    notification.save()
    return JsonResponse({'status':200})

def messagesFetch(request,post_id):
    """
       If the message page is fetched post id
    """
    post = Post.objects.get(id=post_id)
    chat = Chat.objects.filter(user1=request.user,post_id=post_id)
    hideMessage = False
    if chat:
        chat = chat[0]
    else:
        chat = Chat(user1=request.user,user2=post.author,post=post)
        chat.save()
    if request.user == chat.user1:
        partener = chat.user2
    else: partener = chat.user1
    chats = Chat.objects.annotate(latest_date=Max('chatmessage__created_at')).filter(Q(user1 = request.user) | Q(user2 = request.user)).order_by('-latest_date')
    context = {'partener':partener,'chat':chat,'chats':chats,'hideMessage':hideMessage}
    return render(request, 'posts/messages.html', context)


def messagesFetchChat(request,chat_id):
    """
       If the message page is fetched using chat id
    """
    hideMessage = False
    chat = Chat.objects.get(id=chat_id)
    if (request.user != chat.user1) and (request.user != chat.user2):
        return HttpResponseForbidden()
    if request.user == chat.user1:
        partener = chat.user2
    else: partener = chat.user1
    chats = Chat.objects.annotate(latest_date=Max('chatmessage__created_at')).filter(Q(user1 = request.user) | Q(user2 = request.user)).order_by('-latest_date')
    context = {'partener':partener,'chat':chat,'chats':chats,'hideMessage':hideMessage}
    return render(request, 'posts/messages.html', context)


def messages(request):
    """
        If the message page is opened using navbar.
    """
    if not request.user.is_authenticated:
        return render(request,'posts/messages.html',{'chats':[],'chat':'','partener':'','hideMessage':True})
    hideMessage = True
    chats = Chat.objects.annotate(latest_date=Max('chatmessage__created_at')).filter(Q(user1 = request.user) | Q(user2 = request.user)).order_by('-latest_date')
    try:
        chat = ChatMessage.objects.filter(Q(chat__user1 = request.user) | Q(chat__user2 = request.user)).latest('id').chat
        if request.user == chat.user1:
            partener = chat.user2
        else: partener = chat.user1
    except:
        partener = ''
        chat = ''
    context = {'chats':chats,'chat':chat,'partener':partener,'hideMessage':hideMessage}
    return render(request,'posts/messages.html',context)


@login_required
def GroupPostLikeDislike(request):
    action = request.POST.get('action')
    postId = request.POST.get('postId')
    post = GroupPost.objects.get(id=postId)
    user = request.user

    postLike = GroupPostLike.objects.filter(post=post)
    postDisLike = GroupPostDislike.objects.filter(post=post)
    likes = postLike.count()
    dislikes = postDisLike.count()
    if action == 'like':
        if postLike:
            postLike[0].delete()
            likes = likes - 1
        else:
            postLike = GroupPostLike(post=post,user=user)
            postLike.save() 
            likes = likes + 1 
        if postDisLike:
           postDisLike[0].delete() 
           dislikes = dislikes - 1  
        
    elif action == 'dislike':
        if postDisLike:
            postDisLike[0].delete()
            dislikes = dislikes - 1
        else:
            postDisLike = GroupPostDislike(post=post,user=user)
            postDisLike.save()
            dislikes = dislikes + 1
        if postLike:
            postLike[0].delete()
            likes = likes - 1
    return JsonResponse({'status':200,'likes':likes,'dislikes':dislikes})


def CommentLikeDislike(request):
    action = request.POST.get('action')
    commentId = request.POST.get('commentId')
    comment = Comment.objects.get(id=commentId)
    user = request.user

    commentLike = CommentLike.objects.filter(comment=comment)
    commentDisLike = CommentDislike.objects.filter(comment=comment)
    likes = commentLike.count()
    dislikes = commentDisLike.count()
    if action == 'like':
        if commentLike:
            commentLike[0].delete()
            likes = likes - 1
        else:
            commentLike = CommentLike(comment=comment,user=user)
            commentLike.save() 
            likes = likes + 1 
        if commentDisLike:
           commentDisLike[0].delete() 
           dislikes = dislikes - 1  
        
    elif action == 'dislike':
        if commentDisLike:
            commentDisLike[0].delete()
            dislikes = dislikes - 1
        else:
            commentDisLike = CommentDislike(comment=comment,user=user)
            commentDisLike.save()
            dislikes = dislikes + 1
        if commentLike:
            commentLike[0].delete()
            likes = likes - 1
    return JsonResponse({'status':200,'likes':likes,'dislikes':dislikes})


@login_required()
def groups(request):
    groups = UserGroup.objects.filter()
    types = Type.objects.all()
    category = Category.objects.all()
    sub_category = SubCategory.objects.all()
    context = {'groups':groups,'types':types,'categories':category,'sub_categories':sub_category}
    return render(request, 'posts/groups.html', context)


@login_required()
def load_group_category(request):
    typeId = request.GET.get('typeid')
    categories = Category.objects.filter(type__in=[typeId])
    return render(request,'snippets/group_category_types.html',{'categories':categories})


@login_required()
def load_subgroup_category(request):
    typeId = request.GET.get('typeid')
    categories = Category.objects.filter(type__in=[typeId])
    return render(request,'snippets/subgroup_category_types.html',{'categories':categories})


@login_required()
def load_sub_category(request):
    categoryId = request.GET.get('categoryid')
    sub_categories = SubCategory.objects.filter(category__in=[categoryId])
    return render(request,'snippets/sub_category_group_types.html',{'sub_categories':sub_categories})


@login_required()
def orders(request):
    return render(request, 'posts/orders.html')


@login_required()
def group_ads(request):
    return render(request, 'posts/group_ads.html')


def terms(request):
    return render(request, 'menu/terms.html')


def privacy_policy(request):
    return render(request, 'menu/privacy_policy.html')


def about(request):
    return render(request, 'menu/about.html')