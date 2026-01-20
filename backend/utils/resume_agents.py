"""
Multi-Agent Resume Processing System
Simplified version with 6 specialized agents for parallel processing
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

from openai import AsyncOpenAI
from .agent_schemas import ResumeAgentSchemas
from .token_logger import start_timing, log_cache_analysis
from .chunk_resume import strip_bullet_prefix

logger = logging.getLogger(__name__)

def normalize_work_period(work_period: str) -> str:
    """Normalize work period format to exact specification"""
    if not work_period:
        return work_period
    
    # Replace em-dash and en-dash with regular hyphen
    normalized = work_period.replace('–', '-').replace('—', '-')
    
    # Replace "to" with hyphen (case insensitive)
    normalized = re.sub(r'\s+to\s+', ' - ', normalized, flags=re.IGNORECASE)
    
    # Fix spacing around hyphen
    normalized = re.sub(r'\s*[-–—]\s*', ' - ', normalized)
    
    # Convert full month names to abbreviations
    month_mapping = {
        'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
        'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
        'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
    }
    
    for full_month, abbrev in month_mapping.items():
        normalized = normalized.replace(full_month, abbrev)
    
    # Handle any text after hyphen that contains no numeric digits - replace with "Till Date"
    # If there are no digits in the text after hyphen, replace it with "Till Date"
    if re.search(r' - [^0-9]*$', normalized):
        normalized = re.sub(r' - [^0-9]*$', ' - Till Date', normalized)
    
    return normalized.strip()

def normalize_location(location: str) -> str:
    """Normalize location format to exact specification"""
    if not location:
        return location
    
    # Remove extra spaces and normalize
    normalized = ' '.join(location.split())
    
    # US state name to abbreviation mapping
    state_mapping = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    
    # Convert full state names to abbreviations
    for full_state, abbrev in state_mapping.items():
        # Match full state name at the end after comma
        pattern = r',\s*' + re.escape(full_state) + r'$'
        normalized = re.sub(pattern, f', {abbrev}', normalized, flags=re.IGNORECASE)
    
    # Fix common formatting issues
    # Handle missing comma: "Dallas TX" -> "Dallas, TX"
    normalized = re.sub(r'^([A-Za-z\s]+)\s+([A-Z]{2})$', r'\1, \2', normalized)
    
    # Fix spacing around comma: "Dallas,TX" -> "Dallas, TX" or "Dallas , TX" -> "Dallas, TX"
    normalized = re.sub(r'\s*,\s*', ', ', normalized)
    
    # Handle common separators: "Dallas-TX" or "Dallas|TX" -> "Dallas, TX"
    normalized = re.sub(r'[-|]\s*', ', ', normalized)
    
    return normalized.strip()

class AgentType(Enum):
    """Enumeration of available resume processing agents"""
    HEADER = "header"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"

@dataclass
class AgentResult:
    """Structured result from an individual agent"""
    agent_type: AgentType
    data: Dict[str, Any]
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class ResumeAgent:
    """
    Individual resume processing agent with specialized extraction capabilities
    """
    
    def __init__(self, client: AsyncOpenAI, agent_type: AgentType):
        self.client = client
        self.agent_type = agent_type
        self.schema = self._get_agent_schema()
        
    def _get_agent_schema(self) -> Dict[str, Any]:
        """Get the appropriate schema for this agent type"""
        schema_map = {
            AgentType.HEADER: ResumeAgentSchemas.get_header_agent_schema,
            AgentType.SUMMARY: ResumeAgentSchemas.get_summary_agent_schema,
            AgentType.EXPERIENCE: ResumeAgentSchemas.get_experience_agent_schema,
            AgentType.EDUCATION: ResumeAgentSchemas.get_education_agent_schema,
            AgentType.SKILLS: ResumeAgentSchemas.get_skills_agent_schema,
            AgentType.CERTIFICATIONS: ResumeAgentSchemas.get_certifications_agent_schema
        }
        return schema_map[self.agent_type]()
    
    def _get_system_prompt(self) -> str:
        """Get specialized system prompt for this agent"""
        base_prompt = """You are a specialized resume extraction agent with 40 years of experience. 
Your task is to extract ONLY the specific section you're responsible for with perfect accuracy.

CRITICAL INSTRUCTIONS:
1. Extract ONLY the section type you're assigned to
2. Preserve ALL content exactly as written - no summarization
3. Maintain original structure and formatting
4. If the section doesn't exist, return empty arrays/objects
5. Never invent or hallucinate information
6. PROJECTS RULE: Only include projects if they are explicitly mentioned in the resume text. If no projects are mentioned for a job, return empty projects array."""

        section_specific = {
            AgentType.HEADER: "Focus ONLY on personal information: name, title, contact details, requisition numbers.",
            AgentType.SUMMARY: "Extract ONLY professional summary, career overview, and profile sections. Include ALL bullet points and paragraphs.",
            AgentType.EXPERIENCE: """Extract ONLY employment history and work experience. Include ALL jobs with complete details. Missing any job is unacceptable. 

CRITICAL PROJECT EXTRACTION RULES:
- ONLY include 'projects' if explicitly mentioned specific named projects, project titles, or project-specific work for that job, if it is outside that particular job entry dont add.
- If a job only lists general responsibilities without mentioning specific projects, return projects as empty array []
""",
            AgentType.EDUCATION: "Extract ONLY education, academic background, and degrees. Include ALL educational entries.",
            AgentType.SKILLS: "Extract ONLY technical skills with proper hierarchical structure. When you see a main heading followed by colon-separated items, the main heading becomes the categoryName and the colon-separated items become subCategories. Items that appear grouped under a main heading belong together as subcategories, not as separate main categories. Preserve the exact nesting structure as written in the resume.",
            AgentType.CERTIFICATIONS: "Extract ONLY certifications, licenses, and professional credentials. Only include explicitly mentioned certifications."
        }
        
        return f"{base_prompt}\n\nSPECIFIC FOCUS: {section_specific[self.agent_type]}"
    
    def _add_cache_variation(self, text: str) -> str:
        """Add cache-busting variation to prevent OpenAI caching"""
        import random
        import time
        
        timestamp = int(time.time() * 1000)
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        agent_session = f"AGENT_{self.agent_type.value.upper()}_{timestamp}_{random_id}"
        
        cache_breaker = f"[Agent Session: {agent_session}]\n[Processing: {self.agent_type.value}]\n[Timestamp: {datetime.now().isoformat()}]\n\n"
        
        return cache_breaker + text
    
    async def process(self, input_text: str, model: str = 'gpt-4o-mini') -> AgentResult:
        """
        Process resume text and extract section-specific data
        
        Args:
            input_text: Resume text (can be full resume or chunked section)
            model: OpenAI model to use
            
        Returns:
            AgentResult with extracted data and metadata
        """
        start_time = start_timing()
        
        try:
            input_length = len(input_text)
            logger.info(f"🤖 {self.agent_type.value.title()} Agent: Starting extraction... (Input: {input_length} chars)")
            
            # Prepare the prompt with cache busting
            user_prompt = self._add_cache_variation(
                f"Extract {self.agent_type.value} information from this resume:\n\n{input_text}"
            )
            
            # Make OpenAI API call
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                tools=[{"type": "function", "function": self.schema}],
                tool_choice={"type": "function", "function": {"name": self.schema["name"]}},
                max_tokens=16384,
                temperature=0.1
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log cache analysis
            log_cache_analysis(response, self.agent_type.value)
            
            # Parse the response
            tool_call_arguments = response.choices[0].message.tool_calls[0].function.arguments
            extracted_data = json.loads(tool_call_arguments)
            
            # Clean bullet points if needed
            cleaned_data = self._clean_extracted_data(extracted_data)
            
            logger.info(f"✅ {self.agent_type.value.title()} Agent: Extraction successful ({processing_time:.2f}s)")
            
            return AgentResult(
                agent_type=self.agent_type,
                data=cleaned_data,
                processing_time=processing_time,
                success=True
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ {self.agent_type.value.title()} Agent: JSON parsing error - {e}")
            return self._create_error_result(start_time, f"JSON parsing failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ {self.agent_type.value.title()} Agent: Processing failed - {e}")
            return self._create_error_result(start_time, str(e))
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean bullet points and format extracted data"""
        if self.agent_type == AgentType.SUMMARY and data.get('professionalSummary'):
            data['professionalSummary'] = [strip_bullet_prefix(item) for item in data['professionalSummary']]
            
            if data.get('summarySections'):
                for section in data['summarySections']:
                    if section.get('content'):
                        section['content'] = [strip_bullet_prefix(item) for item in section['content']]
        
        elif self.agent_type == AgentType.EXPERIENCE and data.get('employmentHistory'):
            for job in data['employmentHistory']:
                # Normalize work period format
                if job.get('workPeriod'):
                    job['workPeriod'] = normalize_work_period(job['workPeriod'])
                
                # Normalize location format
                if job.get('location'):
                    job['location'] = normalize_location(job['location'])
                
                if job.get('responsibilities'):
                    job['responsibilities'] = [strip_bullet_prefix(item) for item in job['responsibilities']]
                if job.get('subsections'):
                    for subsection in job['subsections']:
                        if subsection.get('content'):
                            subsection['content'] = [strip_bullet_prefix(item) for item in subsection['content']]
                if job.get('projects'):
                    for project in job['projects']:
                        # Normalize project period format
                        if project.get('period'):
                            project['period'] = normalize_work_period(project['period'])
                        if project.get('projectResponsibilities'):
                            project['projectResponsibilities'] = [strip_bullet_prefix(item) for item in project['projectResponsibilities']]
                if job.get('clientProjects'):
                    for client_project in job['clientProjects']:
                        if client_project.get('responsibilities'):
                            client_project['responsibilities'] = [strip_bullet_prefix(item) for item in client_project['responsibilities']]
        
        elif self.agent_type == AgentType.EDUCATION and data.get('education'):
            for education in data['education']:
                # Normalize location format
                if education.get('location'):
                    education['location'] = normalize_location(education['location'])
                
                # Normalize date format (apply month abbreviation)
                if education.get('date'):
                    education['date'] = normalize_work_period(education['date'])
        
        elif self.agent_type == AgentType.SKILLS and data.get('skillCategories'):
            for category in data['skillCategories']:
                # Ensure subCategories is always an array
                if not isinstance(category.get('subCategories'), list):
                    category['subCategories'] = []
        
        elif self.agent_type == AgentType.CERTIFICATIONS and data.get('certifications'):
            for cert in data['certifications']:
                # Normalize certification dates (apply month abbreviation)
                if cert.get('dateObtained'):
                    cert['dateObtained'] = normalize_work_period(cert['dateObtained'])
                if cert.get('expirationDate'):
                    cert['expirationDate'] = normalize_work_period(cert['expirationDate'])
        
        return data
    

    
    def _create_error_result(self, start_time: datetime, error_message: str) -> AgentResult:
        """Create an error result"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResult(
            agent_type=self.agent_type,
            data={},
            processing_time=processing_time,
            success=False,
            error_message=error_message
        )

class MultiAgentResumeProcessor:
    """
    Orchestrates multiple specialized agents for parallel resume processing
    """
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        
    async def process_resume_with_agents(
        self, 
        raw_text: str, 
        model: str = 'gpt-4o-mini'
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process resume using multiple specialized agents - simple version
        """
        logger.info("Starting resume processing...")
        
        try:
            # Chunk the resume
            from .chunk_resume import chunk_resume_from_bold_headings
            sections = chunk_resume_from_bold_headings(raw_text)
            
            # Check if chunking was successful
            if 'error' in sections:
                logger.warning(f"Chunking failed: {sections['error']} - Using full resume for all agents")
                sections = {}
            
            # Create all agents
            agents = [
                ResumeAgent(self.client, AgentType.HEADER),
                ResumeAgent(self.client, AgentType.SUMMARY),
                ResumeAgent(self.client, AgentType.EXPERIENCE),
                ResumeAgent(self.client, AgentType.EDUCATION),
                ResumeAgent(self.client, AgentType.SKILLS),
                ResumeAgent(self.client, AgentType.CERTIFICATIONS)
            ]
            
            # Prepare intelligent inputs for each agent
            agent_inputs = self._prepare_agent_inputs(agents, sections, raw_text)
            
            # Process all agents in parallel
            agent_tasks = [
                agent.process(agent_inputs['inputs'][agent.agent_type], model) 
                for agent in agents
            ]
            results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_agents = []
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Agent task failed with exception: {result}")
                    failed_agents.append(str(result))
                    continue
                    
                if result.success:
                    successful_results.append(result)
                else:
                    failed_agents.append(f"{result.agent_type.value}: {result.error_message}")
            
            # Combine results into final structure
            combined_data = self._combine_agent_results(successful_results)
            
            # Report any failures
            if failed_agents:
                logger.warning(f"Some agents failed: {failed_agents}")
            
            # Only yield final result
            yield {
                'type': 'final_data',
                'data': combined_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resume processing failed: {e}")
            yield {
                'type': 'error',
                'message': f'Resume processing failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _prepare_agent_inputs(self, agents: List[ResumeAgent], sections: Dict[str, str], raw_text: str) -> Dict[str, Any]:
        """
        Prepare intelligent inputs for each agent based on chunked sections
        
        Args:
            agents: List of resume agents
            sections: Chunked resume sections
            raw_text: Complete resume text as fallback
            
        Returns:
            Dictionary with agent inputs and strategy information
        """
        agent_inputs = {}
        strategy = {}
        
        # Section mapping for agents
        section_mapping = {
            AgentType.HEADER: 'header',
            AgentType.SUMMARY: 'summary', 
            AgentType.EXPERIENCE: 'experience',
            AgentType.EDUCATION: 'education',
            AgentType.SKILLS: 'skills',
            AgentType.CERTIFICATIONS: 'certifications'  # Special case - always gets full resume
        }
        
        for agent in agents:
            agent_type = agent.agent_type
            section_key = section_mapping[agent_type]
            
            # 🎯 CERTIFICATION AGENT: Always gets full resume
            if agent_type == AgentType.CERTIFICATIONS:
                agent_inputs[agent_type] = raw_text
                strategy[agent_type.value] = 'full_resume_always'
                logger.info(f"🔍 {agent_type.value.title()} Agent: Using full resume (certification rule)")
                continue
            
            # 🎯 OTHER AGENTS: Use chunked section if available, otherwise full resume
            if section_key in sections and sections[section_key] and sections[section_key].strip():
                # Use chunked section
                chunked_content = sections[section_key].strip()
                
                # For header agent, also include some context from the beginning
                if agent_type == AgentType.HEADER:
                    # Include first 1000 characters for better context
                    context_text = raw_text[:1000]
                    agent_inputs[agent_type] = f"{context_text}\n\n--- HEADER SECTION ---\n{chunked_content}"
                    strategy[agent_type.value] = 'chunked_with_context'
                else:
                    agent_inputs[agent_type] = chunked_content
                    strategy[agent_type.value] = 'chunked_section'
                
                logger.info(f"✅ {agent_type.value.title()} Agent: Using chunked section ({len(chunked_content)} chars)")
            else:
                # Fallback to full resume
                agent_inputs[agent_type] = raw_text
                strategy[agent_type.value] = 'full_resume_fallback'
                logger.info(f"⚠️ {agent_type.value.title()} Agent: Section missing/empty, using full resume")
        
        return {
            'inputs': agent_inputs,
            'strategy': strategy
        }
    
    def _combine_agent_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Combine results from all agents into the expected resume structure
        
        Args:
            results: List of successful agent results
            
        Returns:
            Combined resume data in original format
        """
        # Initialize with default structure
        combined_data = {
            'name': '',
            'title': '',
            'requisitionNumber': '',
            'professionalSummary': [],
            'summarySections': [],
            'subsections': [],  # For compatibility
            'employmentHistory': [],
            'education': [],
            'certifications': [],
            'technicalSkills': {},
            'skillCategories': []
        }
        
        # Merge data from each agent
        for result in results:
            agent_data = result.data
            
            if result.agent_type == AgentType.HEADER:
                combined_data.update({
                    'name': agent_data.get('name', ''),
                    'title': agent_data.get('title', ''),
                    'requisitionNumber': agent_data.get('requisitionNumber', '')
                })
                
            elif result.agent_type == AgentType.SUMMARY:
                combined_data.update({
                    'professionalSummary': agent_data.get('professionalSummary', []),
                    'summarySections': agent_data.get('summarySections', [])
                })
                # For compatibility
                combined_data['subsections'] = combined_data['summarySections']
                
            elif result.agent_type == AgentType.EXPERIENCE:
                combined_data['employmentHistory'] = agent_data.get('employmentHistory', [])
                
            elif result.agent_type == AgentType.EDUCATION:
                combined_data['education'] = agent_data.get('education', [])
                
            elif result.agent_type == AgentType.SKILLS:
                combined_data.update({
                    'technicalSkills': agent_data.get('technicalSkills', {}),
                    'skillCategories': agent_data.get('skillCategories', [])
                })
                
            elif result.agent_type == AgentType.CERTIFICATIONS:
                combined_data['certifications'] = agent_data.get('certifications', [])
        
        logger.info(f"✅ Combined data from {len(results)} agents successfully")
        return combined_data