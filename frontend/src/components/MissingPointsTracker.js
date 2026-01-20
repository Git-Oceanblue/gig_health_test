import React from 'react';
import { FiAlertCircle, FiCheckCircle } from 'react-icons/fi';

const MissingPointsTracker = ({ missingPoints }) => {
  if (!missingPoints) {
    return null;
  }

  const summaryCount = missingPoints.summary ? missingPoints.summary.length : 0;
  const experienceCount = missingPoints.experience ? missingPoints.experience.length : 0;
  const clientProjectsCount = missingPoints.clientProjects ? missingPoints.clientProjects.length : 0;
  const totalCount = summaryCount + experienceCount + clientProjectsCount;
  
  // If all counts are zero, show a success message instead
  if (totalCount === 0) {
    return (
      <div className="fixed right-0 top-20 w-80 bg-white shadow-lg rounded-l-lg p-4 border-l-4 border-green-500 max-h-[80vh] overflow-y-auto">
        <h3 className="text-lg font-semibold flex items-center text-green-700 mb-3">
          <FiCheckCircle className="mr-2" /> Content Analysis
        </h3>
        
        <div className="mb-4">
          <h4 className="font-medium text-gray-700 mb-2">Professional Summary (0 points missed)</h4>
          <p className="text-sm text-green-600">All summary points included! ✓</p>
        </div>
        
        <div className="mb-4">
          <h4 className="font-medium text-gray-700 mb-2">Work Experience (0 points missed)</h4>
          <p className="text-sm text-green-600">All experience points included! ✓</p>
        </div>
        
        <div className="mt-4 text-xs text-gray-500">
          All detected points from your resume were successfully included in the AI-generated data.
        </div>
      </div>
    );
  }

  // Original behavior for when there are missing points
  return (
    <div className="fixed right-0 top-20 w-80 bg-white shadow-lg rounded-l-lg p-4 border-l-4 border-yellow-500 max-h-[80vh] overflow-y-auto">
      <h3 className="text-lg font-semibold flex items-center text-yellow-700 mb-3">
        <FiAlertCircle className="mr-2" /> Missing Content
      </h3>
      
      {missingPoints.summary && missingPoints.summary.length > 0 && (
        <div className="mb-4">
          <h4 className="font-medium text-gray-700 mb-2">Professional Summary ({missingPoints.summary.length} points missed)</h4>
          <ul className="list-disc pl-5 text-sm">
            {missingPoints.summary.map((point, index) => (
              <li key={`summary-${index}`} className="mb-2 text-gray-600">{point}</li>
            ))}
          </ul>
        </div>
      )}
      
      {missingPoints.experience && missingPoints.experience.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Work Experience ({missingPoints.experience.length} points missed)</h4>
          <ul className="list-disc pl-5 text-sm">
            {missingPoints.experience.map((point, index) => (
              <li key={`exp-${index}`} className="mb-2 text-gray-600">{point}</li>
            ))}
          </ul>
        </div>
      )}
      
      {missingPoints.clientProjects && missingPoints.clientProjects.length > 0 && (
        <div className="mt-4">
          <h4 className="font-medium text-gray-700 mb-2">Client Projects ({missingPoints.clientProjects.length} points missed)</h4>
          <ul className="list-disc pl-5 text-sm">
            {missingPoints.clientProjects.map((point, index) => (
              <li key={`client-${index}`} className="mb-2 text-gray-600">{point}</li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="mt-4 text-xs text-gray-500">
        These points were detected in the resume but not included in the AI-generated data.
      </div>
    </div>
  );
};

export default MissingPointsTracker; 