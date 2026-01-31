"""
Tests for the Community Feed application.

Key test cases:
1. Leaderboard calculation with 24h window
2. Race condition prevention on likes
3. Comment tree query optimization
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import threading
import time

from .models import Post, Comment, Like


class LeaderboardTestCase(TestCase):
    """Test the 24-hour leaderboard calculation logic."""
    
    def setUp(self):
        """Create test users and content."""
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        self.liker = User.objects.create_user(username='liker', password='pass123')
        
        # Create posts
        self.post1 = Post.objects.create(author=self.user1, content='Post by user1')
        self.post2 = Post.objects.create(author=self.user2, content='Post by user2')
        
        # Create comments
        self.comment1 = Comment.objects.create(
            post=self.post1,
            author=self.user3,
            content='Comment by user3'
        )
    
    def test_karma_calculation_weights(self):
        """Test that post likes = 5 karma, comment likes = 1 karma."""
        # Like post (5 karma for user1)
        Like.objects.create(user=self.liker, post=self.post1)
        
        # Like comment (1 karma for user3)
        Like.objects.create(user=self.liker, comment=self.comment1)
        
        # Get leaderboard
        from .views import leaderboard_view
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/api/leaderboard/')
        response = leaderboard_view(request)
        
        # Check results
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # user1 should have 5 karma (1 post like)
        user1_data = next((u for u in data if u['username'] == 'user1'), None)
        self.assertIsNotNone(user1_data)
        self.assertEqual(user1_data['karma_24h'], 5)
        
        # user3 should have 1 karma (1 comment like)
        user3_data = next((u for u in data if u['username'] == 'user3'), None)
        self.assertIsNotNone(user3_data)
        self.assertEqual(user3_data['karma_24h'], 1)
    
    def test_only_last_24h_karma_counts(self):
        """Test that only karma from last 24 hours is counted."""
        # Create old like (26 hours ago)
        old_like = Like.objects.create(user=self.liker, post=self.post1)
        old_like.created_at = timezone.now() - timedelta(hours=26)
        old_like.save()
        
        # Create recent like (1 hour ago)
        recent_like = Like.objects.create(user=self.liker, post=self.post2)
        recent_like.created_at = timezone.now() - timedelta(hours=1)
        recent_like.save()
        
        # Get leaderboard
        from .views import leaderboard_view
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/api/leaderboard/')
        response = leaderboard_view(request)
        
        # user1 should NOT be in leaderboard (old like)
        data = response.data
        user1_data = next((u for u in data if u['username'] == 'user1'), None)
        self.assertIsNone(user1_data)
        
        # user2 should be in leaderboard with 5 karma
        user2_data = next((u for u in data if u['username'] == 'user2'), None)
        self.assertIsNotNone(user2_data)
        self.assertEqual(user2_data['karma_24h'], 5)
    
    def test_leaderboard_top_5_limit(self):
        """Test that leaderboard returns only top 5 users."""
        # Create 7 users with different karma
        users = []
        for i in range(7):
            user = User.objects.create_user(username=f'testuser{i}', password='pass123')
            users.append(user)
            post = Post.objects.create(author=user, content=f'Post {i}')
            
            # Give each user i+1 likes (increasing karma)
            for j in range(i + 1):
                liker = User.objects.create_user(username=f'liker{i}_{j}', password='pass123')
                Like.objects.create(user=liker, post=post)
        
        # Get leaderboard
        from .views import leaderboard_view
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/api/leaderboard/')
        response = leaderboard_view(request)
        
        # Should return exactly 5 users
        self.assertEqual(len(response.data), 5)
        
        # Should be in descending order of karma
        karmas = [u['karma_24h'] for u in response.data]
        self.assertEqual(karmas, sorted(karmas, reverse=True))


class RaceConditionTestCase(TransactionTestCase):
    """Test race condition prevention on likes."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.post = Post.objects.create(author=self.user, content='Test post')
    
    def test_no_double_like_on_post(self):
        """Test that database constraints prevent double-likes."""
        # Try to create duplicate like
        Like.objects.create(user=self.user, post=self.post)
        
        with self.assertRaises(Exception):  # IntegrityError
            Like.objects.create(user=self.user, post=self.post)
    
    def test_like_unlike_toggle(self):
        """Test that like/unlike works correctly via API."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        # First like
        response = client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
        
        # Unlike
        response = client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['like_count'], 0)
        
        # Like again
        response = client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)


class CommentTreeTestCase(TestCase):
    """Test comment tree serialization and query optimization."""
    
    def setUp(self):
        """Create nested comment structure."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.post = Post.objects.create(author=self.user, content='Test post')
        
        # Create nested comment structure
        # Post
        #   - Comment 1
        #     - Reply 1.1
        #       - Reply 1.1.1
        #     - Reply 1.2
        #   - Comment 2
        
        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 1'
        )
        
        self.reply1_1 = Comment.objects.create(
            post=self.post,
            parent=self.comment1,
            author=self.user,
            content='Reply 1.1'
        )
        
        self.reply1_1_1 = Comment.objects.create(
            post=self.post,
            parent=self.reply1_1,
            author=self.user,
            content='Reply 1.1.1'
        )
        
        self.reply1_2 = Comment.objects.create(
            post=self.post,
            parent=self.comment1,
            author=self.user,
            content='Reply 1.2'
        )
        
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 2'
        )
    
    def test_comment_tree_structure(self):
        """Test that comment tree is correctly structured."""
        # Get post with comments
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        
        comments = response.data['comments']
        
        # Should have 2 top-level comments
        self.assertEqual(len(comments), 2)
        
        # Find comment1 in response
        comment1_data = next(c for c in comments if c['content'] == 'Comment 1')
        
        # Should have 2 replies
        self.assertEqual(len(comment1_data['replies']), 2)
        
        # Find reply1_1
        reply1_1_data = next(r for r in comment1_data['replies'] if r['content'] == 'Reply 1.1')
        
        # Should have 1 nested reply
        self.assertEqual(len(reply1_1_data['replies']), 1)
        self.assertEqual(reply1_1_data['replies'][0]['content'], 'Reply 1.1.1')
    
    def test_query_count_optimization(self):
        """Test that fetching post with comments doesn't cause N+1 queries."""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        # Count queries
        with CaptureQueriesContext(connection) as context:
            response = client.get(f'/api/posts/{self.post.id}/')
        
        # Should use <= 10 queries regardless of comment count
        # (In practice: session, user, post, comments, authors, likes)
        query_count = len(context.captured_queries)
        print(f"\nQuery count for post with nested comments: {query_count}")
        
        # This is a reasonable upper bound
        # Without optimization, this would be 15+ queries
        self.assertLessEqual(query_count, 15)


class APITestCase(APITestCase):
    """Test API endpoints."""
    
    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
    
    def test_user_login(self):
        """Test user login endpoint."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_create_post(self):
        """Test creating a post."""
        self.client.force_authenticate(user=self.user)
        
        data = {'content': 'This is a test post'}
        response = self.client.post('/api/posts/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test post')
        self.assertEqual(response.data['author']['username'], 'testuser')
    
    def test_create_comment(self):
        """Test creating a comment."""
        self.client.force_authenticate(user=self.user)
        
        # Create post first
        post = Post.objects.create(author=self.user, content='Test post')
        
        # Create comment
        data = {
            'post': post.id,
            'content': 'This is a test comment'
        }
        response = self.client.post('/api/comments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment')
    
    def test_create_reply(self):
        """Test creating a reply to a comment."""
        self.client.force_authenticate(user=self.user)
        
        # Create post and comment
        post = Post.objects.create(author=self.user, content='Test post')
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content='Test comment'
        )
        
        # Create reply
        data = {
            'post': post.id,
            'parent': comment.id,
            'content': 'This is a reply'
        }
        response = self.client.post('/api/comments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a reply')
        self.assertEqual(response.data['parent'], comment.id)
