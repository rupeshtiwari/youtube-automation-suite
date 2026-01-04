import React, { useState, useEffect } from 'react';
import { Clock, Send, Trash2, Plus } from 'lucide-react';

interface QueueItem {
  id: number;
  video_id: string;
  video_title: string;
  youtube_url: string;
  platform: string;
  post_content: string;
  schedule_date: string;
  actual_scheduled_date: string;
  status: 'pending' | 'scheduled' | 'published' | 'failed';
  created_at: string;
}

interface Channel {
  id: string;
  name: string;
  type: 'youtube' | 'facebook' | 'linkedin' | 'instagram';
}

interface PublishToChannelPayload {
  video_id: string;
  target_channels: string[];
  scheduled_date: string;
  notes?: string;
}

const Queue: React.FC = () => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal states
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<QueueItem | null>(null);
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [scheduledDate, setScheduledDate] = useState(new Date().toISOString().split('T')[0]);
  const [scheduledTime, setScheduledTime] = useState('10:00');

  useEffect(() => {
    fetchQueue();
    fetchChannels();
  }, []);

  const fetchQueue = async () => {
    try {
      const response = await fetch('/api/queue');
      const data = await response.json();
      if (data.success) {
        // Combine draft and scheduled posts
        const allPosts = [
          ...(data.draft_posts || []),
          ...(data.scheduled_posts || []),
          ...(data.published_posts || [])
        ];
        setQueueItems(allPosts);
      }
    } catch (err) {
      setError('Failed to load queue');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchChannels = async () => {
    try {
      const response = await fetch('/api/channels');
      const data = await response.json();
      if (data.success) {
        setChannels(data.channels || []);
      }
    } catch (err) {
      console.error('Failed to fetch channels:', err);
    }
  };

  const openPublishModal = (item: QueueItem) => {
    setSelectedVideo(item);
    setSelectedChannels([]);
    setShowPublishModal(true);
  };

  const handleChannelToggle = (channelId: string) => {
    setSelectedChannels(prev =>
      prev.includes(channelId)
        ? prev.filter(id => id !== channelId)
        : [...prev, channelId]
    );
  };

  const handlePublish = async () => {
    if (!selectedVideo || selectedChannels.length === 0) {
      setError('Please select at least one channel');
      return;
    }

    try {
      const payload: PublishToChannelPayload = {
        video_id: selectedVideo.video_id,
        target_channels: selectedChannels,
        scheduled_date: `${scheduledDate}T${scheduledTime}`,
        notes: `Published to ${selectedChannels.length} channel(s)`
      };

      const response = await fetch('/api/queue/publish-to-channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (data.success) {
        setSuccess(`Successfully scheduled publishing to ${selectedChannels.length} channel(s)`);
        setShowPublishModal(false);
        setSelectedVideo(null);
        setSelectedChannels([]);
        fetchQueue();
      } else {
        setError(data.error || 'Failed to schedule publishing');
      }
    } catch (err) {
      setError('Error scheduling publication');
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
      const response = await fetch(`/api/queue/${id}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      if (data.success) {
        setSuccess('Item deleted successfully');
        fetchQueue();
      } else {
        setError(data.error || 'Failed to delete item');
      }
    } catch (err) {
      setError('Error deleting item');
      console.error(err);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      pending: 'bg-gray-100 text-gray-800',
      scheduled: 'bg-blue-100 text-blue-800',
      published: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusStyles[status as keyof typeof statusStyles] || statusStyles.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getPlatformIcon = (platform: string) => {
    const icons: { [key: string]: string } = {
      youtube: '📺',
      facebook: '📘',
      linkedin: '💼',
      instagram: '📷',
      twitter: '𝕏'
    };
    return icons[platform] || '📱';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading queue...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📅 Publishing Queue</h1>
          <p className="text-gray-600 mt-1">Schedule and manage cross-channel video publishing</p>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

      {/* Queue List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {queueItems.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No items in queue yet.</p>
            <p className="text-sm mt-1">Generate content or upload videos to populate the queue.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {queueItems.map(item => (
              <div key={`${item.id}-${item.platform}`} className="p-4 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getPlatformIcon(item.platform)}</span>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {item.video_title || 'Untitled'}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">{item.platform.toUpperCase()}</span>
                          {getStatusBadge(item.status)}
                        </div>
                      </div>
                    </div>

                    {/* Content preview */}
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {item.post_content || item.video_title}
                    </p>

                    {/* Scheduled date */}
                    {item.schedule_date && (
                      <div className="flex items-center gap-1 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        Scheduled: {new Date(item.schedule_date).toLocaleString()}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {item.status === 'pending' || item.status === 'scheduled' ? (
                      <>
                        <button
                          onClick={() => openPublishModal(item)}
                          className="p-2 hover:bg-blue-100 rounded-lg transition text-blue-600"
                          title="Publish to more channels"
                        >
                          <Plus className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-2 hover:bg-red-100 rounded-lg transition text-red-600"
                          title="Delete"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </>
                    ) : null}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Publish Modal */}
      {showPublishModal && selectedVideo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Publish to Channels</h2>
                <p className="text-sm text-gray-600 mt-1">{selectedVideo.video_title}</p>
              </div>
              <button
                onClick={() => setShowPublishModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-4 space-y-4">
              {/* Channel Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Select Channels to Publish
                </label>
                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
                  {channels.length === 0 ? (
                    <p className="text-sm text-gray-500 py-4">
                      No channels configured. Please connect channels in Settings first.
                    </p>
                  ) : (
                    channels.map(channel => (
                      <label key={channel.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedChannels.includes(channel.id)}
                          onChange={() => handleChannelToggle(channel.id)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-2xl">{getPlatformIcon(channel.type)}</span>
                        <span className="text-sm text-gray-700">{channel.name}</span>
                      </label>
                    ))
                  )}
                </div>
              </div>

              {/* Scheduled Date/Time */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-1">
                    Scheduled Date
                  </label>
                  <input
                    type="date"
                    value={scheduledDate}
                    onChange={e => setScheduledDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-1">
                    Time
                  </label>
                  <input
                    type="time"
                    value={scheduledTime}
                    onChange={e => setScheduledTime(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-4 flex justify-end gap-2">
              <button
                onClick={() => setShowPublishModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handlePublish}
                disabled={selectedChannels.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Schedule Publishing
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Queue;
