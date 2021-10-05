from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from posts.models import Post



@login_required
def post_chat_room(request,post_id):
 	try:
 		# retrieve course with given id joined by the current user
 		post = Post.objects.get(id=post_id)
 	except:
 		# user is not a student of the course or course does not exist
 		return HttpResponseForbidden()
 	return render(request, 'chat/room.html', {'post': post})