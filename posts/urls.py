from django.urls import path
from .views import (
    CategoryListCreateView,
    PostDetailView,
    PostListCreateView,
    CommentListCreateView,
    RegisterView,
    ProfileView,
    LogoutView,
    CommentDeleteView,
    post_image,
)

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="posts"),
    path("posts/<int:pk>/image/", post_image, name="post-image"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),

    path("categories/", CategoryListCreateView.as_view(), name="categories"),

    path("comments/", CommentListCreateView.as_view(), name="comments-create"),
    path("comments/<int:pk>/", CommentDeleteView.as_view(), name="comment-delete"),

    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]