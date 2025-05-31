import React, { useState } from 'react';
import { RefreshCw, Calendar, Hash, CheckSquare } from 'lucide-react';

interface EmailProcessorControlProps {
  onProcessingComplete: (result: any) => void;
}

const EmailProcessorControl: React.FC<EmailProcessorControlProps> = ({ onProcessingComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxEmails, setMaxEmails] = useState(10);
  const [categories, setCategories] = useState<string[]>(['primary']);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleCategoryChange = (category: string) => {
    if (categories.includes(category)) {
      setCategories(categories.filter(c => c !== category));
    } else {
      setCategories([...categories, category]);
    }
  };

  const runEmailProcessor = async () => {
    if (categories.length === 0) {
      setError('Please select at least one category');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('http://localhost:5000/run-email-processor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          categories,
          max_emails: maxEmails,
          start_date: startDate || null,
          end_date: endDate || null
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        onProcessingComplete(result);
      } else {
        setError(result.message || 'Failed to process emails');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <RefreshCw className="mr-2 h-5 w-5" /> Email Processor Controls
      </h2>
      
      <div className="space-y-6">
        {/* Basic Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Email Count Control */}
          <div>
            <label className="block mb-2 font-medium text-gray-700 flex items-center">
              <Hash className="mr-2 h-4 w-4" /> Number of Emails to Fetch
            </label>
            <div className="flex items-center">
              <input
                type="range"
                min="1"
                max="50"
                value={maxEmails}
                onChange={(e) => setMaxEmails(parseInt(e.target.value))}
                className="w-full h-2 bg-blue-100 rounded-lg appearance-none cursor-pointer"
              />
              <span className="ml-4 min-w-[2rem] text-center">{maxEmails}</span>
            </div>
          </div>
          
          {/* Category Selection */}
          <div>
            <label className="block mb-2 font-medium text-gray-700 flex items-center">
              <CheckSquare className="mr-2 h-4 w-4" /> Email Categories
            </label>
            <div className="flex flex-wrap gap-3">
              {['primary', 'promotions', 'social'].map(category => (
                <button
                  key={category}
                  onClick={() => handleCategoryChange(category)}
                  className={`px-3 py-1 rounded-full text-sm border ${
                    categories.includes(category)
                      ? 'bg-blue-50 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-500'
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        {/* Advanced Options Toggle */}
        <div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-blue-600 text-sm font-medium hover:text-blue-800"
          >
            {showAdvanced ? '▼ Hide Advanced Options' : '▶ Show Advanced Options'}
          </button>
        </div>
        
        {/* Advanced Controls */}
        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-gray-100">
            {/* Date Range Controls */}
            <div>
              <label className="block mb-2 font-medium text-gray-700 flex items-center">
                <Calendar className="mr-2 h-4 w-4" /> Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block mb-2 font-medium text-gray-700 flex items-center">
                <Calendar className="mr-2 h-4 w-4" /> End Date
              </label>
              <input
                type="date"
                value={endDate}
                min={startDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        )}
        
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm">
            {error}
          </div>
        )}
        
        {/* Run Button */}
        <div className="flex justify-end">
          <button
            onClick={runEmailProcessor}
            disabled={isLoading}
            className={`px-4 py-2 rounded-md font-medium flex items-center ${
              isLoading
                ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? (
              <>
                <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-5 w-5" />
                Fetch Emails
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailProcessorControl; 