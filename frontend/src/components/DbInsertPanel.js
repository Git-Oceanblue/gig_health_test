import React, { useState, useEffect } from 'react';
import { FiDatabase, FiAlertCircle, FiCheckCircle, FiLoader } from 'react-icons/fi';

// API base URL - Use environment variable for production
const API_BASE_URL = process.env.REACT_APP_API_URL;

const DbInsertPanel = ({ resumeData }) => {
  const [tableName, setTableName] = useState('');
  const [columns, setColumns] = useState([]);
  const [editableData, setEditableData] = useState({});
  const [loading, setLoading] = useState(true);
  const [inserting, setInserting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch table metadata on component mount
  useEffect(() => {
    const fetchTableMetadata = async () => {
      try {
        setLoading(true);
        setError('');
        
        // POST resume data to get table metadata based on data keys
        const response = await fetch(`${API_BASE_URL}/api/db/table-metadata`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            resumeData: resumeData
          })
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch table metadata: ${response.statusText}`);
        }
        
        const data = await response.json();
        setTableName(data.tableName);
        setColumns(data.columns);
        
        // Initialize editable data with resumeData values
        const initialData = {};
        data.columns.forEach(col => {
          initialData[col] = getValueFromResumeData(col);
        });
        setEditableData(initialData);
        
        setLoading(false);
      } catch (err) {
        console.error('❌ Error fetching table metadata:', err);
        setError(`Error loading table metadata: ${err.message}`);
        setLoading(false);
      }
    };

    if (resumeData) {
      fetchTableMetadata();
    }
  }, [resumeData]);

  // Helper function to map resumeData fields to database columns
  const getValueFromResumeData = (columnName) => {
    if (!resumeData) return '';

    const mappings = {
      name: resumeData.name || '',
      title: resumeData.title || '',
      requisitionNumber: resumeData.requisitionNumber || '',
      professionalSummary: Array.isArray(resumeData.professionalSummary) 
        ? resumeData.professionalSummary.join('\n') 
        : resumeData.professionalSummary || '',
      employmentHistory: resumeData.employmentHistory 
        ? JSON.stringify(resumeData.employmentHistory) 
        : '',
      education: resumeData.education 
        ? JSON.stringify(resumeData.education) 
        : '',
      technicalSkills: Array.isArray(resumeData.technicalSkills)
        ? resumeData.technicalSkills.join(', ')
        : resumeData.technicalSkills || '',
      skillCategories: resumeData.skillCategories 
        ? JSON.stringify(resumeData.skillCategories) 
        : '',
      certifications: resumeData.certifications 
        ? JSON.stringify(resumeData.certifications) 
        : '',
      summarySections: resumeData.summarySections 
        ? JSON.stringify(resumeData.summarySections) 
        : '',
      tokenStats: resumeData.tokenStats 
        ? JSON.stringify(resumeData.tokenStats) 
        : ''
    };

    return mappings[columnName] || '';
  };

  // Handle field changes
  const handleFieldChange = (columnName, value) => {
    setEditableData({
      ...editableData,
      [columnName]: value
    });
    setError('');
  };

  // Handle database insertion
  const handleInsertToDb = async (e) => {
    e.preventDefault();
    
    try {
      setInserting(true);
      setError('');
      setSuccess('');

      // Parse JSON fields if they contain valid JSON
      const dataToInsert = { ...editableData };
      const jsonFields = ['employmentHistory', 'education', 'skillCategories', 'certifications', 'summarySections', 'tokenStats'];
      
      jsonFields.forEach(field => {
        if (dataToInsert[field] && typeof dataToInsert[field] === 'string') {
          try {
            dataToInsert[field] = JSON.parse(dataToInsert[field]);
          } catch (e) {
            // Keep as string if parsing fails
            console.warn(`⚠️ Could not parse JSON for field ${field}`);
          }
        }
      });

      const response = await fetch(`${API_BASE_URL}/api/db/insert-resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tableName: tableName,
          data: dataToInsert
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || `Failed to insert data: ${response.statusText}`);
      }

      setSuccess(result.message || 'Data inserted successfully into the database!');
      setInserting(false);

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      console.error('❌ Error inserting data:', err);
      setError(`Error inserting data: ${err.message}`);
      setInserting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <FiLoader className="w-8 h-8 text-ocean-blue animate-spin mr-3" />
        <span className="text-ocean-dark font-medium">Loading table metadata...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <FiDatabase className="w-6 h-6 text-ocean-blue" />
        <div>
          <h2 className="text-2xl font-bold text-ocean-dark">Database Insertion</h2>
          <p className="text-sm text-gray-600">Insert resume data into: <span className="font-semibold text-ocean-blue">{tableName}</span></p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
          <FiAlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-sm text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-3">
          <FiCheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-green-900">Success</h3>
            <p className="text-sm text-green-800">{success}</p>
          </div>
        </div>
      )}

      {/* Editable Fields Form */}
      <form onSubmit={handleInsertToDb} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {columns.map((column) => (
            <div key={column} className="flex flex-col">
              <label className="text-sm font-semibold text-ocean-dark mb-2 capitalize">
                {column.replace(/([A-Z])/g, ' $1').trim()}
              </label>
              {editableData[column] && editableData[column].includes('\n') ? (
                // Textarea for multi-line fields
                <textarea
                  value={editableData[column]}
                  onChange={(e) => handleFieldChange(column, e.target.value)}
                  className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-blue focus:border-transparent resize-none"
                  rows={4}
                  placeholder={`Enter ${column}`}
                />
              ) : (
                // Input for single-line fields
                <input
                  type="text"
                  value={editableData[column]}
                  onChange={(e) => handleFieldChange(column, e.target.value)}
                  className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-blue focus:border-transparent"
                  placeholder={`Enter ${column}`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Insert Button */}
        <div className="flex gap-3 pt-6 border-t border-gray-200">
          <button
            type="submit"
            disabled={inserting}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center space-x-2 ${
              inserting
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-ocean-blue text-white hover:bg-ocean-dark shadow-md hover:shadow-lg'
            }`}
          >
            {inserting ? (
              <>
                <FiLoader className="w-5 h-5 animate-spin" />
                <span>Inserting...</span>
              </>
            ) : (
              <>
                <FiDatabase className="w-5 h-5" />
                <span>Insert to Database</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">ℹ️ Info:</span> All fields are pre-populated with data from your resume. You can edit any field before inserting to the database.
        </p>
      </div>
    </div>
  );
};

export default DbInsertPanel;
