"""
Database models for the Community Feed application.

This module implements:
- Post: User-generated content posts
- Comment: Threaded comments with self-referential foreign key
- Like: Likes on posts and comments with race condition protection
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    """
    Represents a user post in the community feed.
    
    Karma: Each like on a post gives the author 5 karma points.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(
        help_text="The text content of the post"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:50]}..."


class Comment(models.Model):
    """
    Represents a comment on a post or a reply to another comment.
    
    Uses self-referential foreign key for nested threading:
    - parent=None: Top-level comment on a post
    - parent=<comment>: Reply to another comment
    
    Karma: Each like on a comment gives the author 1 karma point.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment if this is a reply, null if top-level"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(
        help_text="The text content of the comment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Critical for efficient tree queries
            models.Index(fields=['post', 'parent']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        reply_to = f" (reply to {self.parent.id})" if self.parent else ""
        return f"Comment by {self.author.username} on Post {self.post.id}{reply_to}"


class Like(models.Model):
    """
    Represents a like on either a post or a comment.
    
    Race Condition Protection:
    - Database-level unique constraints prevent double-likes
    - Separate constraints for post likes and comment likes
    - created_at indexed for efficient 24h leaderboard queries
    
    Exactly one of post or comment must be set (enforced in clean()).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            # Prevent double-likes on posts
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_post_like'
            ),
            # Prevent double-likes on comments
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_comment_like'
            ),
        ]
        indexes = [
            # Critical for 24h leaderboard calculation
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        if self.post:
            return f"{self.user.username} likes Post {self.post.id}"
        elif self.comment:
            return f"{self.user.username} likes Comment {self.comment.id}"
        return f"Like by {self.user.username}"
    
    def clean(self):
        """Validate that exactly one of post or comment is set."""
        from django.core.exceptions import ValidationError
        
        if self.post and self.comment:
            raise ValidationError("A like cannot be on both a post and a comment.")
        if not self.post and not self.comment:
            raise ValidationError("A like must be on either a post or a comment.")
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
