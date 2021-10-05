from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout,get_user_model
from operator import attrgetter
from accounts.forms import RegistrationForm, AccountAuthenticationForm
from posts.models import Post, Gallery
from accounts.forms import FeedbackForm,HelpForm
from accounts.models import Account,Feedback,HelpMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
UserModel = get_user_model()




class FeedbackCreateView(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    form_class = FeedbackForm
    template_name = 'accounts/feedback.html'
    success_message = "Feedback is submitted"
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class HelpCreateView(SuccessMessageMixin,CreateView):
    form_class = HelpForm
    template_name = 'accounts/help.html'
    success_message = "Your message is submitted, we will get back to you soon."

def user_add_bio(request):
    bio = request.POST.get('bio')
    user = Account.objects.get(id=request.user.id)
    user.bio = bio
    user.save()
    return JsonResponse({})


def account_detail(request,pk,name,username,slug):
    account = get_object_or_404(Account,pk=pk,name=name,username=username,slug=slug)
    return render(request,'accounts/account_detail.html',{'account':account})

def registration_view(request):
    context = {}
    context['form_type'] = 'login'
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('accounts/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.content_subtype = "html"
                email.send()
                context['message'] = 'An account verification link has been sent to your email. Please Visit your email and click on the verification link.'
                form = RegistrationForm()
                context['registration_form'] = form
            else:
                context['registration_form'] = form
                context['form_type'] = 'registeration'
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    context['login_form'] = AccountAuthenticationForm()
    return render(request, 'accounts/index.html', context)

def login_view(request):
    context = {}
    form = AccountAuthenticationForm()
    context['login_form'] = form
    context['registration_form'] = RegistrationForm()
    context['form_type'] = 'login'
    if request.POST:
            form = AccountAuthenticationForm(request.POST)
            if form.is_valid():
                email = request.POST['email']
                password = request.POST['password']
                try:
                    temporary_user = Account.objects.get(email=email)
                    if not temporary_user.is_active:
                        context['alert_message'] = 'You account has been not verified yet. Please Visit your email and click on the verification link.'
                        return render(request,'accounts/index.html',context)
                except:
                    pass
                user = authenticate(email=email, password=password)

                if user:
                    login(request, user)
                    return redirect('home')
            else:
                context['alert_message'] = 'Invalid login credentials'
                context['login_form'] = form
    return render(request,'accounts/index.html',context)

def logout_view(request):
    logout(request)
    return redirect('registration_view')


def my_account(request):
    context = {}
    posts = sorted(Post.objects.filter(author=request.user), key=attrgetter('date_updated'), reverse=True)
    context['posts'] = posts

    return render(request, 'accounts/myaccount.html', context)


def details(request):
    context = {}

    return render(request, 'accounts/details.html', context)


def account_extend(request):
    do_reload = False
    type_id = request.POST.get('user_type')
    if type_id:
        Account.objects.update_or_create(email=request.user.email, defaults={'user_type': type_id})
    date_birth = request.POST.get('date_birth')
    
    if date_birth:
        Account.objects.update_or_create(email=request.user.email,defaults={'date_birth': date_birth})
    
    
    profile_pic = request.FILES.get('profile_pic')
    cropped_profile_pic = request.FILES.get('cropped_profile_pic')
    if cropped_profile_pic:
        profile_pic=cropped_profile_pic
    if profile_pic:
        Account.objects.update_or_create(email=request.user.email,defaults={'profile_pic':profile_pic})
        do_reload = True

    identity = request.FILES.get('identity')
    if identity:
        Account.objects.update_or_create(email=request.user.email,defaults={'identity':identity})
        do_reload = True
    return JsonResponse({'success':True,'do_reload':do_reload})


def account_step(request):
    user=Account.objects.get(id=request.user.id)
    data = {'user_type':user.user_type}
    step=0
    if not user.user_type:
        data['step'] = step
        return JsonResponse(data,safe=False)
    else:
        step=1
    if not user.date_birth:
        data['step'] = step
        return JsonResponse(data,safe=False)
    else:
        step=2
    if not user.profile_pic:
        data['step'] = step
        return JsonResponse(data,safe=False)
    else:
        step=3
    if user.identity:
        step=4
    data['step'] = step
    return JsonResponse(data,safe=False)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request,user)
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')

def account_verify_message(request):
    return render(request,'accounts/verify_message.html')

def account_notverified_message(request):
    return render(request,'accounts/not_verified_message.html')






def validate_name_username(request):
    username = request.GET.get('username')
    isUserNameExist = False

    if(Account.objects.filter(username=username).count()):
        isUserNameExist = True

    return JsonResponse({'status':200,'username':isUserNameExist})

def validate_email_phone(request):
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    isEmailExist,isPhoneExist = False,False

    if(Account.objects.filter(email=email).count()):
        isEmailExist = True

    if(Account.objects.filter(phone=phone).count()):
        isPhoneExist = True

    return JsonResponse({'status':200, 'email':isEmailExist, 'phone':isPhoneExist})