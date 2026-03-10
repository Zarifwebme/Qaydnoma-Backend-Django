from django.conf import settings
from django.http import HttpResponse, Http404
from django.db.models import Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

import hashlib

from .models import Category, Post, Comment, PostView
from .serializers import (
    CategorySerializer,
    PostSerializer,
    CommentSerializer,
    RegisterSerializer,
    ProfileSerializer,
    RelatedPostSerializer,
)
from .permissions import IsOwnerOrReadOnly


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().select_related("category").prefetch_related("comments__user").order_by("-id")
    serializer_class = PostSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        q = self.request.query_params.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(snippet__icontains=q) |
                Q(description__icontains=q)
            )

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


def post_image(request, pk):
    try:
        post = Post.objects.only("image", "image_mime").get(pk=pk)
    except Post.DoesNotExist:
        raise Http404("Post not found")

    if not post.image:
        raise Http404("Image not found")

    content_type = post.image_mime or "application/octet-stream"
    return HttpResponse(post.image, content_type=content_type)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all().select_related("category").prefetch_related("comments__user")
    serializer_class = PostSerializer
    lookup_field = "slug"

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        visitor_key = hashlib.sha256(f"{ip}|{ua}".encode()).hexdigest()[:64]
        today = timezone.localdate()

        _, created = PostView.objects.get_or_create(
            post=post,
            day=today,
            visitor_key=visitor_key,
        )

        if created:
            Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
            post.refresh_from_db(fields=["views"])

        post_serializer = self.get_serializer(post, context={"request": request})

        if post.category:
            related_posts = Post.objects.filter(
                category=post.category
            ).exclude(
                pk=post.pk
            ).order_by("-created_at")[:5]
        else:
            related_posts = Post.objects.none()

        related_serializer = RelatedPostSerializer(
            related_posts,
            many=True,
            context={"request": request}
        )

        return Response({
            "post": post_serializer.data,
            "related_posts": related_serializer.data
        })


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("-name")
    serializer_class = CategorySerializer


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.select_related("user", "post").order_by("-id")
        post_id = self.request.query_params.get("post")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token topilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass

        response = Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie(
            key="refresh_token",
            path="/",
            samesite="Lax",
        )
        return response


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            refresh_token = response.data.pop("refresh", None)

            if refresh_token:
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    max_age=60 * 60 * 24 * 7,
                    path="/",
                )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token topilmadi"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        request.data["refresh"] = refresh_token
        return super().post(request, *args, **kwargs)