"use client";

import React, { useState, useEffect, useMemo } from 'react';
import io from 'socket.io-client';
import { type Socket as SocketClient } from 'socket.io-client';
import { Bug, ShieldAlert, ShieldX, SpellCheckIcon as Spam, Star, TrendingUp } from 'lucide-react';
import DetectionChart from '../components/detection-chart';
import DetectionOverview from './detection-overview';
import RecentDetections from './recent-detections';
import SecurityMetricCard from '../components/security-metric-card';
import EmailProcessorControl from '../components/email-processor-control';

// API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface Email {
  id: number;
  sender: string;
  subject: string;
  is_spam: boolean;
  is_phishing: boolean;
  category: string;
  email_date: string;
  is_important: boolean;
  is_archived: boolean;
  is_read: boolean;
  priority_level: number;
  has_attachment: boolean;
}

const SecurityDashboard = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [socket, setSocket] = useState<ReturnType<typeof io> | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [processingResult, setProcessingResult] = useState<any>(null);

  // WebSocket initialization with error handling
  useEffect(() => {
    const newSocket = io(`${API_URL}/emails`, {
      path: '/socket.io',
      transports: ['websocket'],
      auth: {
        token: localStorage.getItem('token')
      }
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected to email namespace');
      setError(null);
      // No need to emit join since we're connecting directly to the namespace
    });

    newSocket.on('new_email', (newEmail: Email) => {
      setEmails(prev => Array.isArray(prev) ? [newEmail, ...prev] : [newEmail]);
    });

    newSocket.on('email_updated', (updatedEmail: Email) => {
      setEmails(prev => prev.map(email => 
        email.id === updatedEmail.id ? updatedEmail : email
      ));
    });

    newSocket.on('connect_error', (err: Error) => {
      console.error('Connection error:', err.message);
      setError('Real-time updates disabled - connection issues');
    });

    // Add handler for email_deleted event
    newSocket.on('email_deleted', (data: {id: number}) => {
      setEmails(prev => prev.filter(email => email.id !== data.id));
    });

    setSocket(newSocket);

    return () => {
      newSocket.off('connect');
      newSocket.off('new_email');
      newSocket.off('email_updated');
      newSocket.off('connect_error');
      newSocket.off('email_deleted');
      newSocket.disconnect();
    };
  }, []);

  // Initial email fetch with abort controller
  useEffect(() => {
    const controller = new AbortController();
    
    const fetchEmails = async () => {
      try {
        const response = await fetch(`${API_URL}/emails`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          signal: controller.signal
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setEmails(Array.isArray(data) ? data : []);
        setLoading(false);
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : 'Failed to load emails');
          setLoading(false);
        }
      }
    };

    fetchEmails();
    return () => controller.abort();
  }, []);

  // Function to refresh emails
  const refreshEmails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/emails`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setEmails(Array.isArray(data) ? data : []);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load emails');
      setLoading(false);
    }
  };

  // Email marking functionality
  const markAsImportant = async (emailId: number) => {
    try {
      const response = await fetch(`${API_URL}/emails/${emailId}/mark-important`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to mark email');
    } catch (err) {
      setUpdateError('Failed to update email status');
      setTimeout(() => setUpdateError(null), 3000);
      console.error('Error marking email:', err);
    }
  };

  // Archive email functionality
  const toggleArchive = async (emailId: number) => {
    try {
      const response = await fetch(`${API_URL}/emails/${emailId}/toggle-archive`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to archive email');
    } catch (err) {
      setUpdateError('Failed to archive email');
      setTimeout(() => setUpdateError(null), 3000);
      console.error('Error archiving email:', err);
    }
  };

  // Toggle read status functionality
  const toggleRead = async (emailId: number) => {
    try {
      const response = await fetch(`${API_URL}/emails/${emailId}/toggle-read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to update read status');
    } catch (err) {
      setUpdateError('Failed to update read status');
      setTimeout(() => setUpdateError(null), 3000);
      console.error('Error updating read status:', err);
    }
  };

  // Delete email functionality
  const deleteEmail = async (emailId: number) => {
    try {
      const response = await fetch(`${API_URL}/emails/${emailId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to delete email');
      
      // Remove email from local state if WebSocket fails
      setEmails(prev => prev.filter(email => email.id !== emailId));
    } catch (err) {
      setUpdateError('Failed to delete email');
      setTimeout(() => setUpdateError(null), 3000);
      console.error('Error deleting email:', err);
    }
  };

  // Handle email processing complete
  const handleProcessingComplete = (result: any) => {
    // Show success message
    setProcessingResult(result);
    
    // Automatically refresh the email list
    refreshEmails();
    
    // Clear the result after 5 seconds
    setTimeout(() => {
      setProcessingResult(null);
    }, 5000);
  };

  // Security metrics calculation
  const metrics = useMemo(() => [
    { 
      title: 'Malware', 
      detections: emails.filter(e => e.category === 'Malware').length,
      icon: Bug,
      color: 'text-blue-500',
    },
    { 
      title: 'Phishing', 
      detections: emails.filter(e => e.is_phishing).length,
      icon: ShieldAlert,
      color: 'text-green-500',
    },
    { 
      title: 'Total Detections', 
      detections: emails.length,
      icon: ShieldX,
      color: 'text-yellow-500',
    },
    { 
      title: 'Spam', 
      detections: emails.filter(e => e.is_spam).length,
      icon: Spam,
      color: 'text-purple-500',
    },
    { 
      title: 'Important', 
      detections: emails.filter(e => e.is_important).length,
      icon: Star,
      color: 'text-orange-500',
    }
  ], [emails]);

  const overviewProps = {
    totalDetections: emails.length,
    percentageChange: 2.5, // Dummy data, replace with actual calculation
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-t-transparent border-blue-500"></div>
        <p className="text-gray-600">Loading security data...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6 max-w-2xl mx-auto bg-red-50 rounded-lg shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-red-800 font-semibold">Connection Error</h3>
            <p className="text-red-700 mt-1">{error}</p>
            <p className="text-sm mt-2">
              WebSocket status: {socket?.connected ? '✅ Connected' : '❌ Disconnected'}
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-100 text-red-800 rounded-md hover:bg-red-200 transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  // Main dashboard UI
  return (
    <div className="container mx-auto p-6 space-y-8">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Security Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1 rounded-full text-sm ${
            socket?.connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {socket?.connected ? 'Live Updates' : 'Offline Mode'}
          </span>
          {updateError && (
            <div className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
              {updateError}
            </div>
          )}
        </div>
      </header>

      {/* Processing Result Notification */}
      {processingResult && (
        <div className="bg-green-50 text-green-800 p-4 rounded-lg mb-4 flex justify-between items-center">
          <div>
            <h3 className="font-medium">Email Processing Complete</h3>
            <p className="text-sm mt-1">
              Successfully processed emails from {processingResult.results ? Object.keys(processingResult.results).join(', ') : 'selected categories'}.
            </p>
          </div>
          <button 
            onClick={() => setProcessingResult(null)}
            className="text-green-700 hover:text-green-900"
          >
            ✕
          </button>
        </div>
      )}

      {/* Email Processor Control Panel */}
      <EmailProcessorControl 
        onProcessingComplete={handleProcessingComplete}
      />

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <DetectionOverview 
          totalDetections={emails.length} 
          percentageChange={2.5}
        />
        <DetectionChart />
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => (
          <SecurityMetricCard 
            key={metric.title}
            title={metric.title}
            detections={metric.detections}
            icon={metric.icon}
            color={metric.color}
          />
        ))}
      </section>

      <section className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Detections</h2>
        <RecentDetections 
          emails={emails.slice(0, 10)} 
          markAsImportant={markAsImportant}
          toggleArchive={toggleArchive}
          toggleRead={toggleRead}
          deleteEmail={deleteEmail}
        />
      </section>
    </div>
  );
};

export default SecurityDashboard;
