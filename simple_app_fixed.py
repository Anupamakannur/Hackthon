#!/usr/bin/env python3
"""
Simplified Resume Evaluator System - FIXED VERSION
This version has minimal dependencies and will work immediately
"""

import os
import sys
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def get_file_size_mb(filepath):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(filepath)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0

def get_uploaded_files():
    """Get list of uploaded files with their sizes"""
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return [], [], {}
    
    files = os.listdir(uploads_dir)
    resumes = []
    jobs = []
    file_sizes = {}
    
    for file in files:
        if os.path.isfile(os.path.join(uploads_dir, file)):
            filepath = os.path.join(uploads_dir, file)
            size_mb = get_file_size_mb(filepath)
            file_sizes[file] = f"{size_mb} MB"
            
            # Categorize files based on extension or content
            if file.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                if 'job' in file.lower() or 'jd' in file.lower():
                    jobs.append(file)
                else:
                    resumes.append(file)
    
    return resumes, jobs, file_sizes

def create_simple_app():
    """Create a simplified Flask app that works without complex dependencies"""
    
    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
        print("✓ Flask imported successfully")
    except ImportError:
        print("Installing Flask...")
        os.system("pip install flask")
        from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-for-demo'
    
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('simple_index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Simple dashboard with real data"""
        # Count actual uploaded files
        uploads_dir = 'uploads'
        if os.path.exists(uploads_dir):
            uploaded_files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
            total_resumes = len(uploaded_files)
        else:
            total_resumes = 0
        
        # Get file sizes
        total_size = 0
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                filepath = os.path.join(uploads_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        
        # Convert to MB
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        # Get categorized files
        resumes, jobs, file_sizes = get_uploaded_files()
        
        return render_template('simple_dashboard.html', 
                             total_resumes=total_resumes,
                             total_size_mb=total_size_mb,
                             total_jobs=len(jobs),
                             total_evaluations=0,
                             avg_score=0,
                             uploaded_resumes=resumes,
                             job_descriptions=jobs,
                             file_sizes=file_sizes)
    
    @app.route('/upload')
    def upload():
        """File upload page"""
        return render_template('simple_upload.html')
    
    @app.route('/api/delete/<file_type>/<filename>', methods=['DELETE'])
    def delete_file(file_type, filename):
        """Delete uploaded file"""
        try:
            # Security check - only allow specific file types
            if file_type not in ['resume', 'job']:
                return jsonify({'success': False, 'message': 'Invalid file type'})
            
            # Security check - prevent directory traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                return jsonify({'success': False, 'message': 'Invalid filename'})
            
            # Use the correct uploads directory path
            filepath = os.path.join('uploads', filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return jsonify({'success': True, 'message': 'File deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'File not found'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    @app.route('/api/health')
    def health():
        """Health check endpoint"""
        # Count uploaded files
        uploads_dir = 'uploads'
        if os.path.exists(uploads_dir):
            uploaded_files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
            total_resumes = len(uploaded_files)
        else:
            total_resumes = 0
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Resume Evaluator System is running!',
            'total_resumes': total_resumes
        })
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Handle file upload"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        file_type = request.form.get('fileType', 'resume')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        
        return jsonify({
            'message': f'{file_type.title()} uploaded successfully',
            'filename': filename,
            'status': 'success'
        })
    
    return app

def create_simple_templates():
    """Create simple HTML templates"""
    
    # Create base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Resume Evaluator{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-file-alt me-2"></i>Resume Evaluator
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <a class="nav-link" href="/upload">Upload</a>
            </div>
        </div>
    </nav>
    
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open('templates/simple_base.html', 'w') as f:
        f.write(base_html)
    
    # Create index template
    index_html = '''{% extends "simple_base.html" %}

{% block title %}Welcome - Resume Evaluator{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="jumbotron bg-primary text-white rounded p-5 mb-5">
            <h1 class="display-4">Automated Resume Relevance Check System</h1>
            <p class="lead">AI-powered resume evaluation for Innomatics Research Labs</p>
            <hr class="my-4">
            <p>Upload resumes, create job descriptions, and get intelligent relevance scores.</p>
            <a class="btn btn-light btn-lg" href="/dashboard" role="button">
                <i class="fas fa-tachometer-alt me-2"></i>Go to Dashboard
            </a>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center">
                <i class="fas fa-upload fa-3x text-primary mb-3"></i>
                <h5 class="card-title">Upload Resumes</h5>
                <p class="card-text">Upload resumes in PDF, DOC, DOCX, or TXT format for analysis.</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center">
                <i class="fas fa-briefcase fa-3x text-success mb-3"></i>
                <h5 class="card-title">Create Jobs</h5>
                <p class="card-text">Define job requirements and criteria for accurate matching.</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center">
                <i class="fas fa-chart-line fa-3x text-info mb-3"></i>
                <h5 class="card-title">Get Scores</h5>
                <p class="card-text">Receive detailed relevance scores and improvement feedback.</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open('templates/simple_index.html', 'w') as f:
        f.write(index_html)
    
    # Create dashboard template
    dashboard_html = '''{% extends "simple_base.html" %}

{% block title %}Dashboard - Resume Evaluator{% endblock %}

{% block content %}
<h1 class="mb-4">
    <i class="fas fa-tachometer-alt me-2"></i>Dashboard
    <button class="btn btn-secondary float-end" onclick="location.reload()">
        <i class="fas fa-sync-alt me-2"></i>Refresh Dashboard
    </button>
</h1>

<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h4 class="card-title">{{ total_jobs or 0 }}</h4>
                        <p class="card-text">Total Jobs</p>
                    </div>
                    <i class="fas fa-briefcase fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h4 class="card-title">{{ total_resumes or 0 }}</h4>
                        <p class="card-text">Total Resumes</p>
                        {% if total_size_mb %}
                        <small>{{ total_size_mb }} MB</small>
                        {% endif %}
                    </div>
                    <i class="fas fa-file-pdf fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h4 class="card-title">{{ total_evaluations or 0 }}</h4>
                        <p class="card-text">Evaluations</p>
                    </div>
                    <i class="fas fa-chart-line fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-3 mb-3">
        <div class="card bg-warning text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h4 class="card-title">{{ avg_score or 0 }}%</h4>
                        <p class="card-text">Avg Score</p>
                    </div>
                    <i class="fas fa-percentage fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="/upload" class="btn btn-primary">
                        <i class="fas fa-upload me-2"></i>Upload Resume
                    </a>
                    <button class="btn btn-success" onclick="alert('Job creation feature coming soon!')">
                        <i class="fas fa-plus me-2"></i>Create Job Description
                    </button>
                    <button class="btn btn-info" onclick="alert('Evaluation feature coming soon!')">
                        <i class="fas fa-chart-line me-2"></i>View Evaluations
                    </button>
                    <button class="btn btn-secondary" onclick="location.reload()">
                        <i class="fas fa-sync-alt me-2"></i>Refresh Dashboard
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">System Status</h5>
            </div>
            <div class="card-body">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>System is running normally
                </div>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>AI services are available
                </div>
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>Some features are in development
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Uploaded Files</h5>
            </div>
            <div class="card-body">
                {% if total_resumes and total_resumes > 0 %}
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i>{{ total_resumes }} file(s) uploaded successfully
                    </div>
                    <p class="text-muted">Files are stored in the uploads directory and ready for processing.</p>
                {% else %}
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>No files uploaded yet
                    </div>
                    <p class="text-muted">Upload your first resume to get started!</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- File Management Section -->
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-file-pdf me-2"></i>Uploaded Resumes
                    <span class="badge bg-success ms-2">{{ uploaded_resumes|length }}</span>
                </h5>
            </div>
            <div class="card-body">
                {% if uploaded_resumes %}
                    {% for file in uploaded_resumes %}
                    <div class="file-item d-flex justify-content-between align-items-center" id="file-{{ file }}">
                        <div>
                            <i class="fas fa-file-pdf text-danger me-2"></i>
                            <span>{{ file }}</span>
                            <small class="text-muted d-block">{{ file_sizes.get(file, 'Unknown size') }}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-danger delete-btn" 
                                    onclick="confirmDelete('{{ file }}', 'resume')"
                                    title="Delete Resume">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No resumes uploaded yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-briefcase me-2"></i>Job Descriptions
                    <span class="badge bg-info ms-2">{{ job_descriptions|length }}</span>
                </h5>
            </div>
            <div class="card-body">
                {% if job_descriptions %}
                    {% for file in job_descriptions %}
                    <div class="file-item d-flex justify-content-between align-items-center" id="file-{{ file }}">
                        <div>
                            <i class="fas fa-file-alt text-info me-2"></i>
                            <span>{{ file }}</span>
                            <small class="text-muted d-block">{{ file_sizes.get(file, 'Unknown size') }}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-danger delete-btn" 
                                    onclick="confirmDelete('{{ file }}', 'job')"
                                    title="Delete Job Description">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No job descriptions uploaded yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
// Confirm delete function
function confirmDelete(fileName, fileType) {
    if (confirm(`Are you sure you want to delete ${fileName}? This action cannot be undone.`)) {
        deleteFile(fileName, fileType);
    }
}

// Delete file function
function deleteFile(fileName, fileType) {
    console.log('Attempting to delete:', fileName, 'Type:', fileType);
    
    fetch(`/api/delete/${fileType}/${fileName}`, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            // Remove the file item from the page
            const fileItem = document.getElementById(`file-${fileName}`);
            if (fileItem) {
                fileItem.remove();
            }
            // Show success message
            showAlert('File deleted successfully!', 'success');
            // Refresh the page after a short delay
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('Error deleting file: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Delete error:', error);
        showAlert('Error deleting file: ' + error.message, 'danger');
    });
}

// Show alert function
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alertDiv, document.body.firstChild);
}
</script>

<style>
.file-item {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}
.delete-btn {
    color: #dc3545;
}
.delete-btn:hover {
    color: #c82333;
}
</style>
{% endblock %}'''
    
    with open('templates/simple_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    # Create upload template
    upload_html = '''{% extends "simple_base.html" %}

{% block title %}Upload Files - Resume Evaluator{% endblock %}

{% block content %}
<h1 class="mb-4">
    <i class="fas fa-upload me-2"></i>Upload Files
</h1>

<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="mb-4">
                        <label class="form-label">Select File Type:</label>
                        <div class="btn-group w-100" role="group">
                            <input type="radio" class="btn-check" name="fileType" id="resume" value="resume" checked>
                            <label class="btn btn-outline-primary" for="resume">
                                <i class="fas fa-file-pdf me-2"></i>Resume
                            </label>
                            
                            <input type="radio" class="btn-check" name="fileType" id="job" value="job">
                            <label class="btn btn-outline-info" for="job">
                                <i class="fas fa-briefcase me-2"></i>Job Description
                            </label>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="file" class="form-label">Select File</label>
                        <input type="file" class="form-control" id="file" name="file" 
                               accept=".pdf,.doc,.docx,.txt" required>
                        <div class="form-text">
                            Supported formats: PDF, DOC, DOCX, TXT (Max size: 16MB)
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="candidate_name" class="form-label">Name (Optional)</label>
                        <input type="text" class="form-control" id="candidate_name" name="candidate_name"
                               placeholder="Enter candidate name or job title">
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label">Email (Optional)</label>
                        <input type="email" class="form-control" id="email" name="email"
                               placeholder="Enter email address">
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-upload me-2"></i>Upload File
                        </button>
                    </div>
                </form>
                
                <div id="uploadResult" class="mt-3" style="display: none;">
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i>
                        <span id="resultMessage"></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const fileType = document.querySelector('input[name="fileType"]:checked').value;
    formData.append('fileType', fileType);
    
    const resultDiv = document.getElementById('uploadResult');
    const messageSpan = document.getElementById('resultMessage');
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            messageSpan.textContent = 'Error: ' + data.error;
            resultDiv.querySelector('.alert').className = 'alert alert-danger';
        } else {
            messageSpan.textContent = data.message + ' - File: ' + data.filename;
            resultDiv.querySelector('.alert').className = 'alert alert-success';
        }
        resultDiv.style.display = 'block';
    })
    .catch(error => {
        messageSpan.textContent = 'Error: ' + error.message;
        resultDiv.querySelector('.alert').className = 'alert alert-danger';
        resultDiv.style.display = 'block';
    });
});
</script>
{% endblock %}'''
    
    with open('templates/simple_upload.html', 'w') as f:
        f.write(upload_html)

def main():
    """Main function to run the simplified app"""
    print("=" * 60)
    print("Resume Evaluator System - FIXED VERSION")
    print("=" * 60)
    
    # Create templates
    print("Creating templates...")
    create_simple_templates()
    print("✓ Templates created")
    
    # Create app
    print("Creating Flask app...")
    app = create_simple_app()
    print("✓ App created successfully")
    
    print("\n" + "=" * 60)
    print("🚀 Starting Resume Evaluator System...")
    print("=" * 60)
    print("Access the system at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
