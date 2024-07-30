from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=30, verbose_name='title', unique=True)  # Add unique=True
    content = models.TextField(verbose_name='content')
    publishedDate = models.DateTimeField(auto_now_add=True, verbose_name='published date')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='category')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Author', default=1)
    img = models.URLField(default="http://placehold.it/900x300", max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    commentDate = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=240)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return f"Commented by {self.author}, on {self.post.title} in {self.commentDate}"
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

class SubscribedUsers(models.Model):
    name = models.CharField(max_length=180)
    email = models.EmailField(unique=True, max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class PostPhoto(models.Model):
    post = models.ForeignKey(Post, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_photos/')

    def __str__(self):
        return f"Photo for {self.post.title}"
    
    class Meta:
        verbose_name = 'PostPhoto'
        verbose_name_plural = 'PostPhotos'