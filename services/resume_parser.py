"""
Advanced Resume Parser Service
Innomatics Research Labs - Enterprise Solution

This module provides comprehensive resume parsing capabilities supporting
multiple formats (PDF, DOC, DOCX, TXT) with AI-powered text extraction
and structured data parsing.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import PyPDF2
import docx
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import spacy
from textstat import flesch_reading_ease

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class ResumeParser:
    """
    Advanced resume parser with support for multiple formats and AI-powered extraction
    """
    
    def __init__(self):
        """Initialize the resume parser with required models and configurations"""
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common patterns for extraction
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        # Skills database
        self.technical_skills = self._load_skills_database()
        
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
                'laravel', 'rails', 'asp.net', 'node.js', 'fastapi', 'gin', 'echo'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sqlite', 'dynamodb', 'neo4j', 'influxdb', 'couchdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr'
            ],
            'tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'jira',
                'confluence', 'slack', 'trello', 'figma', 'sketch', 'postman'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices'
            ]
        }
    
    def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information
        
        Args:
            file_path: Path to the resume file
            file_type: Type of file (pdf, doc, docx, txt)
            
        Returns:
            Dictionary containing parsed resume data
        """
        try:
            logger.info(f"Starting resume parsing for file: {file_path}")
            
            # Extract raw text
            raw_text = self._extract_text(file_path, file_type)
            if not raw_text:
                raise ValueError("No text could be extracted from the file")
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(raw_text)
            
            # Extract structured information
            parsed_data = {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'candidate_name': self._extract_name(cleaned_text),
                'email': self._extract_email(cleaned_text),
                'phone': self._extract_phone(cleaned_text),
                'location': self._extract_location(cleaned_text),
                'summary': self._extract_summary(cleaned_text),
                'skills': self._extract_skills(cleaned_text),
                'experience': self._extract_experience(cleaned_text),
                'education': self._extract_education(cleaned_text),
                'certifications': self._extract_certifications(cleaned_text),
                'projects': self._extract_projects(cleaned_text),
                'languages': self._extract_languages(cleaned_text),
                'parsing_metadata': {
                    'confidence_score': self._calculate_confidence(cleaned_text),
                    'text_quality_score': self._calculate_text_quality(cleaned_text),
                    'parsing_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"Resume parsing completed successfully for file: {file_path}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {str(e)}")
            raise
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract raw text from different file formats"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() in ['doc', 'docx']:
                return self._extract_from_docx(file_path)
            elif file_type.lower() == 'txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        
        return text
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name using NER"""
        if not self.nlp:
            return None
        
        try:
            doc = self.nlp(text[:1000])  # Process first 1000 characters
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.strip()
        except Exception as e:
            logger.warning(f"Error extracting name: {str(e)}")
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        match = self.email_pattern.search(text)
        return match.group() if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        match = self.phone_pattern.search(text)
        return match.group() if match else None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location using NER"""
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
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary/objective"""
        # Look for common summary keywords
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'overview']
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in summary_keywords):
                return sentence.strip()
        
        # If no explicit summary found, return first few sentences
        if len(sentences) > 0:
            return sentences[0][:500]  # Limit to 500 characters
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical and soft skills"""
        skills = set()
        text_lower = text.lower()
        
        # Extract technical skills from database
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.add(skill.title())
        
        # Extract soft skills using patterns
        soft_skills_patterns = [
            r'leadership', r'communication', r'teamwork', r'problem.solving',
            r'analytical', r'creative', r'adaptable', r'organized',
            r'management', r'collaboration', r'presentation', r'negotiation'
        ]
        
        for pattern in soft_skills_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                skills.add(match.title())
        
        return list(skills)
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience information"""
        experiences = []
        
        # Common job title patterns
        job_patterns = [
            r'(?:software|web|mobile|data|devops|cloud|ai|ml|full.?stack|front.?end|back.?end)\s+(?:engineer|developer|architect|analyst|scientist|specialist)',
            r'(?:senior|lead|principal|staff)\s+(?:software|web|mobile|data|devops|cloud|ai|ml|full.?stack|front.?end|back.?end)\s+(?:engineer|developer|architect|analyst|scientist|specialist)',
            r'(?:manager|director|head|vp|cto|cfo|ceo)',
            r'(?:intern|trainee|junior|associate)'
        ]
        
        # Extract experience using patterns
        for pattern in job_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Try to extract surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                experiences.append({
                    'title': match.group().strip(),
                    'context': context.strip(),
                    'position': match.start()
                })
        
        return experiences[:10]  # Limit to 10 experiences
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'(?:bachelor|master|phd|doctorate|diploma|certificate)\s+(?:of|in)?\s*(?:science|arts|engineering|technology|computer|business|management)',
            r'(?:b\.?s\.?|m\.?s\.?|ph\.?d\.?|m\.?b\.?a\.?|b\.?e\.?|m\.?e\.?)',
            r'(?:computer|software|information|data|artificial intelligence|machine learning)\s+(?:science|engineering|technology)'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.group().strip(),
                    'context': text[max(0, match.start()-50):min(len(text), match.end()+50)].strip()
                })
        
        return education[:5]  # Limit to 5 education entries
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications and licenses"""
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
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project information"""
        projects = []
        
        # Look for project-related keywords
        project_keywords = ['project', 'developed', 'built', 'created', 'implemented', 'designed']
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in project_keywords):
                projects.append({
                    'description': sentence.strip(),
                    'keywords': [kw for kw in project_keywords if kw in sentence_lower]
                })
        
        return projects[:10]  # Limit to 10 projects
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract programming languages and human languages"""
        languages = []
        
        # Programming languages
        prog_langs = ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift']
        text_lower = text.lower()
        
        for lang in prog_langs:
            if lang in text_lower:
                languages.append(lang.title())
        
        # Human languages
        human_langs = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'hindi', 'tamil', 'telugu']
        for lang in human_langs:
            if lang in text_lower:
                languages.append(lang.title())
        
        return list(set(languages))
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate parsing confidence score"""
        confidence = 0.0
        
        # Check for essential information
        if self._extract_email(text):
            confidence += 0.2
        if self._extract_phone(text):
            confidence += 0.2
        if self._extract_skills(text):
            confidence += 0.2
        if self._extract_experience(text):
            confidence += 0.2
        if self._extract_education(text):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calculate text quality score using readability metrics"""
        try:
            # Use Flesch Reading Ease score
            readability_score = flesch_reading_ease(text)
            
            # Normalize to 0-1 scale (higher is better)
            quality_score = min(max(readability_score / 100, 0), 1)
            
            return quality_score
        except Exception as e:
            logger.warning(f"Error calculating text quality: {str(e)}")
            return 0.5  # Default medium quality
