'use client';

import React from 'react';
import SpamTestForm from '../../components/spam-test-form';

export default function SpamTestPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Spam Test Tool</h1>
        <p className="text-gray-600 mt-2">
          Use ChatGPT AI to analyze text and determine if it's likely to be spam.
        </p>
      </div>
      
      <div className="flex justify-center">
        <SpamTestForm />
      </div>
    </div>
  );
} 