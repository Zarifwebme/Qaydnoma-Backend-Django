import base64
from rest_framework import serializers
from .models import Post, Comment, Category
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["user"] = request.user
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    image = serializers.CharField(write_only=True, required=False)
    image_url = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "slug",
            "title",
            "snippet",
            "description",
            "image",
            "image_url",
            "created_at",
            "category",
            "category_name",
            "category_slug",
            "comments",
            "views",
        ]

    def create(self, validated_data):
        image_data = validated_data.pop("image", None)

        post = Post(**validated_data)

        if image_data:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]

            post.image = base64.b64decode(imgstr)
            post.image_mime = f"image/{ext}"

        post.save()
        return post

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        path = f"/api/posts/{obj.id}/image/"

        if request:
            return request.build_absolute_uri(path) 
        return path

class RelatedPostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "slug",
            "title",
            "snippet",
            "created_at",
            "category_name",
            "category_slug",
            "image_url",
            "views",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        path = f"/api/posts/{obj.id}/image/"

        if request:
            return request.build_absolute_uri(path)
        return path

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.validated_data["refresh"])
            token.blacklist()
        except Exception:
            self.fail("bad_token")