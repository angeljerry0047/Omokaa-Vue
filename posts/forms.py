from django import forms
from posts.models import Post, GroupPost, Category, SubCategory,PostImage


# class PostImageForm(forms.ModelForm):
#     class Meta:
#         model = PostImage
#         fields = ['image']


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = PostImage
        fields = ('image', )


class CreateGroupPost(forms.ModelForm):

    class Meta:
        model = GroupPost
        fields = ['description','thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control detail textarea', 'rows':1, 'placeholder':'Post something here','maxlength':'800'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'multiple': True})
        }


class CreatePostForm(forms.ModelForm):
    thumbnail = forms.ImageField(
            widget=forms.ClearableFileInput(
                attrs={
                    'multiple': True}),
            required=False)

    class Meta:
        model = Post
        fields = ['type', 'category', 'sub_category', 'detail', 'thumbnail', 'location']
        widgets = {
            'detail': forms.Textarea(attrs={'class': 'form-control textarea', 'rows':1,'required':True,'placeholder':'Share Your Hustle'}),
            'location': forms.TextInput(attrs={'class': 'form-control',
                                               'autocomplete': 'on',
                                                'required':True
                                               }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'multiple': True})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({'class': 'form-control','type':'hidden'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].empty_label = 'Type'
        self.fields['category'].empty_label = 'Category'
        self.fields['sub_category'].empty_label = 'Sub-Category'
        self.fields['category'].queryset = Category.objects.none()
        self.fields['sub_category'].queryset = SubCategory.objects.none()
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type__in=[type_id]).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.country.city_set.order_by('name')
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category__in=[category_id]).order_by('name')
            except (ValueError,TypeError):
                pass

                
class CreateSearchForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['type', 'category', 'sub_category']
        widgets = {
            # 'type': forms.Select(attrs={'class': 'form-control'}),
            # 'category': forms.TextInput(attrs={'class': 'form-control'}),
            # 'sub_category': forms.TextInput(attrs={'class': 'form-control'}),
            # 'type': forms.Select(attrs={'class': 'form-control'}),
            # 'category': forms.Select(attrs={'class': 'form-control'}),
            # 'sub_category': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['category'].queryset = Category.objects.none()
        # self.fields['sub_category'].queryset = SubCategory.objects.none()
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].empty_label = 'Type'
        self.fields['category'].empty_label = 'Category'
        self.fields['sub_category'].empty_label = 'Sub-Category(Optional)'
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type__in=[type_id]).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.country.city_set.order_by('name')


class CreateResultForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['type', 'category', 'sub_category', 'location']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control',
                                               'autocomplete': 'on',
                                               'placeholder':'location'
                                               }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].empty_label = 'Type'
        self.fields['category'].empty_label = 'Category'
        self.fields['sub_category'].empty_label = 'Sub-Category(Optional)'
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type__in=[type_id]).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.country.city_set.order_by('name')


class CreateUnAuthForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['type', 'category', 'sub_category', 'location']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control',
                                               'autocomplete': 'on',
                                               'placeholder':'location'
                                               }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({'class': 'form-control','id':'unauth_type'})
        self.fields['category'].widget.attrs.update({'class': 'form-control','id':'unauth_category'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control','id':'unauth_sub_category'})
        self.fields['location'].widget.attrs.update({'id':'unauth_location'})
        self.fields['type'].empty_label = 'Type'
        self.fields['category'].empty_label = 'Category'
        self.fields['sub_category'].empty_label = 'Sub-Category(Optional)'
        if 'type' in self.data:
            try:
                type_id = int(self.data.get('type'))
                self.fields['category'].queryset = Category.objects.filter(type__in=[type_id]).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['category'].queryset = self.instance.country.city_set.order_by('name')
