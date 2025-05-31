import React, { useState } from 'react';
import { AlertCircle, CheckCircle, SendHorizonal, Loader2 } from 'lucide-react';

const SpamTestForm: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const response = await fetch('http://localhost:5000/test-spam', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 w-full max-w-3xl">
      <h2 className="text-2xl font-bold mb-4">Test Text for Spam</h2>
      <p className="mb-4 text-gray-600">
        Enter text to analyze for spam using ChatGPT AI.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <textarea
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={6}
            placeholder="Enter text to analyze for spam..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <SendHorizonal className="w-5 h-5 mr-2" />
              Analyze Text
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-start">
          <AlertCircle className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">Analysis Result:</h3>
          <div className={`p-4 rounded-md ${result.is_spam ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
            <div className="flex items-center mb-3">
              {result.is_spam ? (
                <AlertCircle className="w-6 h-6 mr-2 text-red-500" />
              ) : (
                <CheckCircle className="w-6 h-6 mr-2 text-green-500" />
              )}
              <span className="font-bold text-lg">
                {result.is_spam ? 'Spam Detected' : 'Not Spam'}
              </span>
            </div>
            <div className="text-gray-700 whitespace-pre-line">
              <p className="font-semibold mb-2">AI Analysis:</p>
              <p>{result.analysis}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpamTestForm; 