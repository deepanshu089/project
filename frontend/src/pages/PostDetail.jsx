import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { postsAPI, commentsAPI } from '../services/api';
import Comment from '../components/Comment';
import { formatDistanceToNow } from '../utils/dateUtils';

export default function PostDetail({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [commentContent, setCommentContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [liking, setLiking] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await postsAPI.getById(id);
      setPost(response.data);
    } catch (error) {
      console.error('Failed to fetch post:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!user || liking) return;

    setLiking(true);
    try {
      const response = await postsAPI.like(post.id);
      setPost({
        ...post,
        is_liked: response.data.liked,
        like_count: response.data.like_count,
      });
    } catch (error) {
      console.error('Failed to like post:', error);
    } finally {
      setLiking(false);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!commentContent.trim() || submitting) return;

    setSubmitting(true);
    try {
      await commentsAPI.create({
        post: post.id,
        content: commentContent,
      });
      setCommentContent('');
      fetchPost(); // Refresh to get new comment
    } catch (error) {
      console.error('Failed to post comment:', error);
      alert('Failed to post comment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="card p-8">
            <div className="shimmer h-64 rounded-lg bg-slate-700/30"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Post not found</h2>
          <Link to="/" className="btn-primary">
            Back to Feed
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-slate-400 hover:text-white transition-colors duration-200"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back</span>
        </button>

        {/* Post */}
        <div className="card p-8 animate-slide-up">
          {/* Author Info */}
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-xl font-semibold text-white">
                {post.author.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <div className="text-lg font-semibold text-white">{post.author.username}</div>
              <div className="text-sm text-slate-400">
                {formatDistanceToNow(post.created_at)}
              </div>
            </div>
          </div>

          {/* Content */}
          <p className="text-slate-200 text-lg leading-relaxed mb-6 whitespace-pre-wrap">
            {post.content}
          </p>

          {/* Actions */}
          <div className="flex items-center space-x-6 pt-6 border-t border-slate-700/50">
            <button
              onClick={handleLike}
              disabled={!user || liking}
              className={`flex items-center space-x-2 transition-all duration-200 ${
                post.is_liked
                  ? 'text-red-500'
                  : 'text-slate-400 hover:text-red-500'
              } ${!user ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'} group`}
            >
              <svg
                className={`w-6 h-6 transition-transform duration-200 ${
                  post.is_liked ? 'fill-current scale-110' : 'group-hover:scale-110'
                }`}
                fill={post.is_liked ? 'currentColor' : 'none'}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
              <span className="font-semibold">{post.like_count}</span>
              <span className="text-sm text-slate-500">+5 karma</span>
            </button>

            <div className="flex items-center space-x-2 text-slate-400">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <span className="font-semibold">{post.comments?.length || 0} comments</span>
            </div>
          </div>
        </div>

        {/* Add Comment */}
        {user ? (
          <div className="card p-6 animate-slide-up">
            <h3 className="text-lg font-semibold text-white mb-4">Add a Comment</h3>
            <form onSubmit={handleSubmitComment}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-semibold text-white">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="flex-1">
                  <textarea
                    value={commentContent}
                    onChange={(e) => setCommentContent(e.target.value)}
                    placeholder="Share your thoughts..."
                    className="textarea-field"
                    rows="3"
                  />
                  <div className="flex items-center justify-between mt-3">
                    <p className="text-xs text-slate-400">
                      💡 Comment likes earn you <span className="text-primary-400 font-semibold">1 karma</span>
                    </p>
                    <button
                      type="submit"
                      disabled={!commentContent.trim() || submitting}
                      className="btn-primary"
                    >
                      {submitting ? 'Posting...' : 'Comment'}
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>
        ) : (
          <div className="card p-6 text-center">
            <p className="text-slate-400 mb-4">Please log in to comment</p>
            <Link to="/login" className="btn-primary">
              Log In
            </Link>
          </div>
        )}

        {/* Comments */}
        {post.comments && post.comments.length > 0 && (
          <div className="card p-6 animate-slide-up">
            <h3 className="text-lg font-semibold text-white mb-6">
              Comments ({post.comments.length})
            </h3>
            <div className="space-y-6">
              {post.comments.map((comment) => (
                <Comment
                  key={comment.id}
                  comment={comment}
                  user={user}
                  postId={post.id}
                  onReply={fetchPost}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
