import { Star, Archive, Trash2, Mail, MailOpen, Paperclip } from 'lucide-react';

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

interface RecentDetectionsProps {
  emails: Email[];
  markAsImportant: (emailId: number) => void;
  toggleArchive: (emailId: number) => void;
  toggleRead: (emailId: number) => void;
  deleteEmail: (emailId: number) => void;
}

export default function RecentDetections({ 
  emails, 
  markAsImportant, 
  toggleArchive, 
  toggleRead,
  deleteEmail 
}: RecentDetectionsProps) {
  // Enhanced detection formatting with type safety
  const getAnalysisType = (email: Email) => {
    if (email.is_phishing) return 'Phishing';
    if (email.is_spam) return 'Spam';
    return email.category || 'Normal';
  };

  const getRuleType = (email: Email) => {
    if (email.is_phishing) return 'Phishing Detection';
    if (email.is_spam) return 'Spam Filter';
    return 'Security Scan';
  };

  return (
    <div className="rounded-xl border bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold">Recent Detections</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b text-sm text-muted-foreground">
              <th className="pb-3 text-left font-medium">Subject</th>
              <th className="pb-3 text-left font-medium">Priority</th>
              <th className="pb-3 text-left font-medium">Analysis</th>
              <th className="pb-3 text-left font-medium">Service</th>
              <th className="pb-3 text-left font-medium">Policy</th>
              <th className="pb-3 text-left font-medium">Rule</th>
              <th className="pb-3 text-left font-medium">Date/Time</th>
              <th className="pb-3 text-left font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {emails.map((email) => (
              <tr key={email.id} className={`border-b last:border-0 ${
                email.is_archived ? 'bg-gray-50' : ''
              } ${
                !email.is_read ? 'font-medium' : ''
              }`}>
                <td className="py-3 font-medium">
                  <div className="flex items-center">
                    {email.subject}
                    {email.has_attachment && <Paperclip className="w-4 h-4 ml-2 text-gray-400" />}
                  </div>
                </td>
                <td className="py-3">
                  <span className={`rounded-full px-2 py-1 text-xs ${
                    email.priority_level === 3 ? 'bg-red-100 text-red-800' :
                    email.priority_level === 2 ? 'bg-orange-100 text-orange-800' :
                    email.priority_level === 1 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {email.priority_level === 3 ? 'High' : email.priority_level === 2 ? 'Medium' : email.priority_level === 1 ? 'Low' : 'Normal'}
                  </span>
                </td>
                <td className="py-3">
                  <span className={`rounded-full px-2 py-1 text-xs ${
                    email.is_phishing ? 'bg-red-100 text-red-800' :
                    email.is_spam ? 'bg-yellow-100 text-yellow-800' : 'bg-muted'
                  }`}>
                    {getAnalysisType(email)}
                  </span>
                </td>
                <td className="py-3">Email Security</td>
                <td className="py-3">{email.category || 'Default'}</td>
                <td className="py-3">{getRuleType(email)}</td>
                <td className="py-3">
                  {new Date(email.email_date).toLocaleString()}
                </td>
                <td className="py-3">
                  <div className="flex items-center space-x-2">
                    {/* Important Flag Button */}
                    <button
                      onClick={() => markAsImportant(email.id)}
                      className={`p-1 rounded-full hover:bg-yellow-100 transition-colors ${
                        email.is_important ? 'text-yellow-500' : 'text-gray-300'
                      }`}
                      aria-label={email.is_important ? 'Marked important' : 'Mark as important'}
                      title={email.is_important ? 'Marked important' : 'Mark as important'}
                    >
                      <Star 
                        className="w-5 h-5" 
                        fill={email.is_important ? 'currentColor' : 'none'}
                      />
                    </button>
                    
                    {/* Archive Button */}
                    <button
                      onClick={() => toggleArchive(email.id)}
                      className={`p-1 rounded-full hover:bg-blue-100 transition-colors ${
                        email.is_archived ? 'text-blue-500' : 'text-gray-300'
                      }`}
                      aria-label={email.is_archived ? 'Unarchive' : 'Archive'}
                      title={email.is_archived ? 'Unarchive' : 'Archive'}
                    >
                      <Archive 
                        className="w-5 h-5" 
                        fill={email.is_archived ? 'currentColor' : 'none'}
                      />
                    </button>
                    
                    {/* Read/Unread Button */}
                    <button
                      onClick={() => toggleRead(email.id)}
                      className={`p-1 rounded-full hover:bg-green-100 transition-colors ${
                        email.is_read ? 'text-green-500' : 'text-gray-300'
                      }`}
                      aria-label={email.is_read ? 'Mark as unread' : 'Mark as read'}
                      title={email.is_read ? 'Mark as unread' : 'Mark as read'}
                    >
                      {email.is_read ? 
                        <MailOpen className="w-5 h-5" /> : 
                        <Mail className="w-5 h-5" />
                      }
                    </button>
                    
                    {/* Delete Button */}
                    <button
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this email?')) {
                          deleteEmail(email.id);
                        }
                      }}
                      className="p-1 rounded-full hover:bg-red-100 text-gray-300 hover:text-red-500 transition-colors"
                      aria-label="Delete email"
                      title="Delete email"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
