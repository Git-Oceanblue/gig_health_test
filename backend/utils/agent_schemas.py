"""
Agent Schema Definitions for Resume Processing
Modular, maintainable function schemas for specialized AI agents
"""

from typing import Dict, Any

class ResumeAgentSchemas:
    """
    Centralized schema definitions for resume processing agents.
    Each schema is focused on a specific resume section for optimal extraction.
    """
    
    @staticmethod
    def get_header_agent_schema() -> Dict[str, Any]:
        """Schema for extracting personal information and header details"""
        return {
            "name": "extract_header_info",
            "description": "Extract personal information and header details from resume",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person"
                    },
                    "title": {
                        "type": "string",
                        "description": "Professional title of the person"
                    },
                    "requisitionNumber": {
                        "type": "string",
                        "description": "Requisition number if mentioned in the resume"
                    }
                },
                "required": ["name"]
            }
        }
    
    @staticmethod
    def get_summary_agent_schema() -> Dict[str, Any]:
        """Schema for extracting professional summary and overview sections"""
        return {
            "name": "extract_professional_summary",
            "description": "Extract professional summary, career overview, and profile sections",
            "parameters": {
                "type": "object",
                "properties": {
                    "professionalSummary": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of professional summary paragraphs and bullet points exactly as written. Each paragraph or bullet point should be a separate array item. Include EVERY point without exception."
                    },
                    "summarySections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "The title of the subsection, only include explicitly labeled subsections"},
                                "content": {"type": "array", "items": {"type": "string"}, "description": "Bullet points or paragraphs within this subsection"}
                            }
                        },
                        "description": "Only include explicitly labeled subsections with clear titles"
                    }
                },
                "required": ["professionalSummary"]
            }
        }
    
    @staticmethod
    def get_experience_agent_schema() -> Dict[str, Any]:
        """Schema for extracting employment history and work experience"""
        return {
            "name": "extract_employment_history",
            "description": "Extract complete employment history with all job details",
            "parameters": {
                "type": "object",
                "properties": {
                    "employmentHistory": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "companyName": {"type": "string", "description": "Name of the company. If clients are mentioned, format as 'CompanyName (Client1, Client2, Client3)' with all client names separated by commas"},
                                "roleName": {"type": "string", "description": "Job title or role"},
                                "workPeriod": {
                                    "type": "string",
                                    "pattern": "^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{4} - (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{4}$|^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d{4} - Till Date$",
                                    "description": "MANDATORY 3-LETTER MONTH FORMAT: NEVER use full month names like 'January', 'February', etc. ALWAYS use ONLY 3-letter abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec. Format: 'MMM YYYY - MMM YYYY' or 'MMM YYYY - Till Date'. Use regular hyphen (-) with single spaces. EXAMPLES: 'Jun 2024 - Sep 2025', 'Mar 2023 - Till Date'. FORBIDDEN: 'January 2024', 'February 2025', 'Sept 2024'."
                                },
                                "location": {
                                    "type": "string",
                                    "pattern": "^[A-Za-z\\s]+, [A-Za-z\\s]+$",
                                    "description": "CRITICAL LOCATION FORMAT RULES - EXACT FORMAT REQUIRED: Use format 'City, State/Country' with COMMA and SINGLE SPACE. For US locations, use 2-letter state abbreviations (TX, CA, NY, FL, etc.). For international locations, use full country names. CORRECT EXAMPLES: 'Dallas, TX' (US with state abbreviation), 'New York, NY' (US with state abbreviation), 'Hyderabad, India' (international with full country), 'London, UK' (international with country code), 'Toronto, Canada' (international with full country). The format MUST include: City name + comma + single space + State abbreviation or Country name. Never use full state names for US locations."
                                },

                                "projects": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "projectName": {"type": "string", "description": "Format as 'Project N: ProjectTitle/ Role' where N is descending number (Project 5, Project 4, etc.) with most recent project having highest number. Example: 'Project 4: RWE Datacenter-Transition/ Senior Database Administrator'"},
                                            "projectLocation": {"type": "string", "description": "Location where this specific project was performed, if explicitly mentioned. Use same format as job location: 'City, State/Country'. Only include if project location is different from or specifically mentioned for this project."},
                                            "projectResponsibilities": {"type": "array", "items": {"type": "string"}, "description": "List of responsibilities and achievements specific to this project"},
                                            "keyTechnologies": {"type": "string", "description": "Technologies, tools, and skills used in this specific project"},
                                            "period": {"type": "string", "description": "MANDATORY 3-LETTER MONTH FORMAT: Use ONLY 3-letter abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec. Format: 'MMM YYYY - MMM YYYY' with regular hyphen (-). NEVER use full month names. EXAMPLES: 'Jun 2024 - Sep 2024', 'Mar 2023 - Till Date'."}
                                        }
                                    },
                                    "description": "CRITICAL: ONLY include this field if the resume explicitly mentions specific named projects for this job. If no projects are mentioned, return an empty array []. DO NOT create or invent projects. Look for clear project names, project titles, or project-specific sections in that specific job entry."
                                },
                                "responsibilities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "CRITICAL: If projects exist for this job, leave this array EMPTY. Only include responsibilities when NO projects are mentioned for this job. When projects exist, all work details should be captured in project-specific fields instead."
                                },
                                "keyTechnologies": {"type": "string", "description": "CRITICAL: If projects exist for this job, leave this field EMPTY. Only include technologies when NO projects are mentioned for this job. When projects exist, all technologies should be captured in project-specific fields instead."},
                                "subsections": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "content": {"type": "array", "items": {"type": "string"}}
                                        }
                                    },
                                    "description": "Only include explicitly labeled subsections within this job. Do not create artificial subsections from standalone bullet points."
                                }
                            }
                        },
                        "description": "MANDATORY: Complete employment history with ALL jobs and details preserved exactly as written. Every single job entry MUST be included - missing even one job is unacceptable."
                    }
                },
                "required": ["employmentHistory"]
            }
        }
    
    @staticmethod
    def get_education_agent_schema() -> Dict[str, Any]:
        """Schema for extracting education and academic background"""
        return {
            "name": "extract_education_history",
            "description": "Extract complete education history and academic qualifications with mandatory degree standardization and proper sorting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "degree": {
                                    "type": "string", 
                                    "description": "MANDATORY DEGREE STANDARDIZATION - Convert degrees to standard abbreviations: BTech/BE/BCom/BA/Bachelor → 'BS', MTech/ME/Master → 'MS', MBA → 'MBA', MA → 'MA', MCom → 'MCom', PhD/Doctorate → 'PhD', JD → 'JD', AA → 'AA', AS → 'AS'. EXAMPLES: 'Bachelor of Technology' → 'BS', 'B.Tech' → 'BS', 'Master of Technology' → 'MS', 'M.Tech' → 'MS'."
                                },
                                "areaOfStudy": {"type": "string", "description": "Field of study or major"},
                                "school": {"type": "string", "description": "Educational institution name ONLY - exclude location information"},
                                "location": {
                                    "type": "string",
                                    "pattern": "^[A-Za-z\\s]+, [A-Za-z\\s]+$",
                                    "description": "CRITICAL LOCATION FORMAT RULES - EXACT FORMAT REQUIRED: Use format 'City, State/Country' with COMMA and SINGLE SPACE. For US locations, use 2-letter state abbreviations (TX, CA, NY, FL, etc.). For international locations, use full country names. CORRECT EXAMPLES: 'Austin, TX' (US with state abbreviation), 'Boston, MA' (US with state abbreviation), 'Mumbai, India' (international with full country). Extract separately even if combined with school name. The format MUST include: City name + comma + single space + State abbreviation or Country name."
                                },
                                "date": {"type": "string", "description": "Date of graduation or study period"},
                                "wasAwarded": {"type": "boolean", "description": "Whether the degree was awarded it must be always 'yes', unless it is mentioned as 'no'"}
                            }
                        },
                        "description": "CRITICAL REQUIREMENTS: 1) MANDATORY SORTING: Education entries MUST be sorted in ASCENDING order by degree level (lowest degree first). Exact order: AA/AS (lowest) → BS (bachelors) → MS/MA/MBA/MCom (masters) → PhD/JD (highest). If multiple degrees of same level, sort by date (oldest first). 2) MANDATORY STANDARDIZATION: All bachelor's degrees (BTech/BE/BCom/BA/Bachelor) MUST become 'BS'. All technical master's degrees (MTech/ME/Master) MUST become 'MS'. Keep MBA, MA, MCom, PhD, JD, AA, AS as-is. NO EXCEPTIONS."
                    }
                },
                "required": ["education"]
            }
        }
    
    @staticmethod
    def get_skills_agent_schema() -> Dict[str, Any]:
        """Schema for extracting technical skills and competencies"""
        return {
            "name": "extract_technical_skills",
            "description": "Extract technical skills, competencies, and skill categories with MANDATORY hierarchical structure preservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "technicalSkills": {
                        "type": "object",
                        "description": "Technical skills grouped by categories exactly as shown in resume"
                    },
                    "skillCategories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "categoryName": {"type": "string"},
                                "skills": {"type": "array", "items": {"type": "string"}},
                                "subCategories": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "skills": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                }
                            }
                        },
                        "description": "MANDATORY: Preserve hierarchical structure exactly as written. When skills are grouped under main headings, create nested structure: main heading becomes categoryName, items under it become subCategories. Never create separate categories for items that belong under a main heading. Maintain parent-child relationships as they appear in the resume text."
                    }
                },
                "required": []
            }
        }
    
    @staticmethod
    def get_certifications_agent_schema() -> Dict[str, Any]:
        """Schema for extracting certifications and professional licenses"""
        return {
            "name": "extract_certifications",
            "description": "Extract certifications, licenses, and professional credentials",
            "parameters": {
                "type": "object",
                "properties": {
                    "certifications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the certification"},
                                "issuedBy": {"type": "string", "description": "Organization that issued the certification"},
                                "dateObtained": {"type": "string", "description": "Date when certification was obtained"},
                                "certificationNumber": {"type": "string", "description": "Certification ID or number if available"},
                                "expirationDate": {"type": "string", "description": "Expiration date if applicable"}
                            }
                        },
                        "description": "All certifications with details preserved exactly as written. Only extract explicitly mentioned certifications."
                    }
                },
                "required": ["certifications"]
            }
        }
    
    ##shale