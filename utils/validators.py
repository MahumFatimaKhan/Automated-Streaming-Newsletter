import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """Validate date range for scraping."""
    try:
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Check if start is before end
        if start > end:
            return False, "Start date must be before end date"
        
        # Check if range exceeds 30 days
        if (end - start).days > 30:
            return False, "Date range cannot exceed 30 days"
        
        # Check if dates are not too far in the future
        max_future = datetime.now() + timedelta(days=90)
        if end > max_future:
            return False, "End date cannot be more than 90 days in the future"
        
        return True, "Valid date range"
        
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)$'
    return re.match(pattern, url) is not None

def sanitize_html(text: str) -> str:
    """Sanitize text for HTML output."""
    if not text:
        return ""
    
    # Escape HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    return text

def validate_api_key(api_key: str, service: str) -> bool:
    """Validate API key format for different services."""
    if not api_key:
        return False
    
    if service == 'openai':
        # OpenAI keys typically start with 'sk-'
        return api_key.startswith('sk-') and len(api_key) > 20
    elif service == 'flux':
        # Flux API key validation (adjust based on actual format)
        return len(api_key) > 10
    
    return False

def validate_scraped_item(item: Dict) -> bool:
    """Validate a scraped content item has required fields."""
    required_fields = ['name', 'channel', 'date']
    
    for field in required_fields:
        if field not in item or not item[field]:
            return False
    
    return True

def clean_scraped_data(items: List[Dict]) -> List[Dict]:
    """Clean and validate scraped data."""
    cleaned_items = []
    
    for item in items:
        if validate_scraped_item(item):
            # Sanitize text fields
            if 'description' in item:
                item['description'] = sanitize_html(item['description'])
            if 'name' in item:
                item['name'] = sanitize_html(item['name'])
            
            cleaned_items.append(item)
    
    return cleaned_items