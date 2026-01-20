import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiFileText, FiAlertCircle, FiLoader, FiFile } from 'react-icons/fi';

// API base URL - Use environment variable for production
const API_BASE_URL = process.env.REACT_APP_API_URL;

const FileUpload = ({ onResumeDataExtracted, setLoading }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  
  // Simple loading state
  const [isProcessing, setIsProcessing] = useState(false);

  // Handle file drop using react-dropzone
  const onDrop = useCallback((acceptedFiles) => {
    // Accept only the first file if multiple are uploaded
    const selectedFile = acceptedFiles[0];
    
    if (!selectedFile) return;
    
    // Validate file type
    const validTypes = ['.pdf', '.docx', '.txt'];
    const extension = '.' + selectedFile.name.split('.').pop().toLowerCase();
    
    // Check for DOC files specifically and reject with backend's error message
    if (extension === '.doc') {
      setError('DOC files are not currently supported. Please save your resume as a DOCX, PDF, or TXT file and try again.');
      return;
    }
    
    if (!validTypes.includes(extension)) {
      setError('Invalid file type. Please upload PDF, DOCX, or TXT files.');
      return;
    }
    
    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.');
      return;
    }
    
    // Clear any previous errors and set the file
    setError('');
    setFile(selectedFile);
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    },
    onDropRejected: (rejectedFiles) => {
      const docFile = rejectedFiles.find(file => 
        file.file.name.toLowerCase().endsWith('.doc')
      );
      if (docFile) {
        setError('DOC files are not currently supported. Please save your resume as a DOCX, PDF, or TXT file and try again.');
      }
    }
  });
  
  // 🚀 REVOLUTIONARY STREAMING UPLOAD FUNCTION
  const handleStreamingSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    
    // Reset state
    setIsProcessing(true);
    setLoading(true);
    setError('');
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Simple fetch to process resume
      const response = await fetch(`${API_BASE_URL}api/stream-resume-processing`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Read the stream for final result only
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { value, done } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        const events = buffer.split('\n\n');
        buffer = events.pop();
        
        for (const event of events) {
          if (event.startsWith('data: ')) {
            try {
              const eventData = event.slice(6);
              if (eventData === '[DONE]') continue;
              
              const data = JSON.parse(eventData);
              
              // Only handle final data and errors
              if (data.type === 'final_data') {
                const sanitizedData = sanitizeResumeData(data.data);
                onResumeDataExtracted(sanitizedData);
                return;
              } else if (data.type === 'error') {
                setError(data.message || 'Processing error');
                return;
              }
            } catch (parseError) {
              // Ignore parse errors
            }
          }
        }
      }
      
    } catch (processingError) {
      setError(`Processing failed: ${processingError.message}`);
    } finally {
      setIsProcessing(false);
      setLoading(false);
    }
  };
  

  
  // 🔧 DATA SANITIZATION FUNCTION
  const sanitizeResumeData = (data) => {
    
    try {
      const sanitized = {
        name: data.name || '',
        title: data.title || '',
        requisitionNumber: data.requisitionNumber || '',
        professionalSummary: Array.isArray(data.professionalSummary) ? data.professionalSummary : [],
        summarySections: Array.isArray(data.summarySections) ? data.summarySections : [],
        subsections: Array.isArray(data.subsections) ? data.subsections : [],
        employmentHistory: Array.isArray(data.employmentHistory) ? data.employmentHistory : [],
        education: Array.isArray(data.education) ? data.education : [],
        certifications: Array.isArray(data.certifications) ? data.certifications : [],
        technicalSkills: (data.technicalSkills && typeof data.technicalSkills === 'object') ? data.technicalSkills : {},
        skillCategories: Array.isArray(data.skillCategories) ? data.skillCategories : []
      };
      
      // Ensure employment history has proper structure
      sanitized.employmentHistory = sanitized.employmentHistory.map(job => ({
        companyName: job.companyName || '',
        roleName: job.roleName || '',
        workPeriod: job.workPeriod || '',
        location: job.location || '',
        responsibilities: Array.isArray(job.responsibilities) ? job.responsibilities : (job.responsibilities ? [job.responsibilities] : []),
        projects: Array.isArray(job.projects) ? job.projects.map(project => ({
          projectName: project.projectName || '',
          projectLocation: project.projectLocation || '',
          projectResponsibilities: Array.isArray(project.projectResponsibilities) ? project.projectResponsibilities : [],
          keyTechnologies: project.keyTechnologies || '',
          period: project.period || ''
        })) : [],
        subsections: Array.isArray(job.subsections) ? job.subsections.map(subsection => ({
          title: subsection.title || '',
          content: Array.isArray(subsection.content) ? subsection.content : []
        })) : [],
        keyTechnologies: job.keyTechnologies || ''
      }));
      
      // Ensure summary subsections have proper structure
      if (Array.isArray(data.summarySections)) {
        sanitized.summarySections = data.summarySections.map(subsection => ({
          title: subsection.title || '',
          content: Array.isArray(subsection.content) ? subsection.content : []
        }));
      } else if (Array.isArray(data.subsections)) {
        sanitized.summarySections = data.subsections.map(subsection => ({
          title: subsection.title || '',
          content: Array.isArray(subsection.content) ? subsection.content : []
        }));
        sanitized.subsections = sanitized.summarySections; // For compatibility
      }
      
      // Ensure skill categories have proper structure
      if (Array.isArray(data.skillCategories)) {
        sanitized.skillCategories = data.skillCategories.map(category => ({
          categoryName: category.categoryName || '',
          skills: Array.isArray(category.skills) ? category.skills : [],
          subCategories: Array.isArray(category.subCategories) ? category.subCategories.map(subCategory => ({
            name: subCategory.name || '',
            skills: Array.isArray(subCategory.skills) ? subCategory.skills : []
          })) : []
        }));
      }
      
      // Ensure education has proper structure
      sanitized.education = sanitized.education.map(edu => ({
        degree: edu.degree || '',
        areaOfStudy: edu.areaOfStudy || '',
        school: edu.school || '',
        location: edu.location || '',
        date: edu.date || '',
        wasAwarded: edu.wasAwarded !== undefined ? edu.wasAwarded : true
      }));
      
      // Ensure certifications have proper structure
      sanitized.certifications = sanitized.certifications.map(cert => ({
        name: cert.name || '',
        issuedBy: cert.issuedBy || '',
        dateObtained: cert.dateObtained || '',
        certificationNumber: cert.certificationNumber || '',
        expirationDate: cert.expirationDate || ''
      }));

      return sanitized;

    } catch (error) {
      
      // Return safe default structure
      return {
        name: '',
        title: '',
        requisitionNumber: '',
        professionalSummary: [],
        summarySections: [],
        subsections: [],
        employmentHistory: [],
        education: [],
        certifications: [],
        technicalSkills: {},
        skillCategories: []
      };
    }
  };

  
  return (
    <div className="max-w-4xl mx-auto animate-slide-up">
      {/* Header Section */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <FiFile className="text-6xl text-ocean-blue mr-4" />
          <div>
            <h2 className="text-3xl font-bold text-ocean-dark">Upload Resume</h2>
          </div>
        </div>
      </div>
      
      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 text-red-700 p-6 mb-8 rounded-lg shadow-md animate-fade-in">
          <div className="flex items-start">
            <FiAlertCircle className="mt-1 mr-3 text-xl flex-shrink-0" />
            <div>
              <h4 className="font-semibold mb-1">Upload Error</h4>
              <span>{error}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* File Drop Zone */}
      <div 
        {...getRootProps()} 
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 transform hover:scale-105 mb-8 ${
          isDragActive 
            ? 'border-ocean-blue bg-blue-50 shadow-lg' 
            : 'border-gray-300 hover:border-ocean-blue hover:bg-blue-50'
        }`}
      >
        <input {...getInputProps()} />
        
        {/* Upload Icon and Animation */}
        <div className="mb-6">
          <FiUpload className={`mx-auto text-6xl transition-all duration-300 ${
            isDragActive ? 'text-ocean-blue animate-bounce' : 'text-gray-400'
          }`} />
        </div>
        
        {/* Upload Text */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-ocean-dark">
            {isDragActive ? 'Drop resume here' : 'Drag & drop resume here'}
          </h3>
          <p className="text-gray-600">
            or click to select file
          </p>
          <div className="flex items-center justify-center space-x-4 mt-4">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">PDF</span>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">DOCX</span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">TXT</span>
          </div>
          <p className="text-xs text-red-500 mt-2 font-medium">
            ⚠️ DOC files are not supported
          </p>
        </div>
        
        {/* File Size Limit */}
        <div className="mt-6 text-sm text-gray-500">
          Maximum file size: 10MB
        </div>
      </div>
      
      {/* Selected File Display */}
      {file && (
        <div className="bg-gradient-to-r from-ocean-dark to-ocean-blue rounded-xl p-6 mb-8 text-white shadow-lg animate-fade-in">
          <div className="flex items-center">
            <FiFileText className="text-3xl mr-4" />
            <div className="flex-1">
              <h4 className="font-semibold text-lg">{file.name}</h4>
              <p className="text-blue-200">
                {(file.size / 1024 / 1024).toFixed(2)} MB • Ready for processing
              </p>
            </div>
            <div className="text-right">
              <div className="bg-white bg-opacity-20 rounded-lg px-3 py-1">
                <span className="text-sm font-medium">Selected ✓</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Simple Loading Interface */}
      {isProcessing && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-ocean-blue rounded-2xl p-8 mb-8 shadow-xl animate-fade-in">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <FiLoader className="animate-spin text-4xl text-ocean-blue mr-4" />
              <h3 className="text-2xl font-bold text-ocean-dark">Processing Resume...</h3>
            </div>
            <p className="text-ocean-blue font-medium">Please wait while we analyze your resume</p>
          </div>
        </div>
      )}
      
      {/* Process Button */}
      <div className="flex justify-center">
        <button 
          onClick={handleStreamingSubmit}
          disabled={!file || isProcessing}
          className={`px-8 py-4 rounded-xl text-white font-semibold text-lg flex items-center transition-all duration-300 transform hover:scale-105 ${
            file && !isProcessing 
              ? 'bg-gradient-to-r from-ocean-blue to-blue-500 hover:from-blue-600 hover:to-blue-700 shadow-lg' 
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          {isProcessing ? (
            <>
              <FiLoader className="animate-spin mr-3 text-xl" />
              Processing...
            </>
          ) : (
            <>
              <FiUpload className="mr-3 text-xl" />
              Process Resume
            </>
          )}
        </button>
      </div>
      
    </div>
  );
};

export default FileUpload; 
