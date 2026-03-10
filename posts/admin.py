from django.contrib import admin
from django import forms
from martor.widgets import AdminMartorWidget
from .models import Post, Comment, Category


class PostAdminForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)
    description = forms.CharField(widget=AdminMartorWidget(), required=False)

    class Meta:
        model = Post
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)

        image = self.cleaned_data.get("image_file")
        if image:
            instance.image = image.read()
            instance.image_mime = image.content_type

        if commit:
            instance.save()

        return instance


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("id", "title", "category", "created_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Comment)