import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Secret key for JWT token generation
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

def generate_token(user_id, username, expires_in=3600):
    """
    Generate a JWT token for a user
    
    Args:
        user_id (str): The user ID
        username (str): The username
        expires_in (int): Token expiration time in seconds (default: 1 hour)
        
    Returns:
        str: The JWT token
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """
    Verify a JWT token
    
    Args:
        token (str): The JWT token
        
    Returns:
        dict: The token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    Decorator to require a valid JWT token for a route
    
    Args:
        f (function): The route function
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Check if token is in query parameters
        if not token and 'token' in request.args:
            token = request.args['token']
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        request.user_id = payload['user_id']
        request.username = payload['username']
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator to require admin privileges for a route
    
    Args:
        f (function): The route function
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Check if token is in query parameters
        if not token and 'token' in request.args:
            token = request.args['token']
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Check if user is admin
        if 'is_admin' not in payload or not payload['is_admin']:
            return jsonify({'message': 'Admin privileges required'}), 403
        
        # Add user info to request context
        request.user_id = payload['user_id']
        request.username = payload['username']
        
        return f(*args, **kwargs)
    
    return decorated 