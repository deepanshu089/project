"""
DRF Serializers for the Community Feed application.

Implements efficient serialization with:
- Recursive comment threading
- Optimized query annotations
- User profile embedding
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profiles."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CommentSerializer(serializers.ModelSerializer):
    """
    Recursive serializer for threaded comments.
    
    Handles nested replies efficiently when used with proper
    prefetch_related queries in the view.
    """
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True, required=False)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'parent',
            'author',
            'content',
            'created_at',
            'updated_at',
            'like_count',
            'is_liked',
            'replies'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_replies(self, obj):
        """
        Recursively serialize nested replies.
        
        Uses prefetched data when available to avoid N+1 queries.
        """
        # Check if replies were prefetched
        if hasattr(obj, '_prefetched_objects_cache') and 'replies' in obj._prefetched_objects_cache:
            replies = obj._prefetched_objects_cache['replies']
        else:
            # Fallback: fetch with optimization
            from django.db.models import Count
            replies = obj.replies.select_related('author').annotate(
                like_count=Count('likes')
            ).all()
        
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_is_liked(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                comment=obj
            ).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for posts with embedded author and like count.
    
    For list views, comments are excluded for performance.
    For detail views, top-level comments are included with nested replies.
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True, required=False)
    is_liked = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'content',
            'created_at',
            'updated_at',
            'like_count',
            'is_liked',
            'comment_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
    
    def get_is_liked(self, obj):
        """Check if the current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                post=obj
            ).exists()
        return False


class PostDetailSerializer(PostSerializer):
    """
    Extended post serializer with comment tree.
    
    Only used for detail views to avoid loading comments in list views.
    """
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        """
        Get top-level comments with nested replies.
        
        Expects comments to be prefetched in the view for efficiency.
        """
        # Get only top-level comments (parent=None)
        top_level_comments = obj.comments.filter(parent__isnull=True)
        
        # Annotate with like count if not already done
        if not hasattr(top_level_comments.first(), 'like_count') if top_level_comments.exists() else False:
            from django.db.models import Count
            top_level_comments = top_level_comments.annotate(
                like_count=Count('likes')
            )
        
        return CommentSerializer(
            top_level_comments,
            many=True,
            context=self.context
        ).data


class CreateCommentSerializer(serializers.ModelSerializer):
    """Serializer for creating comments and replies."""
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'content']
        read_only_fields = ['id']
    
    def validate(self, data):
        """
        Validate that if parent is set, it belongs to the same post.
        """
        parent = data.get('parent')
        post = data.get('post')
        
        if parent and parent.post != post:
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        
        return data
    
    def create(self, validated_data):
        """Create comment with the current user as author."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class LeaderboardSerializer(serializers.Serializer):
    """
    Serializer for leaderboard entries.
    
    Not a ModelSerializer because it uses annotated queryset data.
    """
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    karma_24h = serializers.IntegerField()
    post_karma_24h = serializers.IntegerField(required=False)
    comment_karma_24h = serializers.IntegerField(required=False)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
