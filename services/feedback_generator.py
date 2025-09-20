"""
Intelligent Feedback Generation Service
Innomatics Research Labs - Enterprise Solution

This module provides comprehensive feedback generation for candidates
with personalized improvement suggestions and actionable recommendations.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
import json

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """
    Advanced feedback generator providing personalized improvement suggestions
    """
    
    def __init__(self):
        """Initialize the feedback generator with AI models"""
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
        )
        
        # Feedback templates for different scenarios
        self.feedback_templates = {
            'high_match': {
                'tone': 'positive',
                'focus': 'strengths_and_optimization'
            },
            'medium_match': {
                'tone': 'constructive',
                'focus': 'improvement_and_development'
            },
            'low_match': {
                'tone': 'encouraging',
                'focus': 'skill_development_and_guidance'
            }
        }
        
        # Resource recommendations database
        self.resource_recommendations = {
            'programming_languages': {
                'python': [
                    'Python for Data Science - Coursera',
                    'Automate the Boring Stuff with Python',
                    'Python.org Official Tutorial'
                ],
                'javascript': [
                    'JavaScript: The Complete Guide - Udemy',
                    'MDN Web Docs - JavaScript Guide',
                    'Eloquent JavaScript Book'
                ],
                'java': [
                    'Java Programming Masterclass - Udemy',
                    'Oracle Java Tutorials',
                    'Effective Java by Joshua Bloch'
                ]
            },
            'frameworks': {
                'react': [
                    'React Official Documentation',
                    'React - The Complete Guide - Udemy',
                    'React Patterns and Best Practices'
                ],
                'django': [
                    'Django Girls Tutorial',
                    'Django Official Documentation',
                    'Two Scoops of Django Book'
                ]
            },
            'cloud_platforms': {
                'aws': [
                    'AWS Certified Solutions Architect - A Cloud Guru',
                    'AWS Free Tier Hands-on Labs',
                    'AWS Well-Architected Framework'
                ],
                'azure': [
                    'Microsoft Learn - Azure Fundamentals',
                    'Azure Architecture Center',
                    'Azure Certification Paths'
                ]
            },
            'soft_skills': {
                'leadership': [
                    'Leadership and Management - Coursera',
                    'The 7 Habits of Highly Effective People',
                    'Harvard Business Review Leadership Articles'
                ],
                'communication': [
                    'Effective Communication - Coursera',
                    'Crucial Conversations Book',
                    'Toastmasters International'
                ]
            }
        }
    
    def generate_feedback(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive feedback for a candidate
        
        Args:
            evaluation_data: Evaluation results and scores
            resume_data: Parsed resume data
            job_data: Job description analysis
            
        Returns:
            Dictionary containing detailed feedback
        """
        try:
            logger.info("Starting feedback generation")
            
            # Determine feedback type based on match score
            relevance_score = evaluation_data.get('relevance_score', 0)
            fit_verdict = evaluation_data.get('fit_verdict', 'low')
            
            # Generate different types of feedback
            overall_feedback = self._generate_overall_feedback(evaluation_data, resume_data, job_data)
            skill_improvements = self._generate_skill_improvements(evaluation_data, resume_data, job_data)
            experience_improvements = self._generate_experience_improvements(evaluation_data, resume_data, job_data)
            education_improvements = self._generate_education_improvements(evaluation_data, resume_data, job_data)
            certification_suggestions = self._generate_certification_suggestions(evaluation_data, resume_data, job_data)
            project_suggestions = self._generate_project_suggestions(evaluation_data, resume_data, job_data)
            
            # Generate actionable recommendations
            immediate_actions = self._generate_immediate_actions(evaluation_data, resume_data, job_data)
            long_term_goals = self._generate_long_term_goals(evaluation_data, resume_data, job_data)
            resource_recommendations = self._generate_resource_recommendations(evaluation_data, resume_data, job_data)
            
            # Determine feedback priority
            priority = self._determine_feedback_priority(relevance_score, fit_verdict)
            
            feedback = {
                'overall_feedback': overall_feedback,
                'skill_improvements': skill_improvements,
                'experience_improvements': experience_improvements,
                'education_improvements': education_improvements,
                'certification_suggestions': certification_suggestions,
                'project_suggestions': project_suggestions,
                'immediate_actions': immediate_actions,
                'long_term_goals': long_term_goals,
                'resource_recommendations': resource_recommendations,
                'feedback_type': 'automatic',
                'priority': priority,
                'generation_metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'generator_version': '1.0.0',
                    'relevance_score': relevance_score,
                    'fit_verdict': fit_verdict
                }
            }
            
            logger.info("Feedback generation completed successfully")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            raise
    
    def _generate_overall_feedback(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate overall feedback message"""
        try:
            relevance_score = evaluation_data.get('relevance_score', 0)
            fit_verdict = evaluation_data.get('fit_verdict', 'low')
            strengths = evaluation_data.get('strengths', [])
            weaknesses = evaluation_data.get('weaknesses', [])
            
            # Use AI to generate personalized feedback
            prompt = f"""
            Generate a professional, encouraging feedback message for a candidate based on their resume evaluation:
            
            Job: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}
            Relevance Score: {relevance_score}%
            Fit Verdict: {fit_verdict.title()}
            
            Strengths: {', '.join(strengths) if strengths else 'None identified'}
            Areas for Improvement: {', '.join(weaknesses) if weaknesses else 'None identified'}
            
            Write a 2-3 paragraph feedback that:
            1. Acknowledges their strengths
            2. Provides constructive guidance on areas for improvement
            3. Encourages continued professional development
            4. Maintains a professional yet encouraging tone
            
            Keep it concise, actionable, and motivating.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional career counselor providing constructive feedback to job candidates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Error generating overall feedback: {str(e)}")
            return self._generate_fallback_feedback(relevance_score, fit_verdict)
    
    def _generate_fallback_feedback(self, relevance_score: float, fit_verdict: str) -> str:
        """Generate fallback feedback when AI is unavailable"""
        if fit_verdict == 'high':
            return f"Congratulations! Your resume shows a strong match ({relevance_score}%) for this position. Your technical skills and experience align well with the job requirements. Continue building on your strengths and consider applying for similar roles."
        elif fit_verdict == 'medium':
            return f"Your resume shows a moderate match ({relevance_score}%) for this position. There are several areas where you can strengthen your candidacy. Focus on developing the missing skills and gaining relevant experience to improve your chances."
        else:
            return f"While your current profile shows a lower match ({relevance_score}%) for this specific role, there are clear paths to improve your candidacy. Focus on developing the key skills and experience mentioned in the job requirements."
    
    def _generate_skill_improvements(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate skill improvement suggestions"""
        missing_skills = evaluation_data.get('missing_skills', [])
        job_skills = job_data.get('skills_required', [])
        
        improvements = []
        
        for skill in missing_skills[:5]:  # Limit to top 5 missing skills
            improvement = {
                'skill': skill,
                'current_level': 'Not mentioned',
                'target_level': 'Proficient',
                'suggestion': f"Focus on developing {skill} skills through hands-on projects and practice",
                'timeline': '3-6 months',
                'resources': self._get_skill_resources(skill)
            }
            improvements.append(improvement)
        
        return improvements
    
    def _generate_experience_improvements(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate experience improvement suggestions"""
        improvements = []
        
        # Check for experience level mismatch
        resume_experience = resume_data.get('experience', [])
        job_experience_years = job_data.get('experience_years', 0)
        
        if job_experience_years > 0 and len(resume_experience) * 2 < job_experience_years:
            improvement = {
                'area': 'Work Experience',
                'current_situation': f"Currently have {len(resume_experience)} positions listed",
                'target_situation': f"Job requires {job_experience_years} years of experience",
                'suggestion': "Consider gaining additional relevant work experience through internships, freelance projects, or volunteer work",
                'timeline': '6-12 months',
                'priority': 'High'
            }
            improvements.append(improvement)
        
        return improvements
    
    def _generate_education_improvements(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate education improvement suggestions"""
        improvements = []
        
        job_education = job_data.get('education_required')
        resume_education = resume_data.get('education', [])
        
        if job_education and not resume_education:
            improvement = {
                'area': 'Education',
                'requirement': job_education,
                'suggestion': f"Consider pursuing {job_education} to meet the job requirements",
                'alternatives': [
                    "Online courses and certifications",
                    "Professional development programs",
                    "Self-study with practical projects"
                ],
                'timeline': '1-2 years',
                'priority': 'Medium'
            }
            improvements.append(improvement)
        
        return improvements
    
    def _generate_certification_suggestions(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate certification suggestions"""
        suggestions = []
        
        job_certs = job_data.get('certifications_required', [])
        resume_certs = resume_data.get('certifications', [])
        
        for cert in job_certs:
            if cert not in resume_certs:
                suggestion = {
                    'certification': cert,
                    'importance': 'Required',
                    'suggestion': f"Obtain {cert} certification to meet job requirements",
                    'study_time': '2-4 months',
                    'cost': 'Varies by certification',
                    'resources': self._get_certification_resources(cert)
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_project_suggestions(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate project suggestions"""
        suggestions = []
        
        job_keywords = job_data.get('keywords', [])
        missing_skills = evaluation_data.get('missing_skills', [])
        
        # Suggest projects based on missing skills
        for skill in missing_skills[:3]:
            suggestion = {
                'project_type': f"{skill} Project",
                'description': f"Build a practical project using {skill} to demonstrate your skills",
                'technologies': [skill],
                'timeline': '1-2 months',
                'difficulty': 'Intermediate',
                'portfolio_value': 'High'
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_immediate_actions(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate immediate action items"""
        actions = []
        
        # Update resume
        actions.append({
            'action': 'Update Resume',
            'description': 'Incorporate missing skills and keywords from job description',
            'timeline': '1 week',
            'priority': 'High'
        })
        
        # Skill development
        missing_skills = evaluation_data.get('missing_skills', [])
        if missing_skills:
            actions.append({
                'action': 'Start Skill Development',
                'description': f'Begin learning {missing_skills[0]} through online courses',
                'timeline': '2 weeks',
                'priority': 'High'
            })
        
        # Network
        actions.append({
            'action': 'Network and Research',
            'description': 'Connect with professionals in the field and research the company',
            'timeline': '1 week',
            'priority': 'Medium'
        })
        
        return actions
    
    def _generate_long_term_goals(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate long-term career goals"""
        goals = []
        
        # Skill mastery
        goals.append({
            'goal': 'Master Key Technologies',
            'description': 'Develop expertise in the technologies most relevant to your target roles',
            'timeline': '6-12 months',
            'milestones': ['Complete 3 projects', 'Obtain 2 certifications', 'Contribute to open source']
        })
        
        # Experience building
        goals.append({
            'goal': 'Build Relevant Experience',
            'description': 'Gain hands-on experience through projects, internships, or freelance work',
            'timeline': '6-18 months',
            'milestones': ['Complete 5 projects', 'Work with 2 companies', 'Build professional network']
        })
        
        # Career advancement
        goals.append({
            'goal': 'Career Advancement',
            'description': 'Position yourself for senior roles and leadership opportunities',
            'timeline': '1-3 years',
            'milestones': ['Lead a team project', 'Mentor junior developers', 'Speak at conferences']
        })
        
        return goals
    
    def _generate_resource_recommendations(self, evaluation_data: Dict[str, Any], resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate resource recommendations"""
        resources = {
            'courses': [],
            'books': [],
            'platforms': [],
            'communities': []
        }
        
        missing_skills = evaluation_data.get('missing_skills', [])
        
        # Add resources for missing skills
        for skill in missing_skills[:3]:
            skill_resources = self._get_skill_resources(skill)
            resources['courses'].extend(skill_resources.get('courses', []))
            resources['books'].extend(skill_resources.get('books', []))
        
        # Add general career development resources
        resources['platforms'].extend([
            'Coursera - Online courses from top universities',
            'Udemy - Practical skill-based courses',
            'LinkedIn Learning - Professional development',
            'edX - Free courses from universities'
        ])
        
        resources['communities'].extend([
            'GitHub - Open source contributions',
            'Stack Overflow - Technical Q&A',
            'Reddit - r/programming, r/cscareerquestions',
            'Discord - Developer communities'
        ])
        
        return resources
    
    def _get_skill_resources(self, skill: str) -> Dict[str, List[str]]:
        """Get resources for a specific skill"""
        skill_lower = skill.lower()
        
        for category, skills in self.resource_recommendations.items():
            for skill_name, resources in skills.items():
                if skill_name in skill_lower or skill_lower in skill_name:
                    return {
                        'courses': resources,
                        'books': [],
                        'platforms': []
                    }
        
        return {'courses': [], 'books': [], 'platforms': []}
    
    def _get_certification_resources(self, cert: str) -> List[str]:
        """Get resources for a specific certification"""
        cert_lower = cert.lower()
        
        if 'aws' in cert_lower:
            return ['AWS Training and Certification', 'A Cloud Guru', 'Linux Academy']
        elif 'azure' in cert_lower:
            return ['Microsoft Learn', 'Pluralsight', 'Cloud Academy']
        elif 'gcp' in cert_lower or 'google' in cert_lower:
            return ['Google Cloud Training', 'Coursera', 'Qwiklabs']
        else:
            return ['Official certification website', 'Study guides', 'Practice exams']
    
    def _determine_feedback_priority(self, relevance_score: float, fit_verdict: str) -> str:
        """Determine feedback priority based on match score"""
        if fit_verdict == 'low' or relevance_score < 40:
            return 'high'
        elif fit_verdict == 'medium' or relevance_score < 70:
            return 'medium'
        else:
            return 'low'
