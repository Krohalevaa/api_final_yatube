from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, GroupViewSet, FollowViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'^posts/(?P<post_id>\d+)/comments',
                CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
