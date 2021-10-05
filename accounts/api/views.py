from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.core.serializers import serialize
from rest_framework import viewsets, permissions, views, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response # use DRF's response class
from rest_framework.decorators import permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from accounts.api.serializers import * 
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
UserModel = get_user_model()

class HelpMessageViewset(viewsets.ModelViewSet):
    serializer_class = HelpMessageSerializer
    queryset = HelpMessage.objects.all()
    permission_classes = [IsAuthenticated]


class FeedbackViewset(viewsets.ModelViewSet):
    serializer_class = FeedbackSerialiazer
    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountViewset(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def get_queryset(self):
        return Account.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['GET'])
    def user(self, request, *args, **kwargs):
        res = AccountSerializer(request.user).data
        token = Token.objects.get(user=request.user).key
        return Response({'token': token, 'user': res})

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        token, created = Token.objects.get_or_create(user_id=response.data["id"])
        response.data["token"] = str(token)

        user = Account.objects.get(id=response.data["id"])
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
        to_email = response.data['email']
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.content_subtype = "html"
        email.send()

        return JsonResponse({'status':200})


    @action(detail=True, methods=['POST'])
    def upgrade(self, request, pk):
        instance = self.get_object()
        step = request.POST['step']
        data = {}
        if (int(step) == 1):
            data = {
                'user_type': request.POST['user_type']
            }
        elif (int(step) == 2):
            data = {
                'date_birth': request.POST['birthday'],
            }
        elif (int(step) == 3):
            data = {
                'gender': request.POST['gender'],
            }
        elif (int(step) == 4):
            data = {
                'profile_pic': request.FILES.get('profile_pic'),
            }
        elif (int(step) == 5):
            data = {
                'identity': request.FILES.get('identity_doc')
            }
        serializer = AccountSerializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def upgrade_bio(self, request, pk):
        instance = self.get_object()
        data = {
            'bio': request.POST['bio']
        }
        serializer = AccountSerializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        logout(request)
        return JsonResponse({'status':200})


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = AccountSerializer(token.user).data
        return Response({'token': token.key, 'user': user})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://www.omokaa.com/auth/sign-in/')
    else:
        return HttpResponse('Activation link is invalid!')
