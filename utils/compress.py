from io import BytesIO
from PIL import Image
from django.core.files import File


def compressImage(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO() 

    img_extension = image.name.split('.')[1]
    img_type = "image/jpeg"
    img_format = "JPEG"
    if(img_extension == 'png'):
        img_type = "image/png"
        img_format = "PNG"
    # save image to BytesIO object
    im.save(im_io,img_format, quality=20) 
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image