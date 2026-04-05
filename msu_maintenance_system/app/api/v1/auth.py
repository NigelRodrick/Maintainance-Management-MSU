"""
Auth API v1 Endpoints
Authentication and user management endpoints.
"""

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.api.v1 import api_v1_bp
from app.services.auth_service import AuthService
from app.domain.user import UserCreate, UserLogin, PasswordChange
from app.repositories.user_repository import UserRepository


@api_v1_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create login request
        login_data = UserLogin(**data)
        
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Authenticate user
        user, message = auth_service.authenticate_user(login_data)
        if user:
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user.dict(),
                    'access_token': access_token
                },
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create user request
        user_data = UserCreate(**data)
        
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Create user
        user, message = auth_service.create_user(user_data)
        if user:
            return jsonify({
                'success': True,
                'data': user.dict(),
                'message': message
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile."""
    try:
        current_user_id = get_jwt_identity()
        
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Get user profile
        profile = auth_service.get_user_profile(current_user_id)
        if profile:
            return jsonify({
                'success': True,
                'data': profile.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Create password change request
        password_data = PasswordChange(**data)
        
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Change password
        success, message = auth_service.change_password(current_user_id, password_data)
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/auth/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)."""
    try:
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Get users
        users = auth_service.get_all_users()
        
        return jsonify({
            'success': True,
            'data': [user.dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/auth/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID."""
    try:
        # Initialize auth service
        auth_service = AuthService(UserRepository())
        
        # Get user
        user = auth_service.get_user_by_id(user_id)
        if user:
            return jsonify({
                'success': True,
                'data': user.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
