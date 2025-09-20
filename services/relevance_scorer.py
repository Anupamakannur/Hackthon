"""
AI-Powered Relevance Scoring Service
Innomatics Research Labs - Enterprise Solution

This module provides sophisticated relevance scoring using multiple AI techniques
including semantic similarity, keyword matching, and machine learning models.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import openai
import json

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """
    Advanced relevance scorer using multiple AI techniques for accurate matching
    """
    
    def __init__(self):
        """Initialize the relevance scorer with AI models and configurations"""
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
        )
        
        # Initialize TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )
        
        # Scoring weights for different components
        self.scoring_weights = {
            'skills_match': 0.35,
            'experience_match': 0.25,
            'education_match': 0.15,
            'certification_match': 0.10,
            'project_match': 0.10,
            'semantic_similarity': 0.05
        }
        
        # Experience level scoring matrix
        self.experience_scoring = {
            'entry': {'entry': 1.0, 'mid': 0.7, 'senior': 0.4, 'lead': 0.2},
            'mid': {'entry': 0.6, 'mid': 1.0, 'senior': 0.8, 'lead': 0.5},
            'senior': {'entry': 0.3, 'mid': 0.7, 'senior': 1.0, 'lead': 0.8},
            'lead': {'entry': 0.2, 'mid': 0.5, 'senior': 0.8, 'lead': 1.0}
        }
    
    def calculate_relevance_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive relevance score between resume and job
        
        Args:
            resume_data: Parsed resume data
            job_data: Analyzed job description data
            
        Returns:
            Dictionary containing detailed scoring breakdown
        """
        try:
            logger.info("Starting relevance score calculation")
            
            # Calculate individual component scores
            skills_score = self._calculate_skills_match_score(resume_data, job_data)
            experience_score = self._calculate_experience_match_score(resume_data, job_data)
            education_score = self._calculate_education_match_score(resume_data, job_data)
            certification_score = self._calculate_certification_match_score(resume_data, job_data)
            project_score = self._calculate_project_match_score(resume_data, job_data)
            semantic_score = self._calculate_semantic_similarity(resume_data, job_data)
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * self.scoring_weights['skills_match'] +
                experience_score * self.scoring_weights['experience_match'] +
                education_score * self.scoring_weights['education_match'] +
                certification_score * self.scoring_weights['certification_match'] +
                project_score * self.scoring_weights['project_match'] +
                semantic_score * self.scoring_weights['semantic_similarity']
            )
            
            # Determine fit verdict
            fit_verdict = self._determine_fit_verdict(overall_score)
            
            # Generate AI analysis
            ai_analysis = self._generate_ai_analysis(resume_data, job_data, {
                'skills_score': skills_score,
                'experience_score': experience_score,
                'education_score': education_score,
                'certification_score': certification_score,
                'project_score': project_score,
                'semantic_score': semantic_score,
                'overall_score': overall_score
            })
            
            # Extract matched and missing elements
            matched_skills, missing_skills = self._extract_skill_matches(resume_data, job_data)
            matched_experience, missing_experience = self._extract_experience_matches(resume_data, job_data)
            
            # Identify strengths and weaknesses
            strengths = self._identify_strengths(resume_data, job_data)
            weaknesses = self._identify_weaknesses(resume_data, job_data)
            
            result = {
                'relevance_score': round(overall_score * 100, 2),  # Convert to 0-100 scale
                'fit_verdict': fit_verdict,
                'skills_match_score': round(skills_score * 100, 2),
                'experience_match_score': round(experience_score * 100, 2),
                'education_match_score': round(education_score * 100, 2),
                'certification_match_score': round(certification_score * 100, 2),
                'project_match_score': round(project_score * 100, 2),
                'semantic_similarity_score': round(semantic_score * 100, 2),
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'matched_experience': matched_experience,
                'missing_experience': missing_experience,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'ai_analysis': ai_analysis,
                'ai_confidence': self._calculate_ai_confidence(resume_data, job_data),
                'scoring_metadata': {
                    'scoring_timestamp': datetime.utcnow().isoformat(),
                    'scoring_version': '1.0.0',
                    'weights_used': self.scoring_weights
                }
            }
            
            logger.info(f"Relevance score calculation completed: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            raise
    
    def _calculate_skills_match_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate skills matching score"""
        resume_skills = resume_data.get('skills', [])
        job_required_skills = job_data.get('skills_required', [])
        job_preferred_skills = job_data.get('skills_preferred', [])
        
        if not job_required_skills and not job_preferred_skills:
            return 0.5  # Neutral score if no skills specified
        
        # Calculate required skills match
        required_match = self._calculate_skill_overlap(resume_skills, job_required_skills)
        
        # Calculate preferred skills match
        preferred_match = self._calculate_skill_overlap(resume_skills, job_preferred_skills)
        
        # Weighted combination (required skills are more important)
        if job_required_skills and job_preferred_skills:
            return (required_match * 0.7) + (preferred_match * 0.3)
        elif job_required_skills:
            return required_match
        else:
            return preferred_match
    
    def _calculate_skill_overlap(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill overlap between resume and job requirements"""
        if not job_skills:
            return 0.0
        
        # Normalize skills for comparison
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
        job_skills_lower = [skill.lower().strip() for skill in job_skills]
        
        matches = 0
        for job_skill in job_skills_lower:
            # Check for exact matches and partial matches
            for resume_skill in resume_skills_lower:
                if (job_skill == resume_skill or 
                    job_skill in resume_skill or 
                    resume_skill in job_skill):
                    matches += 1
                    break
        
        return matches / len(job_skills)
    
    def _calculate_experience_match_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate experience matching score"""
        resume_experience = resume_data.get('experience', [])
        job_experience_level = job_data.get('experience_level', 'mid')
        job_experience_years = job_data.get('experience_years', 0)
        
        # Calculate experience level match
        resume_experience_level = self._determine_resume_experience_level(resume_experience)
        level_score = self.experience_scoring.get(resume_experience_level, {}).get(job_experience_level, 0.5)
        
        # Calculate years of experience match
        resume_years = self._calculate_resume_experience_years(resume_experience)
        years_score = self._calculate_years_match_score(resume_years, job_experience_years)
        
        # Weighted combination
        return (level_score * 0.6) + (years_score * 0.4)
    
    def _determine_resume_experience_level(self, experience: List[Dict[str, Any]]) -> str:
        """Determine experience level from resume experience"""
        if not experience:
            return 'entry'
        
        # Look for seniority indicators in job titles
        seniority_keywords = {
            'lead': ['lead', 'principal', 'staff', 'architect', 'manager', 'director'],
            'senior': ['senior', 'sr', 'lead'],
            'mid': ['mid', 'intermediate', 'experienced'],
            'entry': ['junior', 'jr', 'entry', 'trainee', 'intern']
        }
        
        for level, keywords in seniority_keywords.items():
            for exp in experience:
                title = exp.get('title', '').lower()
                if any(keyword in title for keyword in keywords):
                    return level
        
        # Default based on number of experiences
        if len(experience) >= 5:
            return 'senior'
        elif len(experience) >= 2:
            return 'mid'
        else:
            return 'entry'
    
    def _calculate_resume_experience_years(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience from resume"""
        # This is a simplified calculation
        # In a real implementation, you'd parse dates and calculate actual years
        return min(len(experience) * 2, 20)  # Assume 2 years per experience
    
    def _calculate_years_match_score(self, resume_years: int, job_years: int) -> float:
        """Calculate years of experience match score"""
        if job_years == 0:
            return 1.0  # No specific requirement
        
        if resume_years >= job_years:
            return 1.0  # Meets or exceeds requirement
        else:
            # Gradual penalty for being under requirement
            return max(0.0, resume_years / job_years)
    
    def _calculate_education_match_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate education matching score"""
        resume_education = resume_data.get('education', [])
        job_education = job_data.get('education_required')
        
        if not job_education:
            return 0.5  # Neutral score if no education requirement
        
        # Check if resume education matches job requirement
        for edu in resume_education:
            degree = edu.get('degree', '').lower()
            if job_education.lower() in degree or degree in job_education.lower():
                return 1.0
        
        return 0.0
    
    def _calculate_certification_match_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate certification matching score"""
        resume_certs = resume_data.get('certifications', [])
        job_certs = job_data.get('certifications_required', [])
        
        if not job_certs:
            return 0.5  # Neutral score if no certification requirement
        
        return self._calculate_skill_overlap(resume_certs, job_certs)
    
    def _calculate_project_match_score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate project matching score"""
        resume_projects = resume_data.get('projects', [])
        job_keywords = job_data.get('keywords', [])
        
        if not resume_projects or not job_keywords:
            return 0.5
        
        # Calculate keyword overlap in project descriptions
        project_text = ' '.join([proj.get('description', '') for proj in resume_projects])
        job_text = ' '.join(job_keywords)
        
        return self._calculate_text_similarity(project_text, job_text)
    
    def _calculate_semantic_similarity(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate semantic similarity using TF-IDF"""
        resume_text = resume_data.get('cleaned_text', '')
        job_text = job_data.get('cleaned_text', '')
        
        if not resume_text or not job_text:
            return 0.0
        
        return self._calculate_text_similarity(resume_text, job_text)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.warning(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    def _determine_fit_verdict(self, score: float) -> str:
        """Determine fit verdict based on score"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _extract_skill_matches(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract matched and missing skills"""
        resume_skills = resume_data.get('skills', [])
        job_skills = job_data.get('skills_required', [])
        
        matched = []
        missing = []
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            if any(job_skill_lower in resume_skill or resume_skill in job_skill_lower 
                   for resume_skill in resume_skills_lower):
                matched.append(job_skill)
            else:
                missing.append(job_skill)
        
        return matched, missing
    
    def _extract_experience_matches(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract matched and missing experience elements"""
        # This is a simplified implementation
        # In a real system, you'd do more sophisticated matching
        return [], []
    
    def _identify_strengths(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[str]:
        """Identify candidate strengths for the job"""
        strengths = []
        
        # Check for strong skill matches
        matched_skills, _ = self._extract_skill_matches(resume_data, job_data)
        if len(matched_skills) > 5:
            strengths.append(f"Strong technical skills match ({len(matched_skills)} skills)")
        
        # Check for relevant experience
        experience = resume_data.get('experience', [])
        if len(experience) > 3:
            strengths.append(f"Extensive work experience ({len(experience)} positions)")
        
        # Check for certifications
        certifications = resume_data.get('certifications', [])
        if certifications:
            strengths.append(f"Relevant certifications ({len(certifications)} certs)")
        
        return strengths
    
    def _identify_weaknesses(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[str]:
        """Identify candidate weaknesses for the job"""
        weaknesses = []
        
        # Check for missing skills
        _, missing_skills = self._extract_skill_matches(resume_data, job_data)
        if missing_skills:
            weaknesses.append(f"Missing key skills: {', '.join(missing_skills[:3])}")
        
        # Check for experience level mismatch
        resume_experience = resume_data.get('experience', [])
        job_experience_years = job_data.get('experience_years', 0)
        if job_experience_years > 0 and len(resume_experience) * 2 < job_experience_years:
            weaknesses.append(f"May lack required experience ({job_experience_years} years)")
        
        return weaknesses
    
    def _generate_ai_analysis(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], scores: Dict[str, float]) -> str:
        """Generate AI-powered analysis using OpenAI"""
        try:
            # Prepare context for AI analysis
            context = {
                'job_title': job_data.get('title', 'Unknown'),
                'company': job_data.get('company', 'Unknown'),
                'candidate_name': resume_data.get('candidate_name', 'Candidate'),
                'scores': scores,
                'matched_skills': scores.get('matched_skills', []),
                'missing_skills': scores.get('missing_skills', [])
            }
            
            prompt = f"""
            Analyze the following resume-job match and provide a professional assessment:
            
            Job: {context['job_title']} at {context['company']}
            Candidate: {context['candidate_name']}
            
            Match Scores:
            - Overall Relevance: {scores['overall_score']:.1f}%
            - Skills Match: {scores['skills_score']:.1f}%
            - Experience Match: {scores['experience_score']:.1f}%
            - Education Match: {scores['education_score']:.1f}%
            
            Provide a concise, professional analysis (2-3 sentences) highlighting:
            1. Key strengths for this role
            2. Main areas for improvement
            3. Overall recommendation
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional HR analyst providing resume evaluation insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Error generating AI analysis: {str(e)}")
            return "AI analysis unavailable at this time."
    
    def _calculate_ai_confidence(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """Calculate confidence in the AI analysis"""
        # Simple confidence calculation based on data completeness
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data quality
        if resume_data.get('skills'):
            confidence += 0.1
        if resume_data.get('experience'):
            confidence += 0.1
        if resume_data.get('education'):
            confidence += 0.1
        if job_data.get('skills_required'):
            confidence += 0.1
        if job_data.get('description'):
            confidence += 0.1
        
        return min(confidence, 1.0)
