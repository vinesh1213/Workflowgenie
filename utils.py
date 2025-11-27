import json
import re
import logging

logger = logging.getLogger(__name__)


def safe_parse_json(text: str, default=None):
    """Safely parse JSON from text with multiple fallback strategies."""
    if not text:
        return default
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass
    
    bracket_match = re.search(r'\[.*\]', text, re.DOTALL)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(0))
        except json.JSONDecodeError:
            pass
    
    logger.warning("safe_parse_json: Could not extract valid JSON from: %s", text[:200])
    return default


def extract_json_object(text: str, default=None):
    """Extract a JSON object {...} from text."""
    result = safe_parse_json(text, default)
    if isinstance(result, dict):
        return result
    return default


def extract_json_array(text: str, default=None):
    """Extract a JSON array [...] from text."""
    result = safe_parse_json(text, default or [])
    if isinstance(result, list):
        return result
    return default or []

