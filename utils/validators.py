"""
Validation Utilities
Innomatics Research Labs - Enterprise Solution

This module provides comprehensive validation functions for user inputs,
data integrity, and business rule validation.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import email_validator

logger = logging.getLogger(__name__)

class Validators:
    """
    Comprehensive validation utilities for the application
    """
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address format and existence
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not email or not isinstance(email, str):
                return False, "Email is required"
            
            # Use email-validator for comprehensive validation
            email_validator.validate_email(email)
            return True, ""
            
        except email_validator.EmailNotValidError as e:
            return False, f"Invalid email format: {str(e)}"
        except Exception as e:
            logger.error(f"Error validating email: {str(e)}")
            return False, "Email validation failed"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Phone is optional
        
        if not isinstance(phone, str):
            return False, "Phone number must be a string"
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (7-15 digits)
        if len(digits_only) < 7 or len(digits_only) > 15:
            return False, "Phone number must be between 7 and 15 digits"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not isinstance(username, str):
            return False, "Username is required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        # Check for valid characters (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        # Check if it starts with a letter
        if not re.match(r'^[a-zA-Z]', username):
            return False, "Username must start with a letter"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """
        Validate name fields (first name, last name, etc.)
        
        Args:
            name: Name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not isinstance(name, str):
            return False, f"{field_name} is required"
        
        if len(name.strip()) < 2:
            return False, f"{field_name} must be at least 2 characters long"
        
        if len(name.strip()) > 50:
            return False, f"{field_name} must be less than 50 characters"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name.strip()):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    @staticmethod
    def validate_job_description(job_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate job description data
        
        Args:
            job_data: Job description data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['title', 'company', 'description', 'requirements']
        
        for field in required_fields:
            if not job_data.get(field):
                return False, f"{field.title()} is required"
        
        # Validate title length
        if len(job_data['title']) > 200:
            return False, "Job title must be less than 200 characters"
        
        # Validate company name
        if len(job_data['company']) > 100:
            return False, "Company name must be less than 100 characters"
        
        # Validate description length
        if len(job_data['description']) < 50:
            return False, "Job description must be at least 50 characters long"
        
        if len(job_data['description']) > 10000:
            return False, "Job description must be less than 10,000 characters"
        
        # Validate requirements length
        if len(job_data['requirements']) < 20:
            return False, "Job requirements must be at least 20 characters long"
        
        if len(job_data['requirements']) > 5000:
            return False, "Job requirements must be less than 5,000 characters"
        
        return True, ""
    
    @staticmethod
    def validate_resume_data(resume_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate parsed resume data
        
        Args:
            resume_data: Resume data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for essential fields
        if not resume_data.get('candidate_name') and not resume_data.get('email'):
            return False, "Resume must contain either candidate name or email"
        
        # Validate email if present
        if resume_data.get('email'):
            is_valid, error = Validators.validate_email(resume_data['email'])
            if not is_valid:
                return False, f"Invalid email in resume: {error}"
        
        # Validate phone if present
        if resume_data.get('phone'):
            is_valid, error = Validators.validate_phone(resume_data['phone'])
            if not is_valid:
                return False, f"Invalid phone in resume: {error}"
        
        # Check for skills or experience
        if not resume_data.get('skills') and not resume_data.get('experience'):
            return False, "Resume must contain either skills or work experience"
        
        return True, ""
    
    @staticmethod
    def validate_evaluation_data(evaluation_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate evaluation data
        
        Args:
            evaluation_data: Evaluation data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required fields
        required_fields = ['relevance_score', 'fit_verdict']
        
        for field in required_fields:
            if field not in evaluation_data:
                return False, f"{field} is required"
        
        # Validate relevance score
        relevance_score = evaluation_data['relevance_score']
        if not isinstance(relevance_score, (int, float)):
            return False, "Relevance score must be a number"
        
        if not 0 <= relevance_score <= 100:
            return False, "Relevance score must be between 0 and 100"
        
        # Validate fit verdict
        fit_verdict = evaluation_data['fit_verdict']
        if fit_verdict not in ['high', 'medium', 'low']:
            return False, "Fit verdict must be 'high', 'medium', or 'low'"
        
        return True, ""
    
    @staticmethod
    def validate_file_upload(file_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate file upload data
        
        Args:
            file_data: File upload data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required fields
        if not file_data.get('filename'):
            return False, "Filename is required"
        
        if not file_data.get('file_size'):
            return False, "File size is required"
        
        # Validate file size
        file_size = file_data['file_size']
        if not isinstance(file_size, int) or file_size <= 0:
            return False, "File size must be a positive integer"
        
        max_size = 16 * 1024 * 1024  # 16MB
        if file_size > max_size:
            return False, f"File size must be less than {max_size // (1024*1024)}MB"
        
        # Validate file type
        filename = file_data['filename']
        if not isinstance(filename, str):
            return False, "Filename must be a string"
        
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        return True, ""
    
    @staticmethod
    def validate_pagination_params(page: int, per_page: int) -> Tuple[bool, str]:
        """
        Validate pagination parameters
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(page, int) or page < 1:
            return False, "Page must be a positive integer"
        
        if not isinstance(per_page, int) or per_page < 1:
            return False, "Per page must be a positive integer"
        
        if per_page > 100:
            return False, "Per page must be less than or equal to 100"
        
        return True, ""
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """
        Validate search query
        
        Args:
            query: Search query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not isinstance(query, str):
            return False, "Search query is required"
        
        if len(query.strip()) < 2:
            return False, "Search query must be at least 2 characters long"
        
        if len(query.strip()) > 200:
            return False, "Search query must be less than 200 characters"
        
        # Check for potentially malicious patterns
        malicious_patterns = ['<script', 'javascript:', 'vbscript:', 'onload=']
        query_lower = query.lower()
        for pattern in malicious_patterns:
            if pattern in query_lower:
                return False, "Search query contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent XSS attacks
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags and their content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: and vbscript: protocols
        text = re.sub(r'(javascript|vbscript):', '', text, flags=re.IGNORECASE)
        
        # Remove event handlers
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
        """
        Validate date range
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not start_date or not end_date:
                return False, "Both start and end dates are required"
            
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                return False, "Start date must be before end date"
            
            # Check if dates are not too far in the past or future
            today = date.today()
            if start < today.replace(year=today.year - 10):
                return False, "Start date cannot be more than 10 years ago"
            
            if end > today.replace(year=today.year + 1):
                return False, "End date cannot be more than 1 year in the future"
            
            return True, ""
            
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
        except Exception as e:
            logger.error(f"Error validating date range: {str(e)}")
            return False, "Date validation failed"
