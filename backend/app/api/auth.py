"""
Authentication API routes
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError

from app import db
from app.models import User

bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    display_name = data.get('displayName', '').strip()

    # Validate email
    try:
        valid = validate_email(email)
        email = valid.normalized
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 400

    # Validate password
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Create user
    user = User(
        email=email,
        display_name=display_name or None,
        preferences={'font': 'Inter', 'fontSize': 16}
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Log the user in
    login_user(user, remember=True)

    return jsonify({
        'message': 'Account created successfully',
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Log in a user"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', True)

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Log in
    login_user(user, remember=remember)

    # Save password hash if rehashed
    db.session.commit()

    return jsonify({
        'message': 'Logged in successfully',
        'user': user.to_dict()
    })


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})


@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current logged-in user info"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({
        'authenticated': False,
        'user': None
    })


@bp.route('/me', methods=['PATCH'])
@login_required
def update_current_user():
    """Update current user's profile"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update display name
    if 'displayName' in data:
        current_user.display_name = data['displayName'].strip() or None

    # Update preferences (merge with existing)
    if 'preferences' in data and isinstance(data['preferences'], dict):
        if current_user.preferences is None:
            current_user.preferences = {}
        current_user.preferences.update(data['preferences'])

    db.session.commit()

    return jsonify({
        'message': 'Profile updated',
        'user': current_user.to_dict()
    })


@bp.route('/me/password', methods=['POST'])
@login_required
def change_password():
    """Change current user's password"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400

    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'})
