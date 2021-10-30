from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
User = get_user_model()

# Create your models here.
class PublishManager(models.Manager):
    def get_queryset(self):
        return super(PublishManager, self).get_queryset().filter(status='published')

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'), 
        ('published', 'Published'),
    )
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    image = models.ImageField(upload_to='images/', blank=True)
    body = RichTextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    objects = models.Manager()
    published = PublishManager()
    tags = TaggableManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
