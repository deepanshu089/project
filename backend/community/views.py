"""
API Views for the Community Feed application.

Implements:
- Optimized post and comment queries (avoiding N+1)
- Race-condition-safe like/unlike operations
- Dynamic 24-hour leaderboard calculation
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from django.db.models import Count, Q, F, Prefetch
from django.utils import timezone
from datetime import timedelta

from .models import Post, Comment, Like
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    LeaderboardSerializer,
    UserSerializer,
    UserRegistrationSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for posts with optimized queries.
    
    List view: Annotates like_count and comment_count to avoid N+1 queries
    Detail view: Prefetches comment tree efficiently
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Optimize queries based on action.
        
        List: Annotate counts, select author
        Retrieve: Prefetch entire comment tree
        """
        queryset = Post.objects.select_related('author')
        
        if self.action == 'list':
            # For list view: just counts, no comments
            queryset = queryset.annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True)
            )
        elif self.action == 'retrieve':
            # For detail view: prefetch comment tree
            # This is the key to avoiding N+1 queries!
            queryset = queryset.prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(parent__isnull=True)
                        .select_related('author')
                        .prefetch_related(
                            Prefetch(
                                'replies',
                                queryset=Comment.objects.select_related('author')
                                    .prefetch_related(
                                        Prefetch(
                                            'replies',
                                            queryset=Comment.objects.select_related('author')
                                        )
                                    )
                                    .annotate(like_count=Count('likes'))
                            )
                        )
                        .annotate(like_count=Count('likes'))
                        .order_by('-created_at')
                )
            ).annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a post.
        
        Uses atomic transaction and get_or_create to prevent race conditions.
        Database constraints provide additional protection against double-likes.
        """
        post = self.get_object()
        
        try:
            with transaction.atomic():
                # Atomic operation: prevents race conditions
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    post=post
                )
                
                if not created:
                    # Like already exists, so unlike
                    like.delete()
                    return Response({
                        'liked': False,
                        'like_count': post.likes.count()
                    })
                
                return Response({
                    'liked': True,
                    'like_count': post.likes.count()
                })
        
        except IntegrityError:
            # Database constraint prevented double-like
            # This should never happen with get_or_create, but safety first
            return Response(
                {'error': 'Like operation failed due to constraint violation'},
                status=status.HTTP_409_CONFLICT
            )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for comments with optimized queries.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Optimize comment queries."""
        return Comment.objects.select_related('author', 'post').annotate(
            like_count=Count('likes')
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Use create serializer for write operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return CreateCommentSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a comment.
        
        Uses atomic transaction and get_or_create to prevent race conditions.
        """
        comment = self.get_object()
        
        try:
            with transaction.atomic():
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    comment=comment
                )
                
                if not created:
                    # Unlike
                    like.delete()
                    return Response({
                        'liked': False,
                        'like_count': comment.likes.count()
                    })
                
                return Response({
                    'liked': True,
                    'like_count': comment.likes.count()
                })
        
        except IntegrityError:
            return Response(
                {'error': 'Like operation failed due to constraint violation'},
                status=status.HTTP_409_CONFLICT
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    """
    Get top 5 users by karma earned in the last 24 hours.
    
    Karma calculation:
    - Post like = 5 karma (to post author)
    - Comment like = 1 karma (to comment author)
    
    This does NOT use a stored karma field. It calculates dynamically
    from the Like activity history.
    """
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    # This approach uses conditional aggregation
    leaderboard = User.objects.annotate(
        # Count post likes in last 24h
        post_likes_24h=Count(
            'posts__likes',
            filter=Q(posts__likes__created_at__gte=twenty_four_hours_ago),
            distinct=True
        ),
        # Count comment likes in last 24h
        comment_likes_24h=Count(
            'comments__likes',
            filter=Q(comments__likes__created_at__gte=twenty_four_hours_ago),
            distinct=True
        ),
    ).annotate(
        # Calculate karma
        post_karma_24h=F('post_likes_24h') * 5,
        comment_karma_24h=F('comment_likes_24h') * 1,
        karma_24h=F('post_karma_24h') + F('comment_karma_24h')
    ).filter(
        karma_24h__gt=0
    ).order_by('-karma_24h')[:5]
    
    serializer = LeaderboardSerializer(leaderboard, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Auto-login after registration
        login(request, user)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login a user."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response(UserSerializer(user).data)
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout the current user."""
    logout(request)
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get the current user's profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
