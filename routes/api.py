"""
RESTful API Routes
Innomatics Research Labs - Enterprise Solution

This module provides RESTful API endpoints for system integration
and external access to the resume evaluation system.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, JobDescription, Resume, Evaluation, Feedback, User
from services.resume_parser import ResumeParser
from services.job_analyzer import JobAnalyzer
from services.relevance_scorer import RelevanceScorer
from services.feedback_generator import FeedbackGenerator
from utils.file_handler import FileHandler
from utils.validators import Validators

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
resume_parser = ResumeParser()
job_analyzer = JobAnalyzer()
relevance_scorer = RelevanceScorer()
feedback_generator = FeedbackGenerator()

@api_bp.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': 'connected',
            'ai_services': 'available'
        }
    })

@api_bp.route('/jobs', methods=['GET'])
@login_required
def get_jobs():
    """Get job descriptions with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        company = request.args.get('company', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Build query
        query = JobDescription.query
        
        # Apply filters
        if search:
            is_valid, error = Validators.validate_search_query(search)
            if not is_valid:
                return jsonify({'error': error}), 400
            query = query.filter(
                JobDescription.title.contains(search) |
                JobDescription.company.contains(search) |
                JobDescription.description.contains(search)
            )
        
        if status:
            query = query.filter(JobDescription.status == status)
        
        if company:
            query = query.filter(JobDescription.company.contains(company))
        
        # Order and paginate
        jobs = query.order_by(JobDescription.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs.items],
            'pagination': {
                'page': jobs.page,
                'per_page': jobs.per_page,
                'total': jobs.total,
                'pages': jobs.pages,
                'has_next': jobs.has_next,
                'has_prev': jobs.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/jobs', methods=['POST'])
@login_required
def create_job():
    """Create new job description via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Extract and validate job data
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
            'experience_years': data.get('experience_years'),
            'deadline': data.get('deadline'),
            'priority': data.get('priority', 'medium')
        }
        
        # Validate job data
        is_valid, error = Validators.validate_job_description(job_data)
        if not is_valid:
            return jsonify({'error': error}), 400
        
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
        
        logger.info(f"Job created via API: {job.title} at {job.company}")
        
        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating job via API: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create job'}), 500

@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    """Get specific job description"""
    try:
        job = JobDescription.query.get_or_404(job_id)
        return jsonify({'job': job.to_dict()})
        
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        return jsonify({'error': 'Job not found'}), 404

@api_bp.route('/resumes', methods=['GET'])
@login_required
def get_resumes():
    """Get resumes with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Build query
        query = Resume.query
        
        # Apply filters
        if search:
            is_valid, error = Validators.validate_search_query(search)
            if not is_valid:
                return jsonify({'error': error}), 400
            query = query.filter(
                Resume.candidate_name.contains(search) |
                Resume.email.contains(search) |
                Resume.original_filename.contains(search)
            )
        
        if status:
            query = query.filter(Resume.parsing_status == status)
        
        # Order and paginate
        resumes = query.order_by(Resume.uploaded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'resumes': [resume.to_dict() for resume in resumes.items],
            'pagination': {
                'page': resumes.page,
                'per_page': resumes.per_page,
                'total': resumes.total,
                'pages': resumes.pages,
                'has_next': resumes.has_next,
                'has_prev': resumes.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting resumes: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/resumes', methods=['POST'])
@login_required
def upload_resume():
    """Upload and parse resume via API"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Initialize file handler
        file_handler = FileHandler(current_app.config['UPLOAD_FOLDER'])
        
        # Validate file
        is_valid, error = file_handler.validate_file(file)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Save file
        file_path, error = file_handler.save_file(file)
        if not file_path:
            return jsonify({'error': error}), 500
        
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
        
        # Parse resume
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
            
            logger.info(f"Resume uploaded and parsed via API: {resume.original_filename}")
            
            return jsonify({
                'message': 'Resume uploaded and parsed successfully',
                'resume': resume.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Error parsing resume via API: {str(e)}")
            resume.parsing_status = 'failed'
            resume.parsing_errors = str(e)
            db.session.commit()
            
            return jsonify({'error': f'Resume uploaded but parsing failed: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error uploading resume via API: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upload resume'}), 500

@api_bp.route('/resumes/<int:resume_id>', methods=['GET'])
@login_required
def get_resume(resume_id):
    """Get specific resume"""
    try:
        resume = Resume.query.get_or_404(resume_id)
        return jsonify({'resume': resume.to_dict()})
        
    except Exception as e:
        logger.error(f"Error getting resume {resume_id}: {str(e)}")
        return jsonify({'error': 'Resume not found'}), 404

@api_bp.route('/evaluations', methods=['GET'])
@login_required
def get_evaluations():
    """Get evaluations with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        job_id = request.args.get('job_id', type=int)
        verdict = request.args.get('verdict', '', type=str)
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        
        # Validate pagination parameters
        is_valid, error = Validators.validate_pagination_params(page, per_page)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Build query
        query = Evaluation.query
        
        # Apply filters
        if job_id:
            query = query.filter(Evaluation.job_description_id == job_id)
        
        if verdict:
            query = query.filter(Evaluation.fit_verdict == verdict)
        
        if min_score is not None:
            query = query.filter(Evaluation.relevance_score >= min_score)
        
        if max_score is not None:
            query = query.filter(Evaluation.relevance_score <= max_score)
        
        # Order and paginate
        evaluations = query.order_by(Evaluation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'evaluations': [evaluation.to_dict() for evaluation in evaluations.items],
            'pagination': {
                'page': evaluations.page,
                'per_page': evaluations.per_page,
                'total': evaluations.total,
                'pages': evaluations.pages,
                'has_next': evaluations.has_next,
                'has_prev': evaluations.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting evaluations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/evaluations', methods=['POST'])
@login_required
def create_evaluation():
    """Create new evaluation via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        resume_id = data.get('resume_id')
        job_id = data.get('job_id')
        
        if not resume_id or not job_id:
            return jsonify({'error': 'resume_id and job_id are required'}), 400
        
        # Get resume and job
        resume = Resume.query.get_or_404(resume_id)
        job = JobDescription.query.get_or_404(job_id)
        
        if resume.parsing_status != 'completed':
            return jsonify({'error': 'Resume must be parsed before evaluation'}), 400
        
        # Check if evaluation already exists
        existing_evaluation = Evaluation.query.filter_by(
            resume_id=resume_id,
            job_description_id=job_id
        ).first()
        
        if existing_evaluation:
            return jsonify({'error': 'Evaluation already exists for this resume and job'}), 400
        
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
            
            logger.info(f"Evaluation created via API: Resume {resume_id} vs Job {job_id} - {evaluation.relevance_score}%")
            
            return jsonify({
                'message': 'Evaluation completed successfully',
                'evaluation': evaluation.to_dict(),
                'feedback': feedback.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Error during evaluation via API: {str(e)}")
            evaluation.status = 'failed'
            db.session.commit()
            
            return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error creating evaluation via API: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create evaluation'}), 500

@api_bp.route('/evaluations/<int:evaluation_id>', methods=['GET'])
@login_required
def get_evaluation(evaluation_id):
    """Get specific evaluation with feedback"""
    try:
        evaluation = Evaluation.query.get_or_404(evaluation_id)
        feedback = Feedback.query.filter_by(evaluation_id=evaluation_id).first()
        
        result = {
            'evaluation': evaluation.to_dict(),
            'feedback': feedback.to_dict() if feedback else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting evaluation {evaluation_id}: {str(e)}")
        return jsonify({'error': 'Evaluation not found'}), 404

@api_bp.route('/batch/evaluate', methods=['POST'])
@login_required
def batch_evaluate():
    """Batch evaluate multiple resumes against a job"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        job_id = data.get('job_id')
        resume_ids = data.get('resume_ids', [])
        
        if not job_id or not resume_ids:
            return jsonify({'error': 'job_id and resume_ids are required'}), 400
        
        if not isinstance(resume_ids, list) or len(resume_ids) == 0:
            return jsonify({'error': 'resume_ids must be a non-empty list'}), 400
        
        # Get job
        job = JobDescription.query.get_or_404(job_id)
        
        results = []
        errors = []
        
        for resume_id in resume_ids:
            try:
                # Get resume
                resume = Resume.query.get(resume_id)
                if not resume:
                    errors.append(f"Resume {resume_id} not found")
                    continue
                
                if resume.parsing_status != 'completed':
                    errors.append(f"Resume {resume_id} not parsed")
                    continue
                
                # Check if evaluation already exists
                existing_evaluation = Evaluation.query.filter_by(
                    resume_id=resume_id,
                    job_description_id=job_id
                ).first()
                
                if existing_evaluation:
                    results.append({
                        'resume_id': resume_id,
                        'evaluation_id': existing_evaluation.id,
                        'relevance_score': existing_evaluation.relevance_score,
                        'fit_verdict': existing_evaluation.fit_verdict,
                        'status': 'existing'
                    })
                    continue
                
                # Create evaluation
                evaluation = Evaluation(
                    resume_id=resume_id,
                    job_description_id=job_id,
                    evaluated_by=current_user.id,
                    status='processing'
                )
                
                db.session.add(evaluation)
                db.session.commit()
                
                # Perform evaluation
                resume_data = resume.to_dict()
                job_data = job.to_dict()
                
                scoring_result = relevance_scorer.calculate_relevance_score(resume_data, job_data)
                
                # Update evaluation
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
                
                results.append({
                    'resume_id': resume_id,
                    'evaluation_id': evaluation.id,
                    'relevance_score': evaluation.relevance_score,
                    'fit_verdict': evaluation.fit_verdict,
                    'status': 'completed'
                })
                
            except Exception as e:
                logger.error(f"Error evaluating resume {resume_id}: {str(e)}")
                errors.append(f"Resume {resume_id}: {str(e)}")
                continue
        
        logger.info(f"Batch evaluation completed: {len(results)} successful, {len(errors)} errors")
        
        return jsonify({
            'message': f'Batch evaluation completed: {len(results)} successful, {len(errors)} errors',
            'results': results,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in batch evaluation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Batch evaluation failed'}), 500

@api_bp.route('/analytics/summary')
@login_required
def get_analytics_summary():
    """Get analytics summary for dashboard"""
    try:
        # Calculate statistics
        total_jobs = JobDescription.query.count()
        total_resumes = Resume.query.count()
        total_evaluations = Evaluation.query.count()
        
        # Recent activity (last 7 days)
        recent_evaluations = Evaluation.query.filter(
            Evaluation.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Score distribution
        high_fit = Evaluation.query.filter(Evaluation.fit_verdict == 'high').count()
        medium_fit = Evaluation.query.filter(Evaluation.fit_verdict == 'medium').count()
        low_fit = Evaluation.query.filter(Evaluation.fit_verdict == 'low').count()
        
        # Average scores
        avg_score = db.session.query(db.func.avg(Evaluation.relevance_score)).scalar() or 0
        
        return jsonify({
            'summary': {
                'total_jobs': total_jobs,
                'total_resumes': total_resumes,
                'total_evaluations': total_evaluations,
                'recent_evaluations': recent_evaluations,
                'average_score': round(avg_score, 2)
            },
            'score_distribution': {
                'high': high_fit,
                'medium': medium_fit,
                'low': low_fit
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({'error': 'Failed to get analytics summary'}), 500
