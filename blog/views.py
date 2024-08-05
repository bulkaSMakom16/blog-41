from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404

from .models import Post, Category, Comment, PostPhoto, SubscribedUsers, UserProfile
from .forms import MultiplePhotoForm, PostForm, CommentForm, PostPhotoForm, SubscriptionForm, UserProfileForm, CustomUserCreationForm
from django.db.models import Q

from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
# Create your views here.

def blog_logout(request):
    if request.method == 'POST':
        return redirect('index')
    return render(request, 'registration/logged_out.html')

def blog_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'blog/registration_user.html', {'form': form})

@login_required
def update_profile(request):
    user = request.user
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
        
    return render(request, 'blog/update_profile.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    
    try:
        user_profile = UserProfile.objects.get(user=user)
        avatar_url = user_profile.avatar.url if user_profile.avatar else 'http://placehold.it/64x64'
    except UserProfile.DoesNotExist:
        avatar_url = 'http://placehold.it/64x64'

    context = {
        'user': user,
        'avatar_url': avatar_url
    }
    return render(request, 'blog/profile.html', context)

def send_post_creation_email(post):
    subject = f'Новый пост создан: {post.title}'
    message = f'Здравствуйте!\n\nНовый пост был создан на вашем блоге.\n\nЗаголовок: {post.title}\nСодержание: {post.content}\n\nС уважением,\nВаша команда'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.DEFAULT_FROM_EMAIL]

    send_mail(subject, message, email_from, recipient_list)

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not SubscribedUsers.objects.filter(email=email).exists():
                form.save()
                messages.success(request, f"{email} has been successfully registered.")
                return redirect('index') 
            else:
                messages.error(request, 'This email is already subscribed.')
    else:
        form = SubscriptionForm()
    context = {'form': form}
    context.update(getCategories())
    return render(request, 'blog/subscribe.html', context)

def create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        photo_form = MultiplePhotoForm(request.POST, request.FILES)

        if post_form.is_valid():
            try:
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()

                # Save multiple photos
                images = request.FILES.getlist('images')
                for image in images:
                    PostPhoto.objects.create(post=post, image=image)

                # Send email notifications to subscribers
                send_mail(
                    'New Post Published',
                    f'A new post titled "{post.title}" has been published on our blog.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email for user in SubscribedUsers.objects.all()],
                    fail_silently=False,
                )

                messages.success(request, 'Post created successfully with photos and notification sent!')
                return redirect('index')
            except IntegrityError:
                messages.error(request, 'A post with this title already exists.')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        post_form = PostForm()
        photo_form = MultiplePhotoForm()

    context = {'post_form': post_form, 'photo_form': photo_form}
    context.update(getCategories())
    return render(request, 'blog/create.html', context)

def search(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(Q(content__icontains=query)| Q(title__icontains=query))
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def category(request, c=None):
    cObj = get_object_or_404(Category, name=c)
    posts = Post.objects.filter(category=cObj).order_by("-publishedDate")
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def getCategories():
    all = Category.objects.all()
    count = all.count()
    half = count // 2
    firstHalf = all[:half]
    secondHalf = all[half:]
    return{'cats1':firstHalf, 'cats2':secondHalf}


def index(request):
    posts = Post.objects.all().order_by('-publishedDate')
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def post(request, name=None):
    posts = Post.objects.filter(title=name)
    if not posts.exists():
        raise Http404("Post does not exist")
    post = posts.first()
    post = get_object_or_404(Post, title=name)
    comments = Comment.objects.filter(post=post).order_by('-id')

    # Get user profiles and their avatars
    comments_with_avatars = []
    for comment in comments:
        try:
            user_profile = UserProfile.objects.get(user=comment.author)
            avatar_url = user_profile.avatar.url if user_profile.avatar else 'http://placehold.it/64x64'
        except UserProfile.DoesNotExist:
            avatar_url = 'http://placehold.it/64x64'
        
        comments_with_avatars.append((comment, avatar_url))

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = request.POST.get('content')
            comment = Comment.objects.create(post=post, content=content, author=request.user)
            comment.save()
            return redirect('post', name=name)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments_with_avatars': comments_with_avatars,
        'comment_form': comment_form
    }
    context.update(getCategories())
    return render(request, 'blog/post.html', context)

def contact(request):
    return render(request, 'blog/contact.html')

def about(request):
    return render(request, 'blog/about.html')

def services(request):
    return render(request, 'blog/services.html')
