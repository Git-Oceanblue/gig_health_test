# Resume Builder Project Flow Diagram

## System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[User Browser] --> B[React Frontend App]
        B --> C[FileUpload Component]
        B --> D[ResumeForm Component]
        B --> E[GeneratedResume Component]
    end

    subgraph "Frontend Processing"
        C --> G[File Validation<br/>PDF/DOCX/TXT]
        G --> H[Drag & Drop Interface]
        H --> I[Server-Sent Events<br/>Streaming]
    end

    subgraph "AWS Infrastructure"
        J[CloudFront CDN] --> K[S3 Bucket<br/>Static Website Hosting]
        L[Lambda Function URL] --> M[AWS Lambda<br/>Python Runtime]
        N[CloudWatch Logs] --> M
        O[IAM Roles] --> M
    end

    subgraph "Backend Processing"
        M --> P[FastAPI Application]
        P --> Q[File Parser<br/>PyMuPDF + docx2python]
        Q --> R[Multi-Agent AI System]
        R --> S[OpenAI GPT-4o-mini API]
        S --> T[6 Specialized Agents<br/>Parallel Processing]
    end

    subgraph "AI Agent Pipeline"
        T --> U[Header Agent<br/>Personal Info]
        T --> V[Summary Agent<br/>Professional Summary]
        T --> W[Experience Agent<br/>Employment + Projects]
        T --> X[Education Agent<br/>Academic Background]
        T --> Y[Skills Agent<br/>Technical Skills]
        T --> Z[Certifications Agent<br/>Professional Credentials]
    end

    subgraph "Data Processing & Validation"
        U --> AA[Data Normalization<br/>Dates, Locations, Degrees]
        V --> AA
        W --> AA
        X --> AA
        Y --> AA
        Z --> AA
        AA --> BB[Structured JSON Output]
    end

    subgraph "Output Generation"
        BB --> CC[Resume Preview<br/>React Components]
        BB --> DD[Word Document<br/>DOCX Generation]
        BB --> EE[Print Layout<br/>CSS Print Styles]
        CC --> FF[User Downloads]
        DD --> FF
        EE --> FF
    end

    %% Connections
    I --> L
    B --> J
    P --> S
    BB --> B
    FF --> A

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef aws fill:#fff3e0
    classDef ai fill:#e8f5e8
    classDef output fill:#fce4ec

    class A,B,C,D,E,G,H,I frontend
    class P,Q,R,AA,BB backend
    class J,K,L,M,N,O aws
    class S,T,U,V,W,X,Y,Z ai
    class CC,DD,EE,FF output
```

## Detailed Multi-Agent Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant L as Lambda
    participant FP as File Parser
    participant MA as Multi-Agent System
    participant H as Header Agent
    participant S as Summary Agent
    participant E as Experience Agent
    participant ED as Education Agent
    participant SK as Skills Agent
    participant C as Certifications Agent
    participant AI as OpenAI API

    U->>F: Upload Resume File
    F->>F: Validate File (PDF/DOCX/TXT)
    F->>L: POST /api/stream-resume-processing
    L->>FP: Extract Text from File
    FP->>FP: Parse with PyMuPDF/docx2python
    FP-->>L: Return Raw Text
    L->>MA: Initialize Multi-Agent Processing
    
    par Parallel Agent Processing
        MA->>H: Extract Personal Info
        H->>AI: Process with Function Schema
        AI-->>H: Return Header Data
        and
        MA->>S: Extract Professional Summary
        S->>AI: Process with Function Schema
        AI-->>S: Return Summary Data
        and
        MA->>E: Extract Employment History
        E->>AI: Process with Function Schema
        AI-->>E: Return Experience Data
        and
        MA->>ED: Extract Education
        ED->>AI: Process with Function Schema
        AI-->>ED: Return Education Data
        and
        MA->>SK: Extract Technical Skills
        SK->>AI: Process with Function Schema
        AI-->>SK: Return Skills Data
        and
        MA->>C: Extract Certifications
        C->>AI: Process with Function Schema
        AI-->>C: Return Certifications Data
    end
    
    MA->>MA: Combine & Normalize All Data
    MA-->>L: Return Structured JSON
    L-->>F: Stream Final Result (SSE)
    F->>F: Display Extracted Data
    U->>F: Review & Edit Data
    F->>F: Generate Word Document
    F->>U: Download Resume
```

## Infrastructure Components

```mermaid
graph LR
    subgraph "AWS Cloud Infrastructure"
        subgraph "Frontend Hosting"
            A[CloudFront Distribution] --> B[S3 Bucket<br/>Static Website]
            A --> C[Origin Access Control]
        end
        
        subgraph "Backend Processing"
            D[Lambda Function] --> E[Function URL]
            D --> F[CloudWatch Logs]
            D --> G[IAM Role & Policies]
        end
        
        subgraph "External Services"
            H[OpenAI API] --> D
        end
        
        subgraph "Terraform Management"
            I[Terraform State<br/>S3 Backend] --> J[Infrastructure as Code]
            J --> A
            J --> D
        end
    end

    subgraph "Development Environment"
        K[React Development Server] --> L[Local Testing]
        M[Python Backend] --> N[Local API Testing]
    end

    %% Styling
    classDef aws fill:#ff9800,color:#fff
    classDef dev fill:#2196f3,color:#fff
    classDef external fill:#4caf50,color:#fff

    class A,B,C,D,E,F,G,I,J aws
    class K,L,M,N dev
    class H external
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Input Processing"
        A[Resume File Upload] --> B[File Type Detection]
        B --> C[Text Extraction]
        C --> D[Content Sanitization]
    end

    subgraph "AI Processing Pipeline"
        D --> E[Section Detection]
        E --> F[Professional Summary<br/>Extraction]
        E --> G[Employment History<br/>Extraction]
        E --> H[Education<br/>Extraction]
        E --> I[Certifications<br/>Extraction]
        E --> J[Skills<br/>Extraction]
    end

    subgraph "Data Structuring"
        F --> K[Structured JSON]
        G --> K
        H --> K
        I --> K
        J --> K
        K --> L[Data Validation]
        L --> M[Clean Data Output]
    end

    subgraph "Output Generation"
        M --> N[Resume Preview]
        M --> O[Word Document]
        M --> P[Print Layout]
        N --> Q[User Download]
        O --> Q
        P --> Q
    end

    %% Styling
    classDef input fill:#e3f2fd
    classDef ai fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef output fill:#fce4ec

    class A,B,C,D input
    class E,F,G,H,I,J ai
    class K,L,M data
    class N,O,P,Q output
```

## Key Features & Technologies

### Frontend (React + Tailwind CSS)
- **FileUpload Component**: 
  - Drag & drop interface with react-dropzone
  - File validation (PDF/DOCX/TXT, max 10MB)
  - DOC file rejection with clear messaging
  - Server-sent events streaming for real-time progress
- **ResumeForm Component**: 
  - Comprehensive editing interface for all resume sections
  - Dynamic form fields with add/remove functionality
  - Nested structure support (projects, subsections, skill categories)
  - Real-time data validation and sanitization
- **GeneratedResume Component**: 
  - Live resume preview with professional styling
  - Word document generation using docx library
  - Print functionality with CSS print styles
  - Download options for multiple formats

### Backend (FastAPI + Python)
- **File Parser Module**: 
  - PyMuPDF for PDF text extraction
  - docx2python for DOCX processing
  - Plain text file support
  - Robust error handling and cleanup
- **Multi-Agent AI System**: 
  - 6 specialized agents for parallel processing
  - OpenAI GPT-4o-mini with function calling
  - Cache-busting for fresh AI responses
  - Intelligent chunking and section detection
- **Data Normalization**: 
  - Date format standardization (MMM YYYY)
  - Location format normalization (City, State)
  - Degree standardization (BS, MS, PhD)
  - Work period normalization with "to" → "-" conversion
- **Token Management**: 
  - Cost tracking and usage analytics
  - Efficient prompt engineering
  - Processing time monitoring

### Infrastructure (AWS + Terraform)
- **S3 Static Website Hosting**: 
  - CloudFront CDN distribution
  - Origin Access Control for security
  - Custom error pages for SPA routing
- **Lambda Serverless Backend**: 
  - Function URL for direct API access
  - 5-minute timeout for complex processing
  - Automatic scaling and cost optimization
- **Infrastructure as Code**: 
  - Terraform modules for reusable components
  - Environment-specific deployments
  - S3 backend for state management
- **CI/CD Pipeline**: 
  - GitHub Actions for automated deployment
  - Docker-based Lambda packaging
  - Automatic frontend build and deployment

### AI Processing Architecture
- **Specialized Agents**: 
  - Header Agent: Personal information extraction
  - Summary Agent: Professional summary with subsections
  - Experience Agent: Employment history with projects
  - Education Agent: Academic background with sorting
  - Skills Agent: Technical skills with hierarchical structure
  - Certifications Agent: Professional credentials
- **Advanced Features**: 
  - Parallel agent execution for speed
  - Hierarchical skills structure preservation
  - Project vs job-level content differentiation
  - Comprehensive data validation and cleaning

## Detailed Project Structure

```
ob-resume-builder-test/
├── frontend/                           # React SPA with Tailwind CSS
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.js          # Drag & drop file upload with streaming
│   │   │   ├── ResumeForm.js          # Comprehensive resume editing interface
│   │   │   └── GeneratedResume.js     # Preview & Word document generation
│   │   ├── App.js                     # Main application with 3-step wizard
│   │   ├── index.js                   # React app entry point
│   │   └── index.css                  # Tailwind CSS imports
│   ├── public/
│   │   ├── index.html                 # HTML template
│   │   └── logo.png                   # OceanBlue Solutions logo
│   ├── package.json                   # Dependencies & build scripts
│   ├── tailwind.config.js             # Tailwind configuration
│   └── postcss.config.js              # PostCSS configuration
├── backend/                            # Python FastAPI backend
│   ├── utils/
│   │   ├── file_parser.py             # PDF/DOCX/TXT text extraction
│   │   ├── ai_parser.py               # Multi-agent orchestration
│   │   ├── resume_agents.py           # 6 specialized AI agents
│   │   ├── agent_schemas.py           # OpenAI function schemas
│   │   ├── chunk_resume.py            # Resume section detection
│   │   └── token_logger.py            # Cost tracking & analytics
│   ├── main.py                        # FastAPI application
│   ├── lambda_handler.py              # AWS Lambda wrapper (Mangum)
│   └── requirements.txt               # Python dependencies
├── terraform/                          # Infrastructure as Code
│   ├── modules/
│   │   ├── s3/                        # S3 static website hosting
│   │   ├── cloudfront/                # CDN distribution
│   │   └── lambda/                    # Serverless backend
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Input variables
│   └── outputs.tf                     # Output values
├── .github/workflows/
│   └── deploy.yml                     # CI/CD pipeline
├── .gitignore                         # Git ignore rules
├── setup.md                           # Setup instructions
└── project-flow-diagram.md           # This documentation
```

## Advanced Technical Implementation Details

### Multi-Agent AI Architecture
The system employs a sophisticated multi-agent approach where 6 specialized AI agents process different resume sections in parallel:

1. **Header Agent**: Extracts personal information (name, title, requisition number)
2. **Summary Agent**: Processes professional summary with nested subsections
3. **Experience Agent**: Handles employment history with intelligent project detection
4. **Education Agent**: Manages academic background with degree standardization
5. **Skills Agent**: Preserves hierarchical technical skills structure
6. **Certifications Agent**: Extracts professional credentials and licenses

### Data Normalization Pipeline
- **Date Standardization**: Converts all dates to "MMM YYYY" format
- **Location Formatting**: Standardizes to "City, State/Country" format
- **Degree Mapping**: Normalizes degrees (BTech→BS, MTech→MS, etc.)
- **Work Period Cleaning**: Handles em-dash, en-dash, and "to" conversions
- **Hierarchical Structure Preservation**: Maintains nested skills and subsections

### Performance Optimizations
- **Parallel Processing**: All 6 agents run simultaneously
- **Cache Busting**: Prevents OpenAI response caching for fresh results
- **Streaming Responses**: Real-time progress updates via Server-Sent Events
- **Token Optimization**: Cost-effective prompt engineering
- **Serverless Scaling**: Automatic Lambda scaling based on demand

This enterprise-grade resume builder demonstrates modern cloud-native architecture, combining React frontend, Python backend, multi-agent AI processing, and AWS infrastructure to deliver intelligent resume parsing and generation capabilities.
