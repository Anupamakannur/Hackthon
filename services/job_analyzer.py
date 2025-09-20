"""
Job Description Analysis Service
Innomatics Research Labs - Enterprise Solution

This module provides comprehensive job description analysis capabilities
including keyword extraction, skill requirements analysis, and job categorization.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

logger = logging.getLogger(__name__)

class JobAnalyzer:
    """
    Advanced job description analyzer with AI-powered keyword extraction
    and skill requirement analysis
    """
    
    def __init__(self):
        """Initialize the job analyzer with required models and configurations"""
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )
        
        # Skills database for better matching
        self.skills_database = self._load_skills_database()
        
        # Experience level patterns
        self.experience_patterns = {
            'entry': ['entry', 'junior', 'trainee', 'intern', 'graduate', '0-2', '0-1', '1-2'],
            'mid': ['mid', 'intermediate', '2-4', '3-5', '2-5', '3-4'],
            'senior': ['senior', 'lead', 'principal', '5+', '6+', '7+', '5-8', '6-10'],
            'lead': ['lead', 'principal', 'staff', 'architect', 'manager', 'director', '8+', '10+']
        }
        
        # Job type patterns
        self.job_type_patterns = {
            'full_time': ['full.time', 'permanent', 'regular', 'fulltime'],
            'part_time': ['part.time', 'parttime', 'contractor'],
            'contract': ['contract', 'consultant', 'freelance', 'temporary'],
            'internship': ['intern', 'internship', 'trainee', 'co.op']
        }
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database for better matching"""
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
                'html', 'css', 'sass', 'scss', 'dart', 'perl', 'bash', 'powershell'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
                'laravel', 'rails', 'asp.net', 'node.js', 'fastapi', 'gin', 'echo',
                'tensorflow', 'pytorch', 'keras', 'scikit.learn', 'pandas', 'numpy'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sqlite', 'dynamodb', 'neo4j', 'influxdb', 'couchdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode'
            ],
            'tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'jira',
                'confluence', 'slack', 'trello', 'figma', 'sketch', 'postman', 'swagger'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices',
                'rest', 'graphql', 'api', 'microservices', 'serverless'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem.solving', 'analytical',
                'creative', 'adaptable', 'organized', 'management', 'collaboration',
                'presentation', 'negotiation', 'mentoring', 'coaching'
            ]
        }
    
    def analyze_job_description(self, job_description: str, requirements: str) -> Dict[str, Any]:
        """
        Analyze job description and extract structured requirements
        
        Args:
            job_description: Main job description text
            requirements: Specific requirements text
            
        Returns:
            Dictionary containing analyzed job data
        """
        try:
            logger.info("Starting job description analysis")
            
            # Combine description and requirements
            full_text = f"{job_description}\n\n{requirements}"
            cleaned_text = self._clean_text(full_text)
            
            # Extract structured information
            analysis_result = {
                'raw_text': full_text,
                'cleaned_text': cleaned_text,
                'skills_required': self._extract_required_skills(cleaned_text),
                'skills_preferred': self._extract_preferred_skills(cleaned_text),
                'experience_level': self._extract_experience_level(cleaned_text),
                'experience_years': self._extract_experience_years(cleaned_text),
                'education_required': self._extract_education_requirements(cleaned_text),
                'certifications_required': self._extract_certification_requirements(cleaned_text),
                'job_type': self._extract_job_type(cleaned_text),
                'location': self._extract_location(cleaned_text),
                'salary_range': self._extract_salary_range(cleaned_text),
                'keywords': self._extract_keywords(cleaned_text),
                'key_responsibilities': self._extract_responsibilities(cleaned_text),
                'qualifications': self._extract_qualifications(cleaned_text),
                'analysis_metadata': {
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'text_length': len(cleaned_text),
                    'complexity_score': self._calculate_complexity_score(cleaned_text)
                }
            }
            
            logger.info("Job description analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        
        return text
    
    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required technical and soft skills"""
        required_skills = set()
        text_lower = text.lower()
        
        # Extract technical skills from database
        for category, skill_list in self.skills_database.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    required_skills.add(skill.title())
        
        # Look for explicit "required" keywords
        required_patterns = [
            r'required[:\s]+([^.]{2,50})',
            r'must have[:\s]+([^.]{2,50})',
            r'essential[:\s]+([^.]{2,50})',
            r'mandatory[:\s]+([^.]{2,50})'
        ]
        
        for pattern in required_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Extract skills from the match
                words = word_tokenize(match)
                for word in words:
                    if len(word) > 2 and word not in self.stop_words:
                        required_skills.add(word.title())
        
        return list(required_skills)
    
    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred skills"""
        preferred_skills = set()
        text_lower = text.lower()
        
        # Look for explicit "preferred" keywords
        preferred_patterns = [
            r'preferred[:\s]+([^.]{2,50})',
            r'nice to have[:\s]+([^.]{2,50})',
            r'bonus[:\s]+([^.]{2,50})',
            r'plus[:\s]+([^.]{2,50})'
        ]
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                words = word_tokenize(match)
                for word in words:
                    if len(word) > 2 and word not in self.stop_words:
                        preferred_skills.add(word.title())
        
        return list(preferred_skills)
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level from job description"""
        text_lower = text.lower()
        
        # Check for experience level patterns
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return level
        
        # Default to mid-level if no specific pattern found
        return 'mid'
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract required years of experience"""
        # Look for year patterns
        year_patterns = [
            r'(\d+)[\s-]*(\d+)?\s*years?',
            r'(\d+)[\s-]*(\d+)?\s*yr',
            r'(\d+)\+?\s*years?'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if match[0]:  # First group
                    try:
                        years = int(match[0])
                        if 0 <= years <= 20:  # Reasonable range
                            return years
                    except ValueError:
                        continue
        
        return None
    
    def _extract_education_requirements(self, text: str) -> Optional[str]:
        """Extract education requirements"""
        education_patterns = [
            r'(?:bachelor|master|phd|doctorate|diploma|certificate)\s+(?:of|in)?\s*(?:science|arts|engineering|technology|computer|business|management)',
            r'(?:b\.?s\.?|m\.?s\.?|ph\.?d\.?|m\.?b\.?a\.?|b\.?e\.?|m\.?e\.?)',
            r'(?:computer|software|information|data|artificial intelligence|machine learning)\s+(?:science|engineering|technology)'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None
    
    def _extract_certification_requirements(self, text: str) -> List[str]:
        """Extract required certifications"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'(?:aws|azure|gcp|google cloud|microsoft|oracle|cisco|comptia|pmp|scrum|agile)\s+(?:certified|certification)',
            r'(?:certified|certification|certificate)\s+(?:in|for)?\s*(?:aws|azure|gcp|google cloud|microsoft|oracle|cisco|comptia|pmp|scrum|agile)',
            r'(?:cissp|cisa|cism|itil|prince2|six sigma)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                certifications.append(match.strip())
        
        return list(set(certifications))
    
    def _extract_job_type(self, text: str) -> str:
        """Extract job type from description"""
        text_lower = text.lower()
        
        for job_type, patterns in self.job_type_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return job_type
        
        return 'full_time'  # Default
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location using NER"""
        if not self.nlp:
            return None
        
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "GPE":  # Geopolitical entity
                    return ent.text.strip()
        except Exception as e:
            logger.warning(f"Error extracting location: {str(e)}")
        
        return None
    
    def _extract_salary_range(self, text: str) -> Optional[str]:
        """Extract salary range information"""
        salary_patterns = [
            r'\$[\d,]+[\s-]*\$?[\d,]*',
            r'[\d,]+[\s-]*[\d,]*\s*(?:lpa|lakh|k|thousand|million)',
            r'(?:salary|compensation|pay)[:\s]*\$?[\d,]+[\s-]*\$?[\d,]*'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords using TF-IDF"""
        try:
            # Tokenize and clean text
            sentences = sent_tokenize(text)
            cleaned_sentences = [self._clean_text(sent) for sent in sentences]
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(cleaned_sentences)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top keywords
            mean_scores = tfidf_matrix.mean(axis=0).A1
            keyword_scores = list(zip(feature_names, mean_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top 20 keywords
            return [kw[0] for kw in keyword_scores[:20]]
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {str(e)}")
            return []
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities"""
        responsibilities = []
        
        # Look for responsibility patterns
        resp_patterns = [
            r'(?:responsible|responsibility|duties|tasks)[:\s]*([^.]{10,200})',
            r'(?:develop|design|implement|manage|lead|create|build)[^.]{10,100}',
            r'(?:will|should|must)[^.]{10,100}'
        ]
        
        for pattern in resp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 10:
                    responsibilities.append(match.strip())
        
        return responsibilities[:10]  # Limit to 10 responsibilities
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications and requirements"""
        qualifications = []
        
        # Look for qualification patterns
        qual_patterns = [
            r'(?:qualification|requirement|must have|should have)[:\s]*([^.]{10,200})',
            r'(?:degree|experience|skill|knowledge|ability)[^.]{5,100}',
            r'(?:proven|demonstrated|strong|excellent)[^.]{5,100}'
        ]
        
        for pattern in qual_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 5:
                    qualifications.append(match.strip())
        
        return qualifications[:10]  # Limit to 10 qualifications
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate job complexity score based on requirements"""
        complexity = 0.0
        
        # Check for seniority indicators
        seniority_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
        if any(keyword in text.lower() for keyword in seniority_keywords):
            complexity += 0.3
        
        # Check for technical complexity
        tech_keywords = ['microservices', 'distributed', 'scalable', 'performance', 'optimization']
        if any(keyword in text.lower() for keyword in tech_keywords):
            complexity += 0.2
        
        # Check for management requirements
        mgmt_keywords = ['team', 'mentor', 'lead', 'manage', 'coordinate']
        if any(keyword in text.lower() for keyword in mgmt_keywords):
            complexity += 0.2
        
        # Check for years of experience
        years = self._extract_experience_years(text)
        if years:
            complexity += min(years / 20, 0.3)  # Cap at 0.3 for 20+ years
        
        return min(complexity, 1.0)
    
    def calculate_skill_match_score(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill matching score between resume and job"""
        if not job_skills:
            return 0.0
        
        # Normalize skills to lowercase for comparison
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate matches
        matches = 0
        for job_skill in job_skills_lower:
            if any(job_skill in resume_skill or resume_skill in job_skill 
                   for resume_skill in resume_skills_lower):
                matches += 1
        
        return matches / len(job_skills) if job_skills else 0.0
