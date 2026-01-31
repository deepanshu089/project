"""
Script to create sample data for testing the Playto Community Feed.

Run with: python manage.py shell < create_sample_data.py
Or: python manage.py shell
     >>> exec(open('create_sample_data.py').read())
"""

from django.contrib.auth.models import User
from community.models import Post, Comment, Like
from django.utils import timezone
from datetime import timedelta
import random

print("Creating sample data...")

# Create users
users = []
usernames = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry']

for username in usernames:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"✓ Created user: {username}")
    else:
        print(f"- User already exists: {username}")
    users.append(user)

# Create posts
post_contents = [
    "Just finished building an amazing community feed app! The threaded comments feature is so smooth. 🚀",
    "What's everyone's favorite programming language? I'm torn between Python and JavaScript.",
    "Hot take: Dark mode is overrated. Fight me! 😄",
    "Just hit 1000 karma! Thanks everyone for the support! 🎉",
    "Anyone else working on side projects this weekend? Would love to hear what you're building!",
    "The new leaderboard feature is addictive. I can't stop trying to get to the top! 🏆",
    "Pro tip: Always write tests before deploying to production. Learned this the hard way...",
    "What's the best way to handle race conditions in Django? Looking for advice!",
    "Just discovered prefetch_related and my queries went from 100+ to 4. Mind blown! 🤯",
    "Community feedback: Should we add image uploads? Vote with likes!",
]

posts = []
for i, content in enumerate(post_contents):
    author = users[i % len(users)]
    post = Post.objects.create(
        author=author,
        content=content
    )
    posts.append(post)
    print(f"✓ Created post by {author.username}")

# Create comments with threading
comment_contents = [
    "Great work! This looks amazing.",
    "I totally agree with this!",
    "Interesting perspective. I never thought about it that way.",
    "Thanks for sharing! Very helpful.",
    "This is exactly what I needed to hear today.",
    "Could you elaborate more on this?",
    "I have a different opinion, but I respect yours.",
    "This deserves more upvotes!",
    "Brilliant implementation!",
    "How did you solve the N+1 query problem?",
]

comments = []
for post in posts[:5]:  # Add comments to first 5 posts
    # Top-level comments
    for i in range(random.randint(2, 4)):
        author = random.choice(users)
        comment = Comment.objects.create(
            post=post,
            author=author,
            content=random.choice(comment_contents)
        )
        comments.append(comment)
        
        # Replies to comments
        if random.random() > 0.5:
            reply_author = random.choice(users)
            reply = Comment.objects.create(
                post=post,
                parent=comment,
                author=reply_author,
                content=random.choice(comment_contents)
            )
            comments.append(reply)
            
            # Nested replies
            if random.random() > 0.7:
                nested_reply_author = random.choice(users)
                Comment.objects.create(
                    post=post,
                    parent=reply,
                    author=nested_reply_author,
                    content=random.choice(comment_contents)
                )

print(f"✓ Created {Comment.objects.count()} comments with threading")

# Create likes
# Recent likes (last 24 hours)
for post in posts:
    num_likes = random.randint(5, 20)
    likers = random.sample(users, min(num_likes, len(users)))
    for liker in likers:
        if liker != post.author:  # Don't like your own post
            Like.objects.get_or_create(
                user=liker,
                post=post
            )

# Likes on comments
for comment in comments[:15]:
    num_likes = random.randint(1, 8)
    likers = random.sample(users, min(num_likes, len(users)))
    for liker in likers:
        if liker != comment.author:
            Like.objects.get_or_create(
                user=liker,
                comment=comment
            )

print(f"✓ Created {Like.objects.count()} likes")

# Create some old likes (more than 24 hours ago) to test leaderboard
old_time = timezone.now() - timedelta(hours=30)
for post in posts[:3]:
    old_like = Like.objects.create(
        user=users[0],
        post=post
    )
    old_like.created_at = old_time
    old_like.save()

print(f"✓ Created old likes for testing")

# Print summary
print("\n" + "="*50)
print("SAMPLE DATA CREATED SUCCESSFULLY!")
print("="*50)
print(f"Users: {User.objects.count()}")
print(f"Posts: {Post.objects.count()}")
print(f"Comments: {Comment.objects.count()}")
print(f"Likes: {Like.objects.count()}")
print("\nTest credentials:")
print("Username: alice, bob, charlie, etc.")
print("Password: password123")
print("\nYou can now test the application with realistic data!")
