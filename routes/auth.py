"""
Authentication Routes
Innomatics Research Labs - Enterprise Solution

This module handles user authentication, registration, and session management.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils.validators import Validators

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Validate input
        if not username or not password:
            error_msg = "Username and password are required"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                error_msg = "Account is deactivated. Please contact administrator."
                if request.is_json:
                    return jsonify({'error': error_msg}), 403
                flash(error_msg, 'error')
                return render_template('auth/login.html')
            
            # Update last login
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Login user
            login_user(user, remember=remember)
            
            logger.info(f"User {username} logged in successfully")
            
            if request.is_json:
                return jsonify({
                    'message': 'Login successful',
                    'redirect_url': url_for('dashboard.index'),
                    'user': user.to_dict()
                })
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            error_msg = "Invalid username or password"
            if request.is_json:
                return jsonify({'error': error_msg}), 401
            flash(error_msg, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Extract form data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', 'student')
        location = data.get('location', '').strip()
        
        # Validate inputs
        errors = []
        
        # Validate username
        is_valid, error = Validators.validate_username(username)
        if not is_valid:
            errors.append(error)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            errors.append("Username already exists")
        
        # Validate email
        is_valid, error = Validators.validate_email(email)
        if not is_valid:
            errors.append(error)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append("Email already exists")
        
        # Validate password
        is_valid, error = Validators.validate_password(password)
        if not is_valid:
            errors.append(error)
        
        # Check password confirmation
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        # Validate names
        is_valid, error = Validators.validate_name(first_name, "First name")
        if not is_valid:
            errors.append(error)
        
        is_valid, error = Validators.validate_name(last_name, "Last name")
        if not is_valid:
            errors.append(error)
        
        # Validate role
        if role not in ['admin', 'recruiter', 'mentor', 'student']:
            errors.append("Invalid role selected")
        
        if errors:
            if request.is_json:
                return jsonify({'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                role=role,
                location=location
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username} ({role})")
            
            if request.is_json:
                return jsonify({
                    'message': 'Registration successful',
                    'redirect_url': url_for('auth.login')
                })
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.session.rollback()
            
            error_msg = "Registration failed. Please try again."
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    username = current_user.username
    logout_user()
    
    logger.info(f"User {username} logged out")
    
    if request.is_json:
        return jsonify({
            'message': 'Logout successful',
            'redirect_url': url_for('auth.login')
        })
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json() if request.is_json else request.form
    
    # Extract form data
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    location = data.get('location', '').strip()
    
    # Validate inputs
    errors = []
    
    # Validate names
    is_valid, error = Validators.validate_name(first_name, "First name")
    if not is_valid:
        errors.append(error)
    
    is_valid, error = Validators.validate_name(last_name, "Last name")
    if not is_valid:
        errors.append(error)
    
    # Validate email
    is_valid, error = Validators.validate_email(email)
    if not is_valid:
        errors.append(error)
    
    # Check if email is already taken by another user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        errors.append("Email already exists")
    
    if errors:
        if request.is_json:
            return jsonify({'errors': errors}), 400
        for error in errors:
            flash(error, 'error')
        return render_template('auth/profile.html', user=current_user)
    
    # Update user profile
    try:
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.location = location
        
        db.session.commit()
        
        logger.info(f"User {current_user.username} updated profile")
        
        if request.is_json:
            return jsonify({
                'message': 'Profile updated successfully',
                'user': current_user.to_dict()
            })
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.session.rollback()
        
        error_msg = "Profile update failed. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    data = request.get_json() if request.is_json else request.form
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validate inputs
    errors = []
    
    # Check current password
    if not check_password_hash(current_user.password_hash, current_password):
        errors.append("Current password is incorrect")
    
    # Validate new password
    is_valid, error = Validators.validate_password(new_password)
    if not is_valid:
        errors.append(error)
    
    # Check password confirmation
    if new_password != confirm_password:
        errors.append("New passwords do not match")
    
    if errors:
        if request.is_json:
            return jsonify({'errors': errors}), 400
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('auth.profile'))
    
    # Update password
    try:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        logger.info(f"User {current_user.username} changed password")
        
        if request.is_json:
            return jsonify({'message': 'Password changed successfully'})
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.session.rollback()
        
        error_msg = "Password change failed. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('auth.profile'))
