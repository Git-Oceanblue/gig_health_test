"""
Token Logger Utility for OpenAI API calls
Migrated from Node.js tokenLogger.js with identical functionality
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """
    Calculate the approximate cost of OpenAI API usage based on token counts
    Equivalent to calculateCost function in Node.js
    
    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        model: The OpenAI model name
        
    Returns:
        Estimated cost in USD
    """
    
    pricing = {
        'gpt-4o-mini': {
            'input': 0.00015,   
            'output': 0.0006    
        },
        'gpt-4o': {
            'input': 0.003,     
            'output': 0.01      
        }
    }
    

    model_pricing = pricing.get(model, pricing['gpt-4o-mini'])
    
    input_cost = (prompt_tokens / 1000) * model_pricing['input']
    output_cost = (completion_tokens / 1000) * model_pricing['output']
    
    return input_cost + output_cost

def log_token_usage(response: Any, model: str, start_time: datetime, operation: str = 'OpenAI API Call') -> Dict[str, Any]:
    """
    Log token usage information from an OpenAI API response
    """
    if not response or not hasattr(response, 'usage') or not response.usage:
        logger.warning('❌ Unable to log token usage: No usage data in response')
        return {
            'promptTokens': 0,
            'completionTokens': 0,
            'totalTokens': 0,
            'duration': 0,
            'cost': 0
        }
    
    end_time = datetime.now()
    call_duration = (end_time - start_time).total_seconds()
    
    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cost = calculate_cost(prompt_tokens, completion_tokens, model)
    
    return {
        'promptTokens': prompt_tokens,
        'completionTokens': completion_tokens,
        'totalTokens': total_tokens,
        'duration': call_duration,
        'cost': cost
    }

def start_timing() -> datetime:
    """
    Start timing an API call
    Equivalent to startTiming function in Node.js
    
    Returns:
        The start time
    """
    return datetime.now()



def log_cache_analysis(response: Any, section_name: Optional[str] = None) -> None:
    """
    Log cache bypass information for OpenAI API responses
    Enhanced functionality for cache analysis
    
    Args:
        response: The OpenAI API response object
        section_name: Optional section name for context
    """
    if not response or not hasattr(response, 'usage') or not response.usage:
        return
    
    usage = response.usage
    

    if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
        cached_tokens = getattr(usage.prompt_tokens_details, 'cached_tokens', 0)
        total_prompt_tokens = usage.prompt_tokens
        cache_hit_rate = (cached_tokens / total_prompt_tokens * 100) if total_prompt_tokens > 0 else 0
        
        context = f" ({section_name})" if section_name else ""
        logger.info(f"🔍 CACHE ANALYSIS{context}:")
        logger.info(f"   Total Prompt Tokens: {total_prompt_tokens}")
        logger.info(f"   Cached Tokens: {cached_tokens}")
        logger.info(f"   Cache Hit Rate: {cache_hit_rate:.1f}%")
        logger.info(f"   Cache Bypass: {'✅ SUCCESSFUL' if cache_hit_rate < 10 else '❌ FAILED'}")
