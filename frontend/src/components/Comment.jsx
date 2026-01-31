import React, { useState } from 'react';
import { commentsAPI } from '../services/api';
import { formatDistanceToNow } from '../utils/dateUtils';

export default function Comment({ comment: initialComment, user, postId, onReply }) {
  const [comment, setComment] = useState(initialComment);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [liking, setLiking] = useState(false);

  const handleLike = async () => {
    if (!user || liking) return;

    setLiking(true);
    try {
      const response = await commentsAPI.like(comment.id);
      setComment({
        ...comment,
        is_liked: response.data.liked,
        like_count: response.data.like_count,
      });
    } catch (error) {
      console.error('Failed to like comment:', error);
    } finally {
      setLiking(false);
    }
  };

  const handleSubmitReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim() || submitting) return;

    setSubmitting(true);
    try {
      const response = await commentsAPI.create({
        post: postId,
        parent: comment.id,
        content: replyContent,
      });
      
      // Add reply to comment
      setComment({
        ...comment,
        replies: [...(comment.replies || []), response.data],
      });
      
      setReplyContent('');
      setShowReplyForm(false);
      if (onReply) onReply();
    } catch (error) {
      console.error('Failed to post reply:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="animate-slide-up">
      <div className="flex space-x-3">
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-xs font-semibold text-white">
              {comment.author.username.charAt(0).toUpperCase()}
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
            {/* Author and Time */}
            <div className="flex items-center space-x-2 mb-2">
              <span className="font-semibold text-white text-sm">
                {comment.author.username}
              </span>
              <span className="text-xs text-slate-500">•</span>
              <span className="text-xs text-slate-400">
                {formatDistanceToNow(comment.created_at)}
              </span>
            </div>

            {/* Comment Text */}
            <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
              {comment.content}
            </p>

            {/* Actions */}
            <div className="flex items-center space-x-4 mt-3">
              {/* Like */}
              <button
                onClick={handleLike}
                disabled={!user || liking}
                className={`flex items-center space-x-1 text-xs transition-all duration-200 ${
                  comment.is_liked
                    ? 'text-red-500'
                    : 'text-slate-400 hover:text-red-500'
                } ${!user ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'} group`}
              >
                <svg
                  className={`w-4 h-4 transition-transform duration-200 ${
                    comment.is_liked ? 'fill-current scale-110' : 'group-hover:scale-110'
                  }`}
                  fill={comment.is_liked ? 'currentColor' : 'none'}
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
                <span className="font-medium">{comment.like_count || 0}</span>
                <span className="text-slate-500">+1</span>
              </button>

              {/* Reply */}
              {user && (
                <button
                  onClick={() => setShowReplyForm(!showReplyForm)}
                  className="text-xs text-slate-400 hover:text-primary-500 transition-colors duration-200 font-medium"
                >
                  Reply
                </button>
              )}
            </div>
          </div>

          {/* Reply Form */}
          {showReplyForm && (
            <form onSubmit={handleSubmitReply} className="mt-3 animate-slide-up">
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Write a reply..."
                className="textarea-field text-sm"
                rows="3"
                autoFocus
              />
              <div className="flex items-center space-x-2 mt-2">
                <button
                  type="submit"
                  disabled={!replyContent.trim() || submitting}
                  className="btn-primary text-sm py-1.5 px-4"
                >
                  {submitting ? 'Posting...' : 'Reply'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowReplyForm(false);
                    setReplyContent('');
                  }}
                  className="btn-secondary text-sm py-1.5 px-4"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Nested Replies */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-4 space-y-4 border-l-2 border-slate-700/50 pl-4">
              {comment.replies.map((reply) => (
                <Comment
                  key={reply.id}
                  comment={reply}
                  user={user}
                  postId={postId}
                  onReply={onReply}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
