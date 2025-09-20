"""
Routes Package for Automated Resume Relevance Check System
Innomatics Research Labs - Enterprise Solution

This package contains all route handlers for the web application.
"""

from .auth import auth_bp
from .dashboard import dashboard_bp
from .api import api_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'api_bp',
    'admin_bp'
]
