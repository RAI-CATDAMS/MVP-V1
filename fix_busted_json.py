"""
fix_busted_json.py - JSON parsing utilities for TDC AI modules
Provides robust JSON extraction and repair functions for handling AI responses.
"""

import re
import json
from typing import Optional, Union

def first_json(text: str) -> Optional[str]:
    """
    Extract the first valid JSON object from text.
    Handles common formatting issues in AI responses.
    """
    if not text:
        return None
    
    # Try to find JSON object with regex
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            # Test if it's valid JSON
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    # If no valid JSON found, try to extract from markdown code blocks
    code_block_pattern = r'```(?:json)?\s*\n(.*?)\n```'
    code_matches = re.findall(code_block_pattern, text, re.DOTALL)
    
    for match in code_matches:
        try:
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    return None

def repair_json(json_str: str) -> str:
    """
    Attempt to repair common JSON formatting issues.
    """
    if not json_str:
        return "{}"
    
    # Remove markdown formatting
    json_str = re.sub(r'```(?:json)?\s*', '', json_str)
    json_str = re.sub(r'```\s*', '', json_str)
    
    # Fix common issues
    json_str = json_str.strip()
    
    # Fix trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fix missing quotes around keys
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    
    # Fix single quotes to double quotes
    json_str = json_str.replace("'", '"')
    
    # Fix boolean values
    json_str = re.sub(r':\s*true\s*([,}])', r': true\1', json_str)
    json_str = re.sub(r':\s*false\s*([,}])', r': false\1', json_str)
    json_str = re.sub(r':\s*null\s*([,}])', r': null\1', json_str)
    
    return json_str

def safe_json_parse(text: str, default: Union[dict, list] = None) -> Union[dict, list]:
    """
    Safely parse JSON with fallback to default value.
    """
    if default is None:
        default = {}
    
    try:
        # First try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Try to extract and repair JSON
        json_str = first_json(text)
        if json_str:
            repaired = repair_json(json_str)
            return json.loads(repaired)
    except (json.JSONDecodeError, ValueError):
        pass
    
    return default

def extract_json_fields(text: str, fields: list) -> dict:
    """
    Extract specific fields from JSON in text.
    """
    result = {}
    json_data = safe_json_parse(text, {})
    
    for field in fields:
        if field in json_data:
            result[field] = json_data[field]
    
    return result 