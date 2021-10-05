from posts.models import DefaultImage, UserGroup


def default_images(request):
	try:
		defaultImage = DefaultImage.objects.latest('-id')
	except:
		defaultImage = {'profile_img':{'url':''},'bg_image':{'url':''}}
	return {'defaultImage':defaultImage}

def user_chosen_group(request):
	if request.user.is_authenticated:
		user_group = UserGroup.objects.filter(users__in=[request.user])
	else:
		user_group = []
	return {'user_group':user_group}
