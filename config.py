"""
Configuration Settings
Innomatics Research Labs - Enterprise Solution

This module contains configuration settings for different environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///resume_evaluator.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # AI/ML settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-3.5-turbo'
    
    # Redis settings (for caching and background tasks)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery settings (for background tasks)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Evaluation settings
    EVALUATION_TIMEOUT = int(os.environ.get('EVALUATION_TIMEOUT') or 300)  # 5 minutes
    BATCH_EVALUATION_LIMIT = int(os.environ.get('BATCH_EVALUATION_LIMIT') or 50)
    
    # Scoring weights
    SCORING_WEIGHTS = {
        'skills_match': 0.35,
        'experience_match': 0.25,
        'education_match': 0.15,
        'certification_match': 0.10,
        'project_match': 0.10,
        'semantic_similarity': 0.05
    }
    
    # File processing settings
    PARSING_TIMEOUT = int(os.environ.get('PARSING_TIMEOUT') or 60)  # 1 minute
    MAX_CONCURRENT_PARSING = int(os.environ.get('MAX_CONCURRENT_PARSING') or 5)
    
    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)  # 5 minutes
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'memory://'
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # API settings
    API_RATE_LIMIT = "1000 per hour"
    API_PAGE_SIZE = 20
    
    # Backup settings
    BACKUP_FOLDER = os.environ.get('BACKUP_FOLDER') or 'backups'
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS') or 30)
    
    # Monitoring settings
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'false').lower() in ['true', 'on', '1']
    METRICS_PORT = int(os.environ.get('METRICS_PORT') or 9090)
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///resume_evaluator_dev.db'
    
    # Enable detailed logging
    LOG_LEVEL = 'DEBUG'
    
    # Disable CSRF for development
    WTF_CSRF_ENABLED = False
    
    # Use memory cache for development
    CACHE_TYPE = 'simple'

class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use memory cache for testing
    CACHE_TYPE = 'simple'
    
    # Disable background tasks for testing
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/resume_evaluator'
    
    # Use Redis cache in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379/1'
    
    # Enable security features
    WTF_CSRF_ENABLED = True
    
    # Use file logging in production
    LOG_LEVEL = 'WARNING'
    
    # Enable metrics
    ENABLE_METRICS = True
    
    @classmethod
    def init_app(cls, app):
        """Initialize production app"""
        Config.init_app(app)
        
        # Log to file
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/resume_evaluator.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Resume Evaluator startup')

class DockerConfig(ProductionConfig):
    """Docker configuration"""
    
    # Override database URL for Docker
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/resume_evaluator'
    
    # Override Redis URL for Docker
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://redis:6379/0'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}
