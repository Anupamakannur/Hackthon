"""
File Handler Utility
Innomatics Research Labs - Enterprise Solution

This module provides secure file handling capabilities for resume uploads
and document processing with proper validation and security measures.
"""

import os
import hashlib
import logging
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import magic

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Secure file handler for resume uploads and processing
    """
    
    def __init__(self, upload_folder: str, max_file_size: int = 16 * 1024 * 1024):
        """
        Initialize file handler
        
        Args:
            upload_folder: Directory to store uploaded files
            max_file_size: Maximum file size in bytes (default: 16MB)
        """
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
        self.allowed_mime_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        }
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        Validate uploaded file for security and format
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            if file.content_length and file.content_length > self.max_file_size:
                return False, f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
            
            # Check file extension
            if not self._is_allowed_extension(file.filename):
                return False, f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            
            # Check MIME type for security
            file.seek(0)  # Reset file pointer
            mime_type = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)  # Reset file pointer again
            
            if mime_type not in self.allowed_mime_types:
                return False, f"File MIME type not allowed: {mime_type}"
            
            # Check for malicious content (basic check)
            if self._contains_malicious_content(file):
                return False, "File contains potentially malicious content"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return False, "File validation failed"
    
    def save_file(self, file: FileStorage) -> Tuple[Optional[str], str]:
        """
        Save uploaded file securely
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (file_path, error_message)
        """
        try:
            # Generate secure filename
            filename = secure_filename(file.filename)
            if not filename:
                return None, "Invalid filename"
            
            # Generate unique filename to prevent conflicts
            file_hash = hashlib.md5(file.read()).hexdigest()
            file.seek(0)  # Reset file pointer
            
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{file_hash[:8]}{ext}"
            
            # Save file
            file_path = os.path.join(self.upload_folder, unique_filename)
            file.save(file_path)
            
            # Verify file was saved correctly
            if not os.path.exists(file_path):
                return None, "Failed to save file"
            
            return file_path, ""
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return None, f"Failed to save file: {str(e)}"
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        try:
            if not os.path.exists(file_path):
                return {}
            
            stat = os.stat(file_path)
            
            return {
                'filename': os.path.basename(file_path),
                'file_size': stat.st_size,
                'file_type': self._get_file_type(file_path),
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {}
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file safely
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def _is_allowed_extension(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in self.allowed_extensions
    
    def _contains_malicious_content(self, file: FileStorage) -> bool:
        """
        Basic check for malicious content
        
        Args:
            file: File object to check
            
        Returns:
            True if potentially malicious, False otherwise
        """
        try:
            # Read first 1KB of file
            file.seek(0)
            content = file.read(1024)
            file.seek(0)  # Reset file pointer
            
            # Check for common malicious patterns
            malicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'<iframe',
                b'<object',
                b'<embed',
                b'<form',
                b'<input',
                b'<meta',
                b'<link'
            ]
            
            content_lower = content.lower()
            for pattern in malicious_patterns:
                if pattern in content_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for malicious content: {str(e)}")
            return False
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type using python-magic"""
        try:
            mime_type = magic.from_file(file_path, mime=True)
            return mime_type
        except Exception as e:
            logger.warning(f"Error getting file type: {str(e)}")
            return 'unknown'
