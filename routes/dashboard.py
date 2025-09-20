"""
Dashboard Routes
Innomatics Research Labs - Enterprise Solution

This module handles the main dashboard functionality including
resume uploads, job management, and evaluation results.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, JobDescription, Resume, Evaluation, Feedback
from services.resume_parser import ResumeParser
from services.job_analyzer import JobAnalyzer
from services.relevance_scorer import RelevanceScorer
from services.feedback_generator import FeedbackGenerator
from utils.file_handler import FileHandler
from utils.validators import Validators

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize services
resume_parser = ResumeParser()
job_analyzer = JobAnalyzer()
relevance_scorer = RelevanceScorer()
feedback_generator = FeedbackGenerator()

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    try:
        # Get recent activity statistics
        stats = {
            'total_jobs': JobDescription.query.count(),
            'total_resumes': Resume.query.count(),
            'total_evaluations': Evaluation.query.count(),
            'recent_evaluations': Evaluation.query.filter(
                Evaluation.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        
        # Get recent evaluations
        recent_evaluations = Evaluation.query.order_by(
            Evaluation.created_at.desc()
        ).limit(10).all()
        
        # Get recent job descriptions
        recent_jobs = JobDescription.query.order_by(
            JobDescription.created_at.desc()
        ).limit(5).all()
        
        return render_template('dashboard/index.html', 
                             stats=stats,
                             recent_evaluations=recent_evaluations,
                             recent_jobs=recent_jobs)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard. Please try again.', 'error')
        return render_template('dashboard/index.html', 
                             stats={}, 
                             recent_evaluations=[], 
                             recent_jobs=[])

@dashboard_bp.route('/jobs')
@login_required
def jobs():
    """Job descriptions management page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            flash(error, 'error')
            return redirect(url_for('dashboard.jobs'))
        
        # Build query
        query = JobDescription.query
        
        # Apply filters
        if search:
            is_valid, error = Validators.validate_search_query(search)
            if is_valid:
                query = query.filter(
                    JobDescription.title.contains(search) |
                    JobDescription.company.contains(search) |
                    JobDescription.description.contains(search)
                )
            else:
                flash(error, 'error')
                return redirect(url_for('dashboard.jobs'))
        
        if status:
            query = query.filter(JobDescription.status == status)
        
        # Order and paginate
        jobs = query.order_by(JobDescription.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('dashboard/jobs.html', jobs=jobs, search=search, status=status)
        
    except Exception as e:
        logger.error(f"Error loading jobs: {str(e)}")
        flash('Error loading jobs. Please try again.', 'error')
        return redirect(url_for('dashboard.jobs'))

@dashboard_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def create_job():
    """Create new job description"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Extract form data
        job_data = {
            'title': data.get('title', '').strip(),
            'company': data.get('company', '').strip(),
            'location': data.get('location', '').strip(),
            'department': data.get('department', '').strip(),
            'job_type': data.get('job_type', 'full_time'),
            'experience_level': data.get('experience_level', 'entry'),
            'salary_range': data.get('salary_range', '').strip(),
            'description': data.get('description', '').strip(),
            'requirements': data.get('requirements', '').strip(),
            'education_required': data.get('education_required', '').strip(),
            'experience_years': data.get('experience_years', type=int),
            'deadline': data.get('deadline', type=str),
            'priority': data.get('priority', 'medium')
        }
        
        # Validate job data
        is_valid, error = Validators.validate_job_description(job_data)
        if not is_valid:
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return render_template('dashboard/create_job.html')
        
        try:
            # Analyze job description
            analysis_result = job_analyzer.analyze_job_description(
                job_data['description'], 
                job_data['requirements']
            )
            
            # Create job description
            job = JobDescription(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                department=job_data['department'],
                job_type=job_data['job_type'],
                experience_level=job_data['experience_level'],
                salary_range=job_data['salary_range'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                skills_required=analysis_result.get('skills_required', []),
                skills_preferred=analysis_result.get('skills_preferred', []),
                education_required=job_data['education_required'],
                experience_years=job_data['experience_years'],
                created_by=current_user.id,
                priority=job_data['priority']
            )
            
            if job_data['deadline']:
                job.deadline = datetime.fromisoformat(job_data['deadline'])
            
            db.session.add(job)
            db.session.commit()
            
            logger.info(f"Job created: {job.title} at {job.company}")
            
            if request.is_json:
                return jsonify({
                    'message': 'Job created successfully',
                    'job': job.to_dict(),
                    'redirect_url': url_for('dashboard.jobs')
                })
            
            flash('Job description created successfully!', 'success')
            return redirect(url_for('dashboard.jobs'))
            
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            db.session.rollback()
            
            error_msg = "Failed to create job description. Please try again."
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
    
    return render_template('dashboard/create_job.html')

@dashboard_bp.route('/resumes')
@login_required
def resumes():
    """Resume management page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            flash(error, 'error')
            return redirect(url_for('dashboard.resumes'))
        
        # Build query
        query = Resume.query
        
        # Apply filters
        if search:
            is_valid, error = Validators.validate_search_query(search)
            if is_valid:
                query = query.filter(
                    Resume.candidate_name.contains(search) |
                    Resume.email.contains(search) |
                    Resume.original_filename.contains(search)
                )
            else:
                flash(error, 'error')
                return redirect(url_for('dashboard.resumes'))
        
        if status:
            query = query.filter(Resume.parsing_status == status)
        
        # Order and paginate
        resumes = query.order_by(Resume.uploaded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('dashboard/resumes.html', resumes=resumes, search=search, status=status)
        
    except Exception as e:
        logger.error(f"Error loading resumes: {str(e)}")
        flash('Error loading resumes. Please try again.', 'error')
        return redirect(url_for('dashboard.resumes'))

@dashboard_bp.route('/resumes/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload and parse resume"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                if request.is_json:
                    return jsonify({'error': 'No file uploaded'}), 400
                flash('No file uploaded', 'error')
                return redirect(url_for('dashboard.upload_resume'))
            
            file = request.files['file']
            if file.filename == '':
                if request.is_json:
                    return jsonify({'error': 'No file selected'}), 400
                flash('No file selected', 'error')
                return redirect(url_for('dashboard.upload_resume'))
            
            # Initialize file handler
            file_handler = FileHandler(current_app.config['UPLOAD_FOLDER'])
            
            # Validate file
            is_valid, error = file_handler.validate_file(file)
            if not is_valid:
                if request.is_json:
                    return jsonify({'error': error}), 400
                flash(error, 'error')
                return redirect(url_for('dashboard.upload_resume'))
            
            # Save file
            file_path, error = file_handler.save_file(file)
            if not file_path:
                if request.is_json:
                    return jsonify({'error': error}), 500
                flash(error, 'error')
                return redirect(url_for('dashboard.upload_resume'))
            
            # Get file info
            file_info = file_handler.get_file_info(file_path)
            
            # Create resume record
            resume = Resume(
                filename=os.path.basename(file_path),
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_info['file_size'],
                file_type=file_info['file_type'],
                parsing_status='processing'
            )
            
            db.session.add(resume)
            db.session.commit()
            
            # Parse resume in background (in production, use Celery)
            try:
                parsed_data = resume_parser.parse_resume(file_path, file_info['file_type'].split('/')[-1])
                
                # Update resume with parsed data
                resume.candidate_name = parsed_data.get('candidate_name')
                resume.email = parsed_data.get('email')
                resume.phone = parsed_data.get('phone')
                resume.location = parsed_data.get('location')
                resume.summary = parsed_data.get('summary')
                resume.skills = parsed_data.get('skills', [])
                resume.experience = parsed_data.get('experience', [])
                resume.education = parsed_data.get('education', [])
                resume.certifications = parsed_data.get('certifications', [])
                resume.projects = parsed_data.get('projects', [])
                resume.languages = parsed_data.get('languages', [])
                resume.parsing_status = 'completed'
                resume.parsed_at = datetime.utcnow()
                resume.confidence_score = parsed_data.get('parsing_metadata', {}).get('confidence_score', 0.0)
                
                db.session.commit()
                
                logger.info(f"Resume parsed successfully: {resume.original_filename}")
                
                if request.is_json:
                    return jsonify({
                        'message': 'Resume uploaded and parsed successfully',
                        'resume': resume.to_dict(),
                        'redirect_url': url_for('dashboard.resumes')
                    })
                
                flash('Resume uploaded and parsed successfully!', 'success')
                return redirect(url_for('dashboard.resumes'))
                
            except Exception as e:
                logger.error(f"Error parsing resume: {str(e)}")
                resume.parsing_status = 'failed'
                resume.parsing_errors = str(e)
                db.session.commit()
                
                error_msg = f"Resume uploaded but parsing failed: {str(e)}"
                if request.is_json:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'error')
                return redirect(url_for('dashboard.resumes'))
            
        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            db.session.rollback()
            
            error_msg = "Failed to upload resume. Please try again."
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
    
    return render_template('dashboard/upload_resume.html')

@dashboard_bp.route('/evaluations')
@login_required
def evaluations():
    """Evaluation results page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        job_id = request.args.get('job_id', type=int)
        verdict = request.args.get('verdict', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            flash(error, 'error')
            return redirect(url_for('dashboard.evaluations'))
        
        # Build query
        query = Evaluation.query
        
        # Apply filters
        if job_id:
            query = query.filter(Evaluation.job_description_id == job_id)
        
        if verdict:
            query = query.filter(Evaluation.fit_verdict == verdict)
        
        # Order and paginate
        evaluations = query.order_by(Evaluation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get job options for filter
        jobs = JobDescription.query.filter_by(status='active').all()
        
        return render_template('dashboard/evaluations.html', 
                             evaluations=evaluations, 
                             jobs=jobs,
                             job_id=job_id,
                             verdict=verdict)
        
    except Exception as e:
        logger.error(f"Error loading evaluations: {str(e)}")
        flash('Error loading evaluations. Please try again.', 'error')
        return redirect(url_for('dashboard.evaluations'))

@dashboard_bp.route('/evaluate', methods=['POST'])
@login_required
def evaluate_resume():
    """Evaluate resume against job description"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        resume_id = data.get('resume_id', type=int)
        job_id = data.get('job_id', type=int)
        
        if not resume_id or not job_id:
            error_msg = "Resume ID and Job ID are required"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.evaluations'))
        
        # Get resume and job
        resume = Resume.query.get_or_404(resume_id)
        job = JobDescription.query.get_or_404(job_id)
        
        if resume.parsing_status != 'completed':
            error_msg = "Resume must be parsed before evaluation"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.evaluations'))
        
        # Check if evaluation already exists
        existing_evaluation = Evaluation.query.filter_by(
            resume_id=resume_id,
            job_description_id=job_id
        ).first()
        
        if existing_evaluation:
            error_msg = "Evaluation already exists for this resume and job"
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.evaluations'))
        
        # Create evaluation record
        evaluation = Evaluation(
            resume_id=resume_id,
            job_description_id=job_id,
            evaluated_by=current_user.id,
            status='processing'
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        # Perform evaluation
        try:
            # Prepare data for evaluation
            resume_data = resume.to_dict()
            job_data = job.to_dict()
            
            # Calculate relevance score
            scoring_result = relevance_scorer.calculate_relevance_score(resume_data, job_data)
            
            # Update evaluation with results
            evaluation.relevance_score = scoring_result['relevance_score']
            evaluation.fit_verdict = scoring_result['fit_verdict']
            evaluation.skills_match_score = scoring_result['skills_match_score']
            evaluation.experience_match_score = scoring_result['experience_match_score']
            evaluation.education_match_score = scoring_result['education_match_score']
            evaluation.certification_match_score = scoring_result['certification_match_score']
            evaluation.project_match_score = scoring_result['project_match_score']
            evaluation.matched_skills = scoring_result['matched_skills']
            evaluation.missing_skills = scoring_result['missing_skills']
            evaluation.strengths = scoring_result['strengths']
            evaluation.weaknesses = scoring_result['weaknesses']
            evaluation.ai_analysis = scoring_result['ai_analysis']
            evaluation.ai_confidence = scoring_result['ai_confidence']
            evaluation.status = 'completed'
            evaluation.completed_at = datetime.utcnow()
            
            # Generate feedback
            feedback_data = feedback_generator.generate_feedback(scoring_result, resume_data, job_data)
            
            feedback = Feedback(
                evaluation_id=evaluation.id,
                overall_feedback=feedback_data['overall_feedback'],
                skill_improvements=feedback_data['skill_improvements'],
                experience_improvements=feedback_data['experience_improvements'],
                education_improvements=feedback_data['education_improvements'],
                certification_suggestions=feedback_data['certification_suggestions'],
                project_suggestions=feedback_data['project_suggestions'],
                immediate_actions=feedback_data['immediate_actions'],
                long_term_goals=feedback_data['long_term_goals'],
                resource_recommendations=feedback_data['resource_recommendations'],
                feedback_type=feedback_data['feedback_type'],
                priority=feedback_data['priority']
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            logger.info(f"Evaluation completed: Resume {resume_id} vs Job {job_id} - {evaluation.relevance_score}%")
            
            if request.is_json:
                return jsonify({
                    'message': 'Evaluation completed successfully',
                    'evaluation': evaluation.to_dict(),
                    'feedback': feedback.to_dict(),
                    'redirect_url': url_for('dashboard.evaluations')
                })
            
            flash('Evaluation completed successfully!', 'success')
            return redirect(url_for('dashboard.evaluations'))
            
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            evaluation.status = 'failed'
            db.session.commit()
            
            error_msg = f"Evaluation failed: {str(e)}"
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.evaluations'))
        
    except Exception as e:
        logger.error(f"Error starting evaluation: {str(e)}")
        db.session.rollback()
        
        error_msg = "Failed to start evaluation. Please try again."
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('dashboard.evaluations'))

@dashboard_bp.route('/evaluations/<int:evaluation_id>')
@login_required
def view_evaluation(evaluation_id):
    """View detailed evaluation results"""
    try:
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        feedback = Feedback.query.filter_by(evaluation_id=evaluation_id).first()
        
        return render_template('dashboard/view_evaluation.html', 
                             evaluation=evaluation, 
                             feedback=feedback)
        
    except Exception as e:
        logger.error(f"Error viewing evaluation: {str(e)}")
        flash('Error loading evaluation details. Please try again.', 'error')
        return redirect(url_for('dashboard.evaluations'))
