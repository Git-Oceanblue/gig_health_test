"""
File Parser Utilities for FastAPI Resume Builder Backend
Direct document parsing without subprocess
"""

import os
import logging
from docx2python import docx2python
import fitz  

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from uploaded file using direct parsing
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        Extracted text content
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    logger.info(f'🔍 Processing file: {file_path} (extension: {file_extension})')


    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    logger.info(f'📊 File size: {file_size} bytes')

    try:
        if file_extension == '.docx':
            logger.info('🔄 Using docx2python for DOCX extraction...')
            try:
   
                doc = docx2python(file_path)
                text = doc.text
                doc.close()
                logger.info(f'✅ DOCX extraction successful - Text length: {len(text)} characters')
                logger.info(f'📝 First 500 characters: {text[:500]}...')
                return text
            except Exception as docx_error:
                logger.error(f'❌ DOCX extraction failed: {docx_error}')

                logger.info('🔄 Trying alternative DOCX extraction...')
                try:
                    import zipfile
                    from xml.etree import ElementTree as ET

                    with zipfile.ZipFile(file_path, 'r') as docx_zip:

                        doc_xml = docx_zip.read('word/document.xml')
                        root = ET.fromstring(doc_xml)

                        text_elements = []
                        for elem in root.iter():
                            if elem.text:
                                text_elements.append(elem.text)

                        text = ' '.join(text_elements)
                        logger.info(f'✅ Alternative DOCX extraction successful - Text length: {len(text)} characters')
                        return text

                except Exception as alt_error:
                    logger.error(f'❌ Alternative DOCX extraction also failed: {alt_error}')
                    raise Exception(f"Failed to extract text from DOCX file: {docx_error}")
            
        elif file_extension == '.pdf':
            logger.info('🔄 Using PyMuPDF for PDF extraction...')
            doc = fitz.open(file_path)
            text = ""
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += page_text + "\n"
                logger.info(f'📄 Page {page_num + 1} extracted {len(page_text)} characters')
            doc.close()
            logger.info(f'✅ PDF extraction successful - Total text length: {len(text)} characters')
            logger.info(f'📝 First 500 characters: {text[:500]}...')
            return text
            
        elif file_extension == '.txt':
            logger.info('🔄 Reading TXT file...')
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.info('✅ TXT extraction successful')
            return text
            
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
    except Exception as e:
        logger.error(f'❌ File extraction failed: {e}')
        raise Exception(f"Failed to extract text from file: {e}")
