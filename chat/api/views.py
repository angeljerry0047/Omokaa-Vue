from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response # use DRF's response class
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse,JsonResponse
from django.db.models import Q,Sum,Count,Max,Case, When
from django.conf import settings
import boto3, uuid
from chat.api.serializers import * 


class ChatNotificationViewset(viewsets.ModelViewSet):
    serializer_class = ChatNotificationSerializer
    queryset = ChatNotification.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def read(self, request, pk):
        instance = self.get_object()
        data = {'is_checked': True, 'msg_counter': 0}
        serializer = ChatNotificationSerializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChatMessageViewset(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ChatViewset(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def items(self, request):
        data = Chat.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user))
        serializer = ChatSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

    def perform_create(self, serializer):
        user2 = Account.objects.get(id=self.request.POST['author'])
        serializer.save(user1=self.request.user, user2=user2)

    @action(detail=False, methods=['POST'])
    def upload_chat_doc(self, request):
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
