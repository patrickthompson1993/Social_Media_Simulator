from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(APIError):
    """Raised when input validation fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

class DatabaseError(APIError):
    """Raised when a database operation fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=500, payload=payload)

def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    
    Args:
        app: The Flask application instance
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle APIError exceptions"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle Werkzeug HTTP exceptions"""
        response = jsonify({
            'status': 'error',
            'message': error.description,
            'code': error.code
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle all other exceptions"""
        # Log the full traceback
        logger.error(f"Unhandled exception: {str(error)}")
        logger.error(traceback.format_exc())
        
        # In production, don't expose internal error details
        if app.config.get('DEBUG', False):
            message = str(error)
        else:
            message = "An unexpected error occurred"
        
        response = jsonify({
            'status': 'error',
            'message': message
        })
        response.status_code = 500
        return response

def handle_validation_error(error):
    """
    Handle validation errors
    
    Args:
        error: The validation error
        
    Returns:
        tuple: (response, status_code)
    """
    response = jsonify({
        'status': 'error',
        'message': str(error),
        'type': 'validation_error'
    })
    return response, 400

def handle_database_error(error):
    """
    Handle database errors
    
    Args:
        error: The database error
        
    Returns:
        tuple: (response, status_code)
    """
    # Log the error
    logger.error(f"Database error: {str(error)}")
    logger.error(traceback.format_exc())
    
    response = jsonify({
        'status': 'error',
        'message': 'A database error occurred',
        'type': 'database_error'
    })
    return response, 500

def handle_not_found_error(error):
    """
    Handle not found errors
    
    Args:
        error: The not found error
        
    Returns:
        tuple: (response, status_code)
    """
    response = jsonify({
        'status': 'error',
        'message': str(error),
        'type': 'not_found'
    })
    return response, 404

def handle_authentication_error(error):
    """
    Handle authentication errors
    
    Args:
        error: The authentication error
        
    Returns:
        tuple: (response, status_code)
    """
    response = jsonify({
        'status': 'error',
        'message': str(error),
        'type': 'authentication_error'
    })
    return response, 401

def handle_authorization_error(error):
    """
    Handle authorization errors
    
    Args:
        error: The authorization error
        
    Returns:
        tuple: (response, status_code)
    """
    response = jsonify({
        'status': 'error',
        'message': str(error),
        'type': 'authorization_error'
    })
    return response, 403 