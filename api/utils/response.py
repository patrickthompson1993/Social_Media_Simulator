from flask import jsonify
from typing import Any, Dict, List, Optional, Union

def success_response(
    data: Optional[Union[Dict, List]] = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple:
    """
    Create a success response
    
    Args:
        data: The response data
        message: The success message
        status_code: The HTTP status code
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'status': 'success',
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def paginated_response(
    data: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Success"
) -> tuple:
    """
    Create a paginated response
    
    Args:
        data: The response data
        page: The current page number
        per_page: The number of items per page
        total: The total number of items
        message: The success message
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'status': 'success',
        'message': message,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }
    
    return jsonify(response), 200

def created_response(
    data: Optional[Union[Dict, List]] = None,
    message: str = "Resource created successfully"
) -> tuple:
    """
    Create a response for resource creation
    
    Args:
        data: The response data
        message: The success message
        
    Returns:
        tuple: (response, status_code)
    """
    return success_response(data, message, 201)

def updated_response(
    data: Optional[Union[Dict, List]] = None,
    message: str = "Resource updated successfully"
) -> tuple:
    """
    Create a response for resource update
    
    Args:
        data: The response data
        message: The success message
        
    Returns:
        tuple: (response, status_code)
    """
    return success_response(data, message, 200)

def deleted_response(
    message: str = "Resource deleted successfully"
) -> tuple:
    """
    Create a response for resource deletion
    
    Args:
        message: The success message
        
    Returns:
        tuple: (response, status_code)
    """
    return success_response(message=message, status_code=200)

def no_content_response() -> tuple:
    """
    Create a no content response
    
    Returns:
        tuple: (response, status_code)
    """
    return '', 204

def error_response(
    message: str,
    errors: Optional[Dict] = None,
    status_code: int = 400
) -> tuple:
    """
    Create an error response
    
    Args:
        message: The error message
        errors: Additional error details
        status_code: The HTTP status code
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'status': 'error',
        'message': message
    }
    
    if errors is not None:
        response['errors'] = errors
    
    return jsonify(response), status_code

def validation_error_response(
    message: str,
    errors: Dict
) -> tuple:
    """
    Create a validation error response
    
    Args:
        message: The error message
        errors: The validation errors
        
    Returns:
        tuple: (response, status_code)
    """
    return error_response(message, errors, 400)

def not_found_response(
    message: str = "Resource not found"
) -> tuple:
    """
    Create a not found response
    
    Args:
        message: The error message
        
    Returns:
        tuple: (response, status_code)
    """
    return error_response(message, status_code=404)

def unauthorized_response(
    message: str = "Unauthorized"
) -> tuple:
    """
    Create an unauthorized response
    
    Args:
        message: The error message
        
    Returns:
        tuple: (response, status_code)
    """
    return error_response(message, status_code=401)

def forbidden_response(
    message: str = "Forbidden"
) -> tuple:
    """
    Create a forbidden response
    
    Args:
        message: The error message
        
    Returns:
        tuple: (response, status_code)
    """
    return error_response(message, status_code=403)

def server_error_response(
    message: str = "Internal server error"
) -> tuple:
    """
    Create a server error response
    
    Args:
        message: The error message
        
    Returns:
        tuple: (response, status_code)
    """
    return error_response(message, status_code=500) 