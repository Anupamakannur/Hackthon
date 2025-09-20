"""
Database Models for Automated Resume Relevance Check System
Innomatics Research Labs - Enterprise Solution

This module defines all database models with proper relationships,
constraints, and business logic for the resume evaluation system.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSON
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for authentication and role management
    Supports multiple user types: admin, recruiter, mentor, student
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('admin', 'recruiter', 'mentor', 'student', name='user_roles'), 
                    nullable=False, default='student')
    location = db.Column(db.String(50), nullable=True)  # Hyderabad, Bangalore, Pune, Delhi NCR
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    job_descriptions = db.relationship('JobDescription', backref='created_by_user', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='evaluated_by_user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'location': self.location,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class JobDescription(db.Model):
    """
    Job Description model for storing job requirements and criteria
    """
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.Enum('full_time', 'part_time', 'contract', 'internship', name='job_types'), 
                        nullable=False, default='full_time')
    experience_level = db.Column(db.Enum('entry', 'mid', 'senior', 'lead', name='experience_levels'), 
                               nullable=False, default='entry')
    salary_range = db.Column(db.String(50), nullable=True)
    
    # Job requirements
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    skills_required = db.Column(JSON, nullable=True)  # List of required skills
    skills_preferred = db.Column(JSON, nullable=True)  # List of preferred skills
    education_required = db.Column(db.String(200), nullable=True)
    certifications_required = db.Column(JSON, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    
    # Metadata
    status = db.Column(db.Enum('active', 'inactive', 'closed', name='job_status'), 
                      default='active', nullable=False)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent', name='job_priority'), 
                        default='medium', nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='job_description', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        Index('idx_job_company_title', 'company', 'title'),
        Index('idx_job_status_created', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f'<JobDescription {self.title} at {self.company}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'department': self.department,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'salary_range': self.salary_range,
            'description': self.description,
            'requirements': self.requirements,
            'skills_required': self.skills_required,
            'skills_preferred': self.skills_preferred,
            'education_required': self.education_required,
            'certifications_required': self.certifications_required,
            'experience_years': self.experience_years,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }

class Resume(db.Model):
    """
    Resume model for storing parsed resume data
    """
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    
    # Parsed resume data
    candidate_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Professional information
    summary = db.Column(db.Text, nullable=True)
    skills = db.Column(JSON, nullable=True)  # List of skills
    experience = db.Column(JSON, nullable=True)  # List of work experiences
    education = db.Column(JSON, nullable=True)  # List of educational background
    certifications = db.Column(JSON, nullable=True)  # List of certifications
    projects = db.Column(JSON, nullable=True)  # List of projects
    languages = db.Column(JSON, nullable=True)  # List of languages
    
    # Parsing metadata
    parsing_status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='parsing_status'), 
                             default='pending', nullable=False)
    parsing_errors = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)  # Parsing confidence
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    parsed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    evaluations = db.relationship('Evaluation', backref='resume', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        Index('idx_resume_email', 'email'),
        Index('idx_resume_parsing_status', 'parsing_status'),
    )
    
    def __repr__(self):
        return f'<Resume {self.original_filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'candidate_name': self.candidate_name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'summary': self.summary,
            'skills': self.skills,
            'experience': self.experience,
            'education': self.education,
            'certifications': self.certifications,
            'projects': self.projects,
            'languages': self.languages,
            'parsing_status': self.parsing_status,
            'confidence_score': self.confidence_score,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'parsed_at': self.parsed_at.isoformat() if self.parsed_at else None
        }

class Evaluation(db.Model):
    """
    Evaluation model for storing resume-job matching results
    """
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    evaluated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Scoring
    relevance_score = db.Column(db.Float, nullable=False)  # 0-100
    fit_verdict = db.Column(db.Enum('high', 'medium', 'low', name='fit_verdicts'), 
                           nullable=False)
    
    # Detailed scoring breakdown
    skills_match_score = db.Column(db.Float, nullable=True)
    experience_match_score = db.Column(db.Float, nullable=True)
    education_match_score = db.Column(db.Float, nullable=True)
    certification_match_score = db.Column(db.Float, nullable=True)
    project_match_score = db.Column(db.Float, nullable=True)
    
    # Analysis results
    matched_skills = db.Column(JSON, nullable=True)
    missing_skills = db.Column(JSON, nullable=True)
    matched_experience = db.Column(JSON, nullable=True)
    missing_experience = db.Column(JSON, nullable=True)
    strengths = db.Column(JSON, nullable=True)
    weaknesses = db.Column(JSON, nullable=True)
    
    # AI Analysis
    ai_analysis = db.Column(db.Text, nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    
    # Status and timestamps
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='evaluation_status'), 
                      default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('relevance_score >= 0 AND relevance_score <= 100', name='check_relevance_score'),
        Index('idx_evaluation_resume_job', 'resume_id', 'job_description_id'),
        Index('idx_evaluation_score', 'relevance_score'),
        Index('idx_evaluation_verdict', 'fit_verdict'),
    )
    
    def __repr__(self):
        return f'<Evaluation Resume {self.resume_id} vs Job {self.job_description_id}: {self.relevance_score}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_description_id': self.job_description_id,
            'evaluated_by': self.evaluated_by,
            'relevance_score': self.relevance_score,
            'fit_verdict': self.fit_verdict,
            'skills_match_score': self.skills_match_score,
            'experience_match_score': self.experience_match_score,
            'education_match_score': self.education_match_score,
            'certification_match_score': self.certification_match_score,
            'project_match_score': self.project_match_score,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'matched_experience': self.matched_experience,
            'missing_experience': self.missing_experience,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'ai_analysis': self.ai_analysis,
            'ai_confidence': self.ai_confidence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Feedback(db.Model):
    """
    Feedback model for storing personalized improvement suggestions
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    
    # Feedback content
    overall_feedback = db.Column(db.Text, nullable=False)
    skill_improvements = db.Column(JSON, nullable=True)
    experience_improvements = db.Column(JSON, nullable=True)
    education_improvements = db.Column(JSON, nullable=True)
    certification_suggestions = db.Column(JSON, nullable=True)
    project_suggestions = db.Column(JSON, nullable=True)
    
    # Actionable recommendations
    immediate_actions = db.Column(JSON, nullable=True)
    long_term_goals = db.Column(JSON, nullable=True)
    resource_recommendations = db.Column(JSON, nullable=True)
    
    # Feedback metadata
    feedback_type = db.Column(db.Enum('automatic', 'manual', 'hybrid', name='feedback_types'), 
                            default='automatic', nullable=False)
    priority = db.Column(db.Enum('low', 'medium', 'high', name='feedback_priority'), 
                        default='medium', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback for Evaluation {self.evaluation_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'overall_feedback': self.overall_feedback,
            'skill_improvements': self.skill_improvements,
            'experience_improvements': self.experience_improvements,
            'education_improvements': self.education_improvements,
            'certification_suggestions': self.certification_suggestions,
            'project_suggestions': self.project_suggestions,
            'immediate_actions': self.immediate_actions,
            'long_term_goals': self.long_term_goals,
            'resource_recommendations': self.resource_recommendations,
            'feedback_type': self.feedback_type,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
