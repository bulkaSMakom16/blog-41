from django import forms
from .models import Post, Comment, SubscribedUsers, User, UserProfile, PostPhoto
from django.contrib.auth.forms import UserCreationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('publishedDate',)
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Post.objects.filter(title=title).exists():
            raise forms.ValidationError("A post with this title already exists.")
        return title

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = SubscribedUsers
        fields = ['name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user_profile = UserProfile.objects.create(user=user, avatar=self.cleaned_data.get('avatar'))
            user_profile.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'img']

class PostPhotoForm(forms.ModelForm):
    class Meta:
        model = PostPhoto
        fields = ['image']

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultiplePhotoForm(forms.Form):
    images = forms.FileField(widget=MultiFileInput(attrs={'multiple': True}), required=False)