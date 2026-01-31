import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { postsAPI } from '../services/api';
import { formatDistanceToNow } from '../utils/dateUtils';

export default function PostCard({ post: initialPost, user, onUpdate }) {
  const [post, setPost] = useState(initialPost);
  const [liking, setLiking] = useState(false);

  const handleLike = async (e) => {
    e.preventDefault();
    if (!user || liking) return;

    setLiking(true);
    try {
      const response = await postsAPI.like(post.id);
      setPost({
        ...post,
        is_liked: response.data.liked,
        like_count: response.data.like_count,
      });
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to like post:', error);
    } finally {
      setLiking(false);
    }
  };

  return (
    <div className="card card-hover p-6 animate-slide-up">
      {/* Author Info */}
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
          <span className="text-sm font-semibold text-white">
            {post.author.username.charAt(0).toUpperCase()}
          </span>
        </div>
        <div>
          <div className="font-semibold text-white">{post.author.username}</div>
          <div className="text-xs text-slate-400">
            {formatDistanceToNow(post.created_at)}
          </div>
        </div>
      </div>

      {/* Content */}
      <Link to={`/post/${post.id}`} className="block">
        <p className="text-slate-200 mb-4 leading-relaxed whitespace-pre-wrap">
          {post.content}
        </p>
      </Link>

      {/* Actions */}
      <div className="flex items-center space-x-6 pt-4 border-t border-slate-700/50">
        {/* Like Button */}
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
            className={`w-5 h-5 transition-transform duration-200 ${
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
          <span className="text-sm font-medium">{post.like_count}</span>
          <span className="text-xs text-slate-500">+5 karma</span>
        </button>

        {/* Comment Button */}
        <Link
          to={`/post/${post.id}`}
          className="flex items-center space-x-2 text-slate-400 hover:text-primary-500 transition-colors duration-200 group"
        >
          <svg
            className="w-5 h-5 group-hover:scale-110 transition-transform duration-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span className="text-sm font-medium">{post.comment_count || 0}</span>
        </Link>
      </div>
    </div>
  );
}
