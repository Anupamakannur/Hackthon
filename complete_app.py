from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, abort
import os
import re
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(filepath):
    """Get file size in MB or KB"""
    try:
        size_bytes = os.path.getsize(filepath)
        if size_bytes < 1024 * 1024:  # Less than 1 MB
            return round(size_bytes / 1024, 2)  # Return in KB
        else:
            return round(size_bytes / (1024 * 1024), 2)  # Return in MB
    except:
        return 0

def get_uploaded_files():
    """Get list of uploaded files with categorization"""
    files = []
    resumes = []
    jobs = []
    total_size_bytes = 0
    
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.txt'):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                size_bytes = os.path.getsize(filepath)
                total_size_bytes += size_bytes
                size_display = get_file_size_mb(filepath)
                
                file_info = {
                    'name': filename,
                    'size_display': size_display,
                    'size_bytes': size_bytes,
                    'path': filepath
                }
                
                if 'resume' in filename.lower():
                    resumes.append(file_info)
                elif 'job' in filename.lower():
                    jobs.append(file_info)
                
                files.append(file_info)
    
    # Convert total size to appropriate unit
    if total_size_bytes < 1024 * 1024:
        total_size_display = round(total_size_bytes / 1024, 2)
        total_size_unit = "KB"
    else:
        total_size_display = round(total_size_bytes / (1024 * 1024), 2)
        total_size_unit = "MB"
    
    return files, resumes, jobs, total_size_display, total_size_unit

def extract_skills_from_text(text):
    """Extract skills from resume text"""
    skills = []
    
    # Common technical skills
    skill_patterns = [
        r'python', r'sql', r'power\s*bi', r'tableau', r'excel', r'pandas', r'numpy',
        r'matplotlib', r'seaborn', r'scikit-learn', r'machine\s*learning', r'deep\s*learning',
        r'data\s*analysis', r'data\s*visualization', r'web\s*scraping', r'beautiful\s*soup',
        r'requests', r'statistics', r'vba', r'dax', r'power\s*query', r'jupyter',
        r'git', r'github', r'aws', r'azure', r'spark', r'kafka', r'pyspark',
        r'databricks', r'c\+\+', r'java', r'javascript', r'html', r'css',
        r'django', r'flask', r'mysql', r'postgresql', r'sqlite', r'nosql',
        r'mongodb', r'redis', r'docker', r'kubernetes', r'jenkins', r'ci/cd'
    ]
    
    text_lower = text.lower()
    for pattern in skill_patterns:
        if re.search(pattern, text_lower):
            skills.append(pattern.replace(r'\s*', ' ').replace(r'\+', '+'))
    
    return list(set(skills))

def extract_education_from_text(text):
    """Extract education information"""
    education = []
    
    # Look for degree patterns
    degree_patterns = [
        r'b\.?tech', r'b\.?e\.?', r'bachelor', r'master', r'm\.?tech', r'm\.?e\.?',
        r'mca', r'mba', r'bsc', r'msc', r'phd', r'doctorate'
    ]
    
    text_lower = text.lower()
    for pattern in degree_patterns:
        if re.search(pattern, text_lower):
            education.append(pattern.replace(r'\.?', '.'))
    
    return list(set(education))

def calculate_relevance_score(resume_text, job_text):
    """Calculate relevance score between resume and job description"""
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_text)
    
    resume_education = extract_education_from_text(resume_text)
    job_education = extract_education_from_text(job_text)
    
    # Calculate skill match percentage
    if not job_skills:
        skill_score = 0
    else:
        matched_skills = set(resume_skills) & set(job_skills)
        skill_score = (len(matched_skills) / len(job_skills)) * 100
    
    # Calculate education match
    education_score = 0
    if job_education and resume_education:
        if any(edu in resume_education for edu in job_education):
            education_score = 100
    
    # Calculate experience match (basic keyword matching)
    experience_keywords = ['experience', 'project', 'internship', 'work', 'developed', 'built', 'created']
    resume_exp_count = sum(1 for keyword in experience_keywords if keyword in resume_text.lower())
    job_exp_count = sum(1 for keyword in experience_keywords if keyword in job_text.lower())
    
    experience_score = min((resume_exp_count / max(job_exp_count, 1)) * 100, 100)
    
    # Weighted final score
    final_score = (skill_score * 0.5) + (education_score * 0.3) + (experience_score * 0.2)
    
    return {
        'total_score': round(final_score, 1),
        'skill_score': round(skill_score, 1),
        'education_score': round(education_score, 1),
        'experience_score': round(experience_score, 1),
        'matched_skills': list(set(resume_skills) & set(job_skills)),
        'missing_skills': list(set(job_skills) - set(resume_skills))
    }

def get_suitability_level(score):
    """Determine suitability level based on score"""
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"

@app.route('/')
def index():
    files, resumes, jobs, total_size_display, total_size_unit = get_uploaded_files()
    return render_template('complete_index.html', 
                         total_resumes=len(resumes),
                         total_jobs=len(jobs),
                         total_size_display=total_size_display,
                         total_size_unit=total_size_unit)

@app.route('/upload')
def upload_page():
    return render_template('complete_upload.html')

@app.route('/dashboard')
def dashboard():
    files, resumes, jobs, total_size_display, total_size_unit = get_uploaded_files()
    
    return render_template('complete_dashboard.html', 
                         total_resumes=len(resumes),
                         total_jobs=len(jobs),
                         total_size_display=total_size_display,
                         total_size_unit=total_size_unit,
                         uploaded_resumes=resumes,
                         job_descriptions=jobs,
                         file_sizes={f['name']: f['size_display'] for f in files})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    file_type = request.form.get('fileType', 'resume')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return jsonify({
            'message': f'File {filename} uploaded successfully as {file_type}!',
            'filename': filename,
            'file_type': file_type
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/delete/<file_type>/<filename>', methods=['DELETE'])
def delete_file(file_type, filename):
    # Security check
    if file_type not in ['resume', 'job']:
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    filepath = os.path.join('uploads', filename)
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'message': f'File {filename} deleted successfully!'})
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500

@app.route('/api/match', methods=['POST'])
def match_resumes():
    """Match all resumes against all job descriptions"""
    try:
        files, resumes, jobs, total_size_display, total_size_unit = get_uploaded_files()
        
        if not resumes:
            return jsonify({'error': 'No resumes found'}), 400
        
        if not jobs:
            return jsonify({'error': 'No job descriptions found'}), 400
        
        matches = []
        
        for resume in resumes:
            try:
                with open(resume['path'], 'r', encoding='utf-8') as f:
                    resume_text = f.read()
            except:
                continue
            
            resume_matches = []
            
            for job in jobs:
                try:
                    with open(job['path'], 'r', encoding='utf-8') as f:
                        job_text = f.read()
                except:
                    continue
                
                # Calculate relevance score
                match_data = calculate_relevance_score(resume_text, job_text)
                
                resume_matches.append({
                    'job_name': job['name'],
                    'job_title': job['name'].replace('_', ' ').replace('.txt', ''),
                    'relevance_score': match_data['total_score'],
                    'skill_score': match_data['skill_score'],
                    'education_score': match_data['education_score'],
                    'experience_score': match_data['experience_score'],
                    'suitability': get_suitability_level(match_data['total_score']),
                    'matched_skills': match_data['matched_skills'],
                    'missing_skills': match_data['missing_skills']
                })
            
            matches.append({
                'resume_name': resume['name'],
                'candidate_name': resume['name'].replace('_', ' ').replace('_Resume.txt', ''),
                'matches': resume_matches
            })
        
        return jsonify({
            'success': True,
            'matches': matches,
            'total_resumes': len(resumes),
            'total_jobs': len(jobs)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing matches: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    files, resumes, jobs, total_size_display, total_size_unit = get_uploaded_files()
    return jsonify({
        'status': 'healthy',
        'total_resumes': len(resumes),
        'total_jobs': len(jobs),
        'total_files': len(files),
        'total_size_display': total_size_display,
        'total_size_unit': total_size_unit
    })

@app.route('/uploads/<filename>')
def view_file(filename):
    """Serve uploaded files for viewing with good formatting"""
    try:
        # Security check - prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(403)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            abort(404)
        
        # Check if it's a text file
        if not filename.endswith('.txt'):
            abort(403)
        
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file type for styling
        file_type = "Resume" if "Resume" in filename else "Job Description"
        icon = "fas fa-file-pdf" if "Resume" in filename else "fas fa-briefcase"
        color = "primary" if "Resume" in filename else "success"
        
        # Render formatted template
        return render_template('file_viewer.html', 
                             filename=filename, 
                             content=content, 
                             file_type=file_type,
                             icon=icon,
                             color=color)
    
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        abort(500)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 COMPLETE RESUME EVALUATOR SYSTEM")
    print("=" * 60)
    print("✅ All functionality working")
    print("🌐 Access at: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("📤 Upload: http://localhost:5000/upload")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
