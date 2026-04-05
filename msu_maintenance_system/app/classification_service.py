"""
Classification Service
Deterministic rule-based categorization and priority assignment
"""

import logging

logger = logging.getLogger(__name__)

def classify_request(description):
    """
    Classify maintenance request using rule-based logic
    
    Args:
        description (str): Request description
        
    Returns:
        tuple: (category, priority)
    """
    logger.info(f"Processing request: {description[:50]}...")
    
    description_lower = description.lower()
    
    # Category mapping based on keywords
    category_keywords = {
        'electrical': ['electric', 'light', 'power', 'socket', 'switch', 'bulb', 'fan', 'ac', 'air conditioner'],
        'plumbing': ['water', 'pipe', 'leak', 'drain', 'sink', 'toilet', 'bathroom', 'faucet', 'shower'],
        'carpentry': ['wood', 'door', 'window', 'chair', 'table', 'desk', 'cabinet', 'shelf', 'lock'],
        'cleaning': ['clean', 'dirt', 'trash', 'garbage', 'sweep', 'mop', 'dust', 'sanitary'],
        'hvac': ['ac', 'air conditioner', 'heating', 'ventilation', 'cooling', 'temperature'],
        'general': []  # fallback
    }
    
    # Determine category
    category = 'General'  # default
    for cat, keywords in category_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            category = cat.title()
            break
    
    # Priority mapping based on urgency keywords
    urgent_keywords = ['urgent', 'emergency', 'broken', 'leaking', 'danger', 'hazard', 'immediate']
    high_keywords = ['important', 'priority', 'asap', 'soon', 'quickly']
    
    if any(keyword in description_lower for keyword in urgent_keywords):
        priority = 'High'
    elif any(keyword in description_lower for keyword in high_keywords):
        priority = 'Medium-High'
    elif any(keyword in description_lower for keyword in ['low', 'minor', 'when possible']):
        priority = 'Low'
    else:
        priority = 'Medium'
    
    logger.info(f"Classification result: {category}, {priority}")
    return category, priority
