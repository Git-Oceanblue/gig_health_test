import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def chunk_resume_from_bold_headings(raw_text: str) -> Dict[str, str]:
    """
    Chunk resume from bold headings
    Equivalent to chunkResumeFromBoldHeadings function in Node.js
    
    Args:
        raw_text: Raw text processed by document parser
        
    Returns:
        Dictionary of resume sections
    """
    logger.info('\n=== RAW TEXT FROM DOCUMENT PARSER ===')
    logger.info(raw_text)
    logger.info(f'Total raw text length: {len(raw_text)} characters')
    logger.info('===================================\n')
    
    section_keywords = {
        'summary': [
            'summary', 'experience summary', 'professional summary', 'professional background',
            'profile', 'professional profile', 'career summary', 'career profile',
            'executive summary', 'technical summary', 'overview', 'profile summary'
        ],
        'experience': [
            'experience', 'work experience', 'employment', 'professional experience',
            'work history', 'career history', 'employment history'
        ],
        'education': [
            'education', 'educational background', 'academic background', 'academic history',
            'academic qualification', 'academic qualifications'
        ],
        'skills': [
            'skills', 'technical skills', 'core competencies', 'key skills',
            'areas of expertise', 'skills summary'
        ],
        'certifications': [
            'certifications', 'certification', 'certified'
        ]
    }
    
    sections = {
        'header': "",
        'summary': "",
        'experience': "",
        'education': "",
        'skills': "",
        'certifications': ""
    }
    

    all_matches = find_sections_by_words(raw_text, section_keywords)
    logger.info(f'Found {len(all_matches)} section matches')
    
    logger.info("\n=== ALL SECTION MATCHES ===")
    for i, match in enumerate(all_matches):
        logger.info(f"{i+1}. {match['section_key']} - \"{match['text']}\" at position {match['start']}")
    
    if len(all_matches) == 0:
        logger.warning('\n⚠️ WARNING: No matching section headings found in the document')
        return {'error': "No matching section headings found."}

    if all_matches:
        first_heading = all_matches[0]
        header_content = raw_text[:first_heading['start']].strip()
        clean_header_text = re.sub(r'</?[^>]+(>|$)', '', header_content)
        sections['header'] = clean_header_text
        
        logger.info('\n=== HEADER SECTION EXTRACTED ===')
        logger.info(sections['header'])
        logger.info('================================\n')
    
    all_matches.append({
        'section_key': "end_of_document",
        'text': "",
        'start': len(raw_text),
        'end': len(raw_text)
    })
    

    for i in range(len(all_matches) - 1):
        this_heading = all_matches[i]
        next_heading = all_matches[i + 1]
        chunk_content = raw_text[this_heading['end']:next_heading['start']].strip()
        clean_text = re.sub(r'</?[^>]+(>|$)', '', chunk_content)
        sections[this_heading['section_key']] += clean_text + "\n"

    extract_certifications_from_text(raw_text, sections)
    
    logger.info('\n=== EXTRACTED SECTIONS ===')
    for section_name, content in sections.items():
        if content and content.strip():
            logger.info(f'\n--- {section_name.upper()} SECTION ---')
            logger.info(content)
            logger.info('-------------------------')
        else:
            logger.info(f'\n--- {section_name.upper()} SECTION --- (empty)')
    logger.info('=========================\n')
    

    sanitized_sections = sanitize_sensitive_info(sections)
    
    return sanitized_sections

def find_sections_by_words(raw_text: str, section_keywords: Dict[str, List[str]]) -> List[Dict[str, any]]:
    """
    Find sections by searching for keywords in clean text, regardless of HTML formatting
    Equivalent to findSectionsByWords function in Node.js
    
    Args:
        raw_text: Raw text with potential HTML formatting
        section_keywords: Dictionary of section keywords
        
    Returns:
        List of section matches
    """
    matches = []
    
    clean_text = re.sub(r'</?[^>]+(>|$)', '', raw_text)
    lines = clean_text.split('\n')
    
    current_position = 0
    original_position = 0
    
    for line_index, line in enumerate(lines):
        clean_line = line.lower().strip()
  
        if len(clean_line) < 3:
            current_position += len(line) + 1  # +1 for newline
            original_position = find_original_position(raw_text, current_position)
            continue
        
        if len(clean_line) <= 50:

            line_without_colon = clean_line.replace(':', '').strip()
            line_with_colon = clean_line
            
            for section_key, keywords in section_keywords.items():
                for keyword in keywords:
                    keyword_lower = keyword.lower()

                    if line_without_colon == keyword_lower or line_with_colon == keyword_lower + ':':
                 
                        if is_line_standalone(line, lines, line_index):
                          
                            line_start_in_raw = find_line_position_in_raw_text(raw_text, line, original_position)
                            line_end_in_raw = line_start_in_raw + find_original_line_length(raw_text, line, line_start_in_raw)
                            
                            logger.info(f'Found section: "{clean_line}" -> {section_key} at line {line_index + 1}')
                            
                            matches.append({
                                'section_key': section_key,
                                'text': clean_line,
                                'start': line_start_in_raw,
                                'end': line_end_in_raw
                            })
                            
                          
                            break
                    
                   
                    if line_without_colon.startswith(keyword_lower + ' '):
                        if is_line_standalone(line, lines, line_index):
                            line_start_in_raw = find_line_position_in_raw_text(raw_text, line, original_position)
                            line_end_in_raw = line_start_in_raw + find_original_line_length(raw_text, line, line_start_in_raw)
                            
                            logger.info(f'Found section (starts-with): "{clean_line}" -> {section_key} at line {line_index + 1}')
                            
                            matches.append({
                                'section_key': section_key,
                                'text': clean_line,
                                'start': line_start_in_raw,
                                'end': line_end_in_raw
                            })
                            
                            break
        
        current_position += len(line) + 1  
        original_position = current_position
    

    return remove_duplicate_sections(sorted(matches, key=lambda x: x['start']))

def is_line_standalone(line: str, all_lines: List[str], line_index: int) -> bool:
    """
    Check if a line is standalone (not part of a larger paragraph)
    Equivalent to isLineStandalone function in Node.js
    
    Args:
        line: Current line
        all_lines: All lines in the document
        line_index: Index of current line
        
    Returns:
        True if line is standalone
    """
    clean_line = line.strip()
    
    # Must not be empty
    if not clean_line:
        return False
    
    # Check previous line
    prev_line = all_lines[line_index - 1].strip() if line_index > 0 else ''
    next_line = all_lines[line_index + 1].strip() if line_index < len(all_lines) - 1 else ''
    
    # Line should be relatively short for a heading
    if len(clean_line) > 50:
        return False
    
    # Line should not end with a sentence-ending that continues to next line
    if clean_line.endswith(',') or clean_line.endswith('and') or clean_line.endswith('or'):
        return False
    
    # Line should not start mid-sentence from previous line
    if prev_line.endswith(',') and not prev_line.endswith('.') and not prev_line.endswith(':'):
        return False
    
    # Should have some spacing around it or be at document boundaries
    has_spacing_before = not prev_line or prev_line == '' or prev_line.endswith('.') or prev_line.endswith(':')
    has_spacing_after = not next_line or next_line == '' or re.match(r'^[A-Z]', next_line)
    
    return has_spacing_before or has_spacing_after

def find_line_position_in_raw_text(raw_text: str, clean_line: str, approximate_position: int) -> int:
    """
    Find the position of a clean line in the original raw text with HTML
    Equivalent to findLinePositionInRawText function in Node.js
    
    Args:
        raw_text: Original raw text with HTML
        clean_line: Clean line to find
        approximate_position: Approximate position to start search
        
    Returns:
        Position of line in raw text
    """
    # Create a search pattern from the clean line
    words = [word for word in clean_line.split() if word]
    if not words:
        return approximate_position
    
    # Look for the words in sequence in the raw text around the approximate position
    search_start = max(0, approximate_position - 500)
    search_end = min(len(raw_text), approximate_position + 500)
    search_text = raw_text[search_start:search_end].lower()
    
    # Find all words in sequence
    last_pos = 0
    for word in words:
        word_pos = search_text.find(word.lower(), last_pos)
        if word_pos == -1:
            # Fallback to approximate position
            return approximate_position
        last_pos = word_pos + len(word)
    
    # Find the start of the first word
    first_word_pos = search_text.find(words[0].lower())
    return search_start + first_word_pos

def find_original_line_length(raw_text: str, clean_line: str, start_position: int) -> int:
    """
    Find the original length of a line in raw text (including HTML tags)
    Equivalent to findOriginalLineLength function in Node.js
    
    Args:
        raw_text: Original raw text with HTML
        clean_line: Clean line
        start_position: Start position in raw text
        
    Returns:
        Original line length
    """
    words = [word for word in clean_line.split() if word]
    if not words:
        return 0
    
    # Find the end of the last word
    last_word = words[-1].replace(':', '')  # Remove colon for search
    search_text = raw_text[start_position:start_position + 200].lower()
    last_word_pos = search_text.rfind(last_word.lower())
    
    if last_word_pos == -1:
        return len(clean_line)  # Fallback
    
    return last_word_pos + len(last_word)

def find_original_position(raw_text: str, clean_position: int) -> int:
    """
    Find original position accounting for HTML tags
    Equivalent to findOriginalPosition function in Node.js
    
    Args:
        raw_text: Original raw text with HTML
        clean_position: Position in clean text
        
    Returns:
        Position in original text
    """
    html_position = 0
    clean_count = 0
    
    while html_position < len(raw_text) and clean_count < clean_position:
        if raw_text[html_position] == '<':
            # Skip HTML tag
            while html_position < len(raw_text) and raw_text[html_position] != '>':
                html_position += 1
            if html_position < len(raw_text):
                html_position += 1  # Skip '>'
        else:
            clean_count += 1
            html_position += 1
    
    return html_position

def remove_duplicate_sections(matches: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Remove duplicate section matches that are too close to each other
    Equivalent to removeDuplicateSections function in Node.js

    Args:
        matches: List of section matches

    Returns:
        Filtered list without duplicates
    """
    if len(matches) <= 1:
        return matches

    result = [matches[0]]

    for i in range(1, len(matches)):
        current = matches[i]
        previous = result[-1]

        # If this is the same section type and close to the previous match, skip it
        if (current['section_key'] == previous['section_key'] and
            (current['start'] - previous['end'] < 200)):
            continue

        result.append(current)

    return result

def sanitize_sensitive_info(sections: Dict[str, str]) -> Dict[str, str]:
    """
    Remove sensitive information like email, phone, and LinkedIn URLs from all sections
    Equivalent to sanitizeSensitiveInfo function in Node.js

    Args:
        sections: Dictionary of resume sections

    Returns:
        Sanitized sections dictionary
    """
    sanitized = {}


    for section_name, content in sections.items():
        if not content:
            sanitized[section_name] = ""
            continue

        sanitized_content = content

        sanitized_content = re.sub(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            '[EMAIL REDACTED]',
            sanitized_content
        )

        sanitized_content = re.sub(
            r'(\+\d{1,3}[-\s]?)?(\(?\d{3}\)?[-\s]?)?\d{3}[-\s]?\d{4}',
            '[PHONE REDACTED]',
            sanitized_content
        )

        sanitized_content = re.sub(
            r'https?://(www\.)?linkedin\.com/in/[^\s]+',
            '[LINKEDIN REDACTED]',
            sanitized_content
        )
        sanitized_content = re.sub(
            r'linkedin\.com/in/[^\s]+',
            '[LINKEDIN REDACTED]',
            sanitized_content
        )

        sanitized[section_name] = sanitized_content


    logger.info('\n=== SANITIZED SECTIONS (SENSITIVE INFO REMOVED) ===')
    for section_name, content in sanitized.items():
        if content and content.strip() and content != sections.get(section_name, ''):
            logger.info(f'\n--- SANITIZED {section_name.upper()} SECTION ---')
            logger.info(content)
            logger.info('-------------------------')
    logger.info('=================================================\n')

    return sanitized

def extract_certifications_from_text(raw_text: str, sections: Dict[str, str]) -> None:
    """
    Extract certification-related lines from the entire text
    Equivalent to extractCertificationsFromText function in Node.js

    Args:
        raw_text: Raw text from document
        sections: Sections dictionary to update
    """

    clean_text = re.sub(r'</?[^>]+(>|$)', '', raw_text)

    lines = clean_text.split('\n')


    cert_keywords = [
        'certified', 'certification', 'certificate', 'license', 'credential',
        'awarded', 'accredited', 'qualified', 'diploma'
    ]

    certification_lines = []
    for line in lines:
        lower_line = line.lower().strip()
        if len(lower_line) < 5:
            continue


        if any(keyword in lower_line for keyword in cert_keywords):
            certification_lines.append(line.strip())


    if certification_lines:
        logger.info('\n=== FOUND CERTIFICATION LINES IN TEXT ===')
        for line in certification_lines:
            logger.info(f'- {line}')
        logger.info('=======================================\n')

        if sections.get('certifications'):
            sections['certifications'] += '\n' + '\n'.join(certification_lines)
        else:
            sections['certifications'] = '\n'.join(certification_lines)
