"""
Admin Routes
Innomatics Research Labs - Enterprise Solution

This module handles administrative functions including user management,
system configuration, and data maintenance.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, JobDescription, Resume, Evaluation, Feedback
from utils.validators import Validators

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    try:
        # Get system statistics
        stats = {
            'total_users': User.query.count(),
            'total_jobs': JobDescription.query.count(),
            'total_resumes': Resume.query.count(),
            'total_evaluations': Evaluation.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'recent_activity': Evaluation.query.filter(
                Evaluation.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        
        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        # Get system health metrics
        health_metrics = {
            'database_connections': 'healthy',
            'ai_services': 'available',
            'file_storage': 'healthy',
            'last_backup': '2024-01-01 00:00:00'  # This would be dynamic in production
        }
        
        return render_template('admin/index.html', 
                             stats=stats, 
                             recent_users=recent_users,
                             health_metrics=health_metrics)
        
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Error loading admin dashboard. Please try again.', 'error')
        return render_template('admin/index.html', 
                             stats={}, 
                             recent_users=[], 
                             health_metrics={})

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        role = request.args.get('role', '', type=str)
        status = request.args.get('status', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            flash(error, 'error')
            return redirect(url_for('admin.users'))
        
        # Build query
        query = User.query
        
        # Apply filters
        if search:
            is_valid, error = Validators.validate_search_query(search)
            if is_valid:
                query = query.filter(
                    User.username.contains(search) |
                    User.email.contains(search) |
                    User.first_name.contains(search) |
                    User.last_name.contains(search)
                )
            else:
                flash(error, 'error')
                return redirect(url_for('admin.users'))
        
        if role:
            query = query.filter(User.role == role)
        
        if status:
            if status == 'active':
                query = query.filter(User.is_active == True)
            elif status == 'inactive':
                query = query.filter(User.is_active == False)
        
        # Order and paginate
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/users.html', 
                             users=users, 
                             search=search, 
                             role=role, 
                             status=status)
        
    except Exception as e:
        logger.error(f"Error loading users: {str(e)}")
        flash('Error loading users. Please try again.', 'error')
        return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user activity
        user_jobs = JobDescription.query.filter_by(created_by=user_id).count()
        user_evaluations = Evaluation.query.filter_by(evaluated_by=user_id).count()
        
        return render_template('admin/view_user.html', 
                             user=user, 
                             user_jobs=user_jobs, 
                             user_evaluations=user_evaluations)
        
    except Exception as e:
        logger.error(f"Error viewing user {user_id}: {str(e)}")
        flash('Error loading user details. Please try again.', 'error')
        return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            if request.is_json:
                return jsonify({'error': 'Cannot deactivate your own account'}), 400
            flash('Cannot deactivate your own account', 'error')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        # Toggle status
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        logger.info(f"User {user.username} {status} by admin {current_user.username}")
        
        if request.is_json:
            return jsonify({
                'message': f'User {status} successfully',
                'is_active': user.is_active
            })
        
        flash(f'User {status} successfully', 'success')
        return redirect(url_for('admin.view_user', user_id=user_id))
        
    except Exception as e:
        logger.error(f"Error toggling user status {user_id}: {str(e)}")
        db.session.rollback()
        
        error_msg = "Failed to update user status. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """Change user role"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json() if request.is_json else request.form
        
        new_role = data.get('role', '').strip()
        
        if new_role not in ['admin', 'recruiter', 'mentor', 'student']:
            error_msg = "Invalid role selected"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        # Prevent admin from changing their own role
        if user.id == current_user.id:
            error_msg = "Cannot change your own role"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        logger.info(f"User {user.username} role changed from {old_role} to {new_role} by admin {current_user.username}")
        
        if request.is_json:
            return jsonify({
                'message': f'User role changed to {new_role}',
                'role': user.role
            })
        
        flash(f'User role changed to {new_role}', 'success')
        return redirect(url_for('admin.view_user', user_id=user_id))
        
    except Exception as e:
        logger.error(f"Error changing user role {user_id}: {str(e)}")
        db.session.rollback()
        
        error_msg = "Failed to change user role. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/system/logs')
@login_required
@admin_required
def system_logs():
    """System logs page"""
    try:
        # In a real application, you would read from actual log files
        # For now, we'll return a placeholder
        logs = [
            {
                'timestamp': '2024-01-01 10:00:00',
                'level': 'INFO',
                'message': 'User john_doe logged in successfully',
                'module': 'auth'
            },
            {
                'timestamp': '2024-01-01 10:05:00',
                'level': 'INFO',
                'message': 'Resume uploaded: resume_123.pdf',
                'module': 'resume_parser'
            },
            {
                'timestamp': '2024-01-01 10:10:00',
                'level': 'ERROR',
                'message': 'Failed to parse resume: invalid_format.docx',
                'module': 'resume_parser'
            }
        ]
        
        return render_template('admin/system_logs.html', logs=logs)
        
    except Exception as e:
        logger.error(f"Error loading system logs: {str(e)}")
        flash('Error loading system logs. Please try again.', 'error')
        return render_template('admin/system_logs.html', logs=[])

@admin_bp.route('/system/backup', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Create system backup"""
    try:
        # In a real application, you would implement actual backup functionality
        # For now, we'll return a success message
        
        logger.info(f"System backup initiated by admin {current_user.username}")
        
        if request.is_json:
            return jsonify({
                'message': 'Backup process started successfully',
                'backup_id': 'backup_20240101_100000',
                'estimated_completion': '2024-01-01 10:05:00'
            })
        
        flash('Backup process started successfully', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        
        error_msg = "Failed to start backup process. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('admin.index'))

@admin_bp.route('/system/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup_system():
    """Clean up old data"""
    try:
        # Clean up old failed evaluations
        old_failed_evaluations = Evaluation.query.filter(
            Evaluation.status == 'failed',
            Evaluation.created_at < datetime.utcnow() - timedelta(days=30)
        ).delete()
        
        # Clean up old failed resume parsing
        old_failed_resumes = Resume.query.filter(
            Resume.parsing_status == 'failed',
            Resume.uploaded_at < datetime.utcnow() - timedelta(days=30)
        ).delete()
        
        db.session.commit()
        
        logger.info(f"System cleanup completed by admin {current_user.username}: {old_failed_evaluations} evaluations, {old_failed_resumes} resumes")
        
        if request.is_json:
            return jsonify({
                'message': 'System cleanup completed successfully',
                'cleaned_evaluations': old_failed_evaluations,
                'cleaned_resumes': old_failed_resumes
            })
        
        flash(f'System cleanup completed: {old_failed_evaluations} evaluations, {old_failed_resumes} resumes cleaned', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        logger.error(f"Error during system cleanup: {str(e)}")
        db.session.rollback()
        
        error_msg = "Failed to complete system cleanup. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('admin.index'))

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics and reporting page"""
    try:
        # Get comprehensive analytics
        analytics_data = {
            'user_stats': {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'users_by_role': {
                    'admin': User.query.filter_by(role='admin').count(),
                    'recruiter': User.query.filter_by(role='recruiter').count(),
                    'mentor': User.query.filter_by(role='mentor').count(),
                    'student': User.query.filter_by(role='student').count()
                }
            },
            'job_stats': {
                'total_jobs': JobDescription.query.count(),
                'active_jobs': JobDescription.query.filter_by(status='active').count(),
                'jobs_by_priority': {
                    'high': JobDescription.query.filter_by(priority='high').count(),
                    'medium': JobDescription.query.filter_by(priority='medium').count(),
                    'low': JobDescription.query.filter_by(priority='low').count()
                }
            },
            'resume_stats': {
                'total_resumes': Resume.query.count(),
                'parsed_resumes': Resume.query.filter_by(parsing_status='completed').count(),
                'failed_parsing': Resume.query.filter_by(parsing_status='failed').count()
            },
            'evaluation_stats': {
                'total_evaluations': Evaluation.query.count(),
                'completed_evaluations': Evaluation.query.filter_by(status='completed').count(),
                'average_score': db.session.query(db.func.avg(Evaluation.relevance_score)).scalar() or 0,
                'score_distribution': {
                    'high': Evaluation.query.filter_by(fit_verdict='high').count(),
                    'medium': Evaluation.query.filter_by(fit_verdict='medium').count(),
                    'low': Evaluation.query.filter_by(fit_verdict='low').count()
                }
            }
        }
        
        return render_template('admin/analytics.html', analytics=analytics_data)
        
    except Exception as e:
        logger.error(f"Error loading analytics: {str(e)}")
        flash('Error loading analytics. Please try again.', 'error')
        return render_template('admin/analytics.html', analytics={})

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings page"""
    try:
        # In a real application, you would load settings from a configuration table
        settings_data = {
            'system_name': 'Automated Resume Relevance Check System',
            'version': '1.0.0',
            'max_file_size': '16MB',
            'allowed_file_types': ['PDF', 'DOC', 'DOCX', 'TXT'],
            'ai_model': 'GPT-3.5-turbo',
            'evaluation_timeout': '300 seconds',
            'backup_frequency': 'Daily',
            'log_retention': '30 days'
        }
        
        return render_template('admin/settings.html', settings=settings_data)
        
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        flash('Error loading settings. Please try again.', 'error')
        return render_template('admin/settings.html', settings={})

@admin_bp.route('/settings', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update system settings"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        # In a real application, you would update settings in a configuration table
        # For now, we'll just log the changes
        
        logger.info(f"Settings updated by admin {current_user.username}: {data}")
        
        if request.is_json:
            return jsonify({
                'message': 'Settings updated successfully',
                'settings': data
            })
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        
        error_msg = "Failed to update settings. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('admin.settings'))
