from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from martor.models import MartorField


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="posts")

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    snippet = models.CharField(max_length=300)
    description = MartorField()

    image = models.BinaryField(blank=True, null=True)
    image_mime = models.CharField(max_length=50, blank=True, default="")

    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
   
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

class PostView(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_views")
    day = models.DateField(auto_now_add=True)
    visitor_key = models.CharField(max_length=64)  # ip+ua hash
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "day", "visitor_key")