from flask import request, jsonify
import re
import uuid

def validate_uuid(uuid_string):
    """
    Validate a UUID string
    
    Args:
        uuid_string (str): The UUID string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False

def validate_email(email):
    """
    Validate an email address
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data
    
    Args:
        data (dict): The data to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, f"Missing required field: {field}"
    return True, ""

def validate_user_data(data):
    """
    Validate user data
    
    Args:
        data (dict): The user data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['username', 'email']
    is_valid, error_message = validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_message
    
    # Validate email
    if not validate_email(data['email']):
        return False, "Invalid email format"
    
    # Validate age if provided
    if 'age' in data and data['age'] is not None:
        try:
            age = int(data['age'])
            if age < 13 or age > 120:
                return False, "Age must be between 13 and 120"
        except (ValueError, TypeError):
            return False, "Age must be a number"
    
    return True, ""

def validate_content_data(data):
    """
    Validate content data
    
    Args:
        data (dict): The content data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['user_id', 'content_type', 'content']
    is_valid, error_message = validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_message
    
    # Validate user_id
    if not validate_uuid(data['user_id']):
        return False, "Invalid user_id format"
    
    # Validate content_type
    valid_content_types = ['thread', 'video', 'mixed']
    if data['content_type'] not in valid_content_types:
        return False, f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
    
    return True, ""

def validate_ad_data(data):
    """
    Validate ad data
    
    Args:
        data (dict): The ad data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['advertiser_id', 'title', 'content', 'content_type', 'budget']
    is_valid, error_message = validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_message
    
    # Validate advertiser_id
    if not validate_uuid(data['advertiser_id']):
        return False, "Invalid advertiser_id format"
    
    # Validate content_type
    valid_content_types = ['thread', 'video', 'mixed']
    if data['content_type'] not in valid_content_types:
        return False, f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
    
    # Validate budget
    try:
        budget = float(data['budget'])
        if budget <= 0:
            return False, "Budget must be greater than 0"
    except (ValueError, TypeError):
        return False, "Budget must be a number"
    
    return True, ""

def validate_report_data(data):
    """
    Validate content report data
    
    Args:
        data (dict): The report data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['reporter_id', 'content_id', 'content_type', 'report_reason']
    is_valid, error_message = validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_message
    
    # Validate reporter_id
    if not validate_uuid(data['reporter_id']):
        return False, "Invalid reporter_id format"
    
    # Validate content_id
    if not validate_uuid(data['content_id']):
        return False, "Invalid content_id format"
    
    # Validate content_type
    valid_content_types = ['post', 'comment', 'ad', 'thread', 'video']
    if data['content_type'] not in valid_content_types:
        return False, f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
    
    # Validate report_reason
    valid_reasons = [
        'spam', 'hate_speech', 'violence', 'harassment', 'misinformation',
        'inappropriate', 'copyright', 'other'
    ]
    if data['report_reason'] not in valid_reasons:
        return False, f"Invalid report_reason. Must be one of: {', '.join(valid_reasons)}"
    
    # Validate severity_score if provided
    if 'severity_score' in data and data['severity_score'] is not None:
        try:
            score = float(data['severity_score'])
            if score < 0 or score > 1:
                return False, "Severity score must be between 0 and 1"
        except (ValueError, TypeError):
            return False, "Severity score must be a number"
    
    return True, ""

def validate_moderation_action_data(data):
    """
    Validate moderation action data
    
    Args:
        data (dict): The moderation action data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['report_id', 'moderator_id', 'action_type']
    is_valid, error_message = validate_required_fields(data, required_fields)
    if not is_valid:
        return False, error_message
    
    # Validate report_id
    if not validate_uuid(data['report_id']):
        return False, "Invalid report_id format"
    
    # Validate moderator_id
    if not validate_uuid(data['moderator_id']):
        return False, "Invalid moderator_id format"
    
    # Validate action_type
    valid_action_types = [
        'warn', 'remove_content', 'ban_user', 'restrict_user',
        'flag_content', 'dismiss_report'
    ]
    if data['action_type'] not in valid_action_types:
        return False, f"Invalid action_type. Must be one of: {', '.join(valid_action_types)}"
    
    return True, "" 