from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


def upload_location(instance, filename, **kwargs):
    file_path = 'accounts/{id}/-{filename}'.format(
        id=str(instance.id), filename=filename)
    return file_path


class MyAccountManager(BaseUserManager):
    def create_user(self, name, username, email, phone, password, country_code):
        if not name:
            raise ValueError('Name is required')
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        if not phone:
            raise ValueError('Phone number is required')
        if not password:
            raise ValueError('Password is required')

        user = self.model(
            name=name,
            username=username,
            email=self.normalize_email(email),
            phone=phone,
            country_code=country_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, username, email, phone, password, country_code):
        user = self.create_user(
            name=name,
            username=username,
            email=self.normalize_email(email),
            phone=phone,
            password=password,
            country_code=country_code
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
        

class Account(AbstractBaseUser):
    name = models.CharField(verbose_name='name', max_length=50)
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(null=True,blank=True)
    email = models.CharField(verbose_name='email', max_length=255, unique=True)
    phone = models.CharField(verbose_name='phone', max_length=20, unique=True)
    profile_pic = models.ImageField(upload_to=upload_location,null=True, blank=True)
    password = models.CharField(verbose_name='password', max_length=255)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    user_type = models.IntegerField(blank=True, null=True)
    date_birth = models.DateTimeField(verbose_name='Date of birth', blank=True, null=True)
    identity = models.FileField(upload_to=upload_location,null=True, blank=True)
    slug = models.SlugField(max_length=200, default=10)
    explore_locations = models.CharField(verbose_name='explore_locations', max_length=5, blank=True, null=True)
    country_code = models.CharField(verbose_name='country_code', max_length=5 , null=True)
    gender = models.IntegerField(blank=True, null=True)
    is_email_public = models.BooleanField(default=False)
    is_phone_public = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username', 'phone', 'country_code', 'is_email_public', 'is_phone_public']

    objects = MyAccountManager()

    def __str__(self):
        return self.name + ', ' + '@' + self.username

    def save(self, *args, **kwargs):
        slug = self.name+self.username
        self.slug = slugify(slug)
        super(Account,self).save(*args,**kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return reverse('account_detail',
                       args=[self.pk, self.name, self.username, self.slug])

"""class Profile(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True)"""





class Feedback(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.name) + ' : ' + str(self.message[:300])

    def get_absolute_url(self):
        return reverse('feedback')



class HelpMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + " : " + self.message

    def get_absolute_url(self):
        return reverse('help')