import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ResumeForm from './components/ResumeForm';
import GeneratedResume from './components/GeneratedResume';

function App() {
  // State to track the current step of the process
  const [step, setStep] = useState(1);
  
  // State to hold the resume data - preserve throughout navigation
  const [resumeData, setResumeData] = useState(null);
  
  // State to track loading state
  const [loading, setLoading] = useState(false);
  
  // Handler for when resume data is extracted
  const handleResumeDataExtracted = (data) => {
    setResumeData(data);
    setStep(2); // Move to form editing step
  };
  
  // Handler for generating final resume
  const handleGenerateResume = (formData) => {
    setResumeData(formData);
    setStep(3); // Move to resume preview step
  };
  
  // Navigation handlers for top nav
  const navigateToStep = (targetStep) => {
    if (targetStep === 1) {
      setStep(1);
    } else if (targetStep === 2 && resumeData) {
      setStep(2);
    } else if (targetStep === 3 && resumeData) {
      setStep(3);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header with Logo and Company Info */}
      <header className="bg-ocean-dark shadow-lg">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img 
                src="/logo.png" 
                alt="OceanBlue Solutions Logo" 
                className="h-12 w-12 rounded-lg shadow-md"
              />
              <div>
                <h1 className="text-2xl font-bold text-white">OceanBlue Solutions</h1>
                <p className="text-ocean-blue text-sm font-medium">Resume Automation Tool</p>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Top Navigation Bar */}
      <nav className="bg-white shadow-md border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex justify-center overflow-x-auto">
            <div className="flex items-center py-6 min-w-max">
              {/* Step 1: Upload */}
              <button
                onClick={() => navigateToStep(1)}
                className={`flex items-center px-4 py-3 font-medium transition-all duration-300 text-sm ${
                  step === 1 
                    ? 'bg-ocean-blue text-white' 
                    : 'text-ocean-dark hover:bg-ocean-blue hover:text-white bg-gray-100'
                } rounded-l-lg border-2 border-ocean-blue`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-2 text-xs font-bold ${
                  step >= 1 ? 'bg-white text-ocean-blue' : 'bg-gray-300 text-gray-600'
                }`}>
                  1
                </div>
                <span className="whitespace-nowrap">Upload Resume</span>
              </button>
              
              {/* Connector */}
              <div className={`w-6 h-1 ${
                step >= 2 ? 'bg-ocean-blue' : 'bg-gray-300'
              }`}></div>
              
              {/* Step 2: Review & Edit */}
              <button
                onClick={() => navigateToStep(2)}
                disabled={!resumeData}
                className={`flex items-center px-4 py-3 font-medium transition-all duration-300 text-sm ${
                  step === 2 
                    ? 'bg-ocean-blue text-white' 
                    : resumeData 
                      ? 'text-ocean-dark hover:bg-ocean-blue hover:text-white bg-gray-100' 
                      : 'text-gray-400 bg-gray-50 cursor-not-allowed'
                } border-2 border-l-0 border-ocean-blue`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-2 text-xs font-bold ${
                  step >= 2 ? 'bg-white text-ocean-blue' : 'bg-gray-300 text-gray-600'
                }`}>
                  2
                </div>
                <span className="whitespace-nowrap">Review & Edit</span>
              </button>
              
              {/* Connector */}
              <div className={`w-6 h-1 ${
                step >= 3 ? 'bg-ocean-blue' : 'bg-gray-300'
              }`}></div>
              
              {/* Step 3: Generated Resume */}
              <button
                onClick={() => navigateToStep(3)}
                disabled={!resumeData}
                className={`flex items-center px-4 py-3 font-medium transition-all duration-300 text-sm ${
                  step === 3 
                    ? 'bg-ocean-blue text-white' 
                    : resumeData 
                      ? 'text-ocean-dark hover:bg-ocean-blue hover:text-white bg-gray-100' 
                      : 'text-gray-400 bg-gray-50 cursor-not-allowed'
                } rounded-r-lg border-2 border-l-0 border-ocean-blue`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-2 text-xs font-bold ${
                  step >= 3 ? 'bg-white text-ocean-blue' : 'bg-gray-300 text-gray-600'
                }`}>
                  3
                </div>
                <span className="whitespace-nowrap">Generated Resume</span>
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          {/* Content based on current step */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden animate-fade-in">
            {step === 1 && (
              <div className="p-8">
                <FileUpload 
                  onResumeDataExtracted={handleResumeDataExtracted}
                  setLoading={setLoading}
                />
              </div>
            )}
            
            {step === 2 && resumeData && (
              <div className="p-8">
                <ResumeForm 
                  initialData={resumeData}
                  onSubmit={handleGenerateResume}
                  onBack={() => setStep(1)}
                />
              </div>
            )}
            
            {step === 3 && resumeData && (
              <div className="p-8">
                <GeneratedResume 
                  resumeData={resumeData}
                  onBack={() => setStep(2)}
                />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;