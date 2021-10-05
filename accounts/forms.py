from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from accounts.models import Account,Feedback,HelpMessage



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control detail textarea', 'rows':5, 'placeholder':'Message here'})
        }

class HelpForm(forms.ModelForm):
    name = forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Your Name','required':True}))
    email = forms.EmailField(max_length=60,label='Email',widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Your Email','required':True}))
    class Meta:
        model = HelpMessage
        fields = ['name','email','message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control detail textarea', 'rows':5, 'placeholder':'Message here'})
        }

class RegistrationForm(UserCreationForm):
    name = forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Your Name','required':True,'style':'margin-top:3px;margin-bottom:0px;'}))
    username = forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Your Username','required':True,'style':'margin-top:3px;margin-bottom:0px;'}))
    email = forms.EmailField(max_length=60,label='Email',widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Your Email','required':True,'style':'margin-top:3px;margin-bottom:0px;','id':'register_email'}))
    phone = forms.CharField(label='Phone Number',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Your PhoneNumber','required':True,'style':'margin-top:3px;margin-bottom:0px;'}))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.pop("autofocus", None)

    class Meta:
        model = Account
        fields = ['name', 'username', 'email', 'phone', 'password1', 'password2']


class AccountAuthenticationForm(forms.ModelForm):
    email = forms.EmailField(label='Email',max_length=60,widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter Your Email or Username','required':'true'}))
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Your Password','required':'true'}))

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            self.user_cache = authenticate(email=email,password=password)
            if self.user_cache is None:
                try:
                    user_temp = Account.objects.get(email=email)
                except:
                    user_temp = None
                if user_temp is not None:
                    if not user_temp.is_active:
                        pass
                    else:
                        if not authenticate(email=email, password=password):
                            raise forms.ValidationError("Invalid login credentials")    
                else:
                    if not authenticate(email=email, password=password):
                        raise forms.ValidationError("Invalid login credentials")


class ProfilePicForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['profile_pic']