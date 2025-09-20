// Automated Resume Relevance Check System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File upload drag and drop
    initializeFileUpload();
    
    // Form validation
    initializeFormValidation();
    
    // Auto-refresh for real-time updates
    initializeAutoRefresh();
    
    // Search functionality
    initializeSearch();
    
    // Chart initialization
    initializeCharts();
});

// File Upload with Drag and Drop
function initializeFileUpload() {
    const fileUploadArea = document.querySelector('.file-upload-area');
    const fileInput = document.querySelector('#file-input');
    
    if (fileUploadArea && fileInput) {
        // Drag and drop events
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileUploadArea.classList.add('dragover');
        });
        
        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
        });
        
        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
        
        // Click to upload
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        // File input change
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }
}

function handleFileSelect(file) {
    const fileUploadArea = document.querySelector('.file-upload-area');
    const fileName = document.querySelector('#file-name');
    const fileSize = document.querySelector('#file-size');
    
    if (fileName) {
        fileName.textContent = file.name;
    }
    
    if (fileSize) {
        fileSize.textContent = formatFileSize(file.size);
    }
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                         'text/plain'];
    
    if (!allowedTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload PDF, DOC, DOCX, or TXT files.', 'danger');
        return;
    }
    
    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showAlert('File too large. Maximum size is 16MB.', 'danger');
        return;
    }
    
    fileUploadArea.classList.add('file-selected');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Auto-refresh for real-time updates
function initializeAutoRefresh() {
    const refreshInterval = 30000; // 30 seconds
    
    setInterval(function() {
        // Only refresh if user is on dashboard or evaluations page
        if (window.location.pathname.includes('dashboard') || 
            window.location.pathname.includes('evaluations')) {
            refreshPageData();
        }
    }, refreshInterval);
}

function refreshPageData() {
    // Refresh statistics
    fetch('/api/analytics/summary')
        .then(response => response.json())
        .then(data => {
            updateStatistics(data.summary);
        })
        .catch(error => {
            console.error('Error refreshing data:', error);
        });
}

function updateStatistics(stats) {
    // Update statistics cards
    const elements = {
        'total-jobs': stats.total_jobs,
        'total-resumes': stats.total_resumes,
        'total-evaluations': stats.total_evaluations,
        'recent-evaluations': stats.recent_evaluations
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        let timeout;
        
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                performSearch(input.value, input.dataset.searchType);
            }, 500);
        });
    });
}

function performSearch(query, type) {
    if (query.length < 2) return;
    
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('search', query);
    currentUrl.searchParams.set('page', '1');
    
    window.location.href = currentUrl.toString();
}

// Chart initialization
function initializeCharts() {
    // Performance chart is initialized in the template
    // Additional charts can be added here
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// AJAX form submission
function submitFormAjax(form, successCallback, errorCallback) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (errorCallback) {
                errorCallback(data.error);
            } else {
                showAlert(data.error, 'danger');
            }
        } else {
            if (successCallback) {
                successCallback(data);
            } else {
                showAlert(data.message || 'Operation completed successfully', 'success');
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) {
            errorCallback('An error occurred. Please try again.');
        } else {
            showAlert('An error occurred. Please try again.', 'danger');
        }
    });
}

// Evaluation functions
function startEvaluation(resumeId, jobId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/dashboard/evaluate';
    
    const resumeInput = document.createElement('input');
    resumeInput.type = 'hidden';
    resumeInput.name = 'resume_id';
    resumeInput.value = resumeId;
    
    const jobInput = document.createElement('input');
    jobInput.type = 'hidden';
    jobInput.name = 'job_id';
    jobInput.value = jobId;
    
    form.appendChild(resumeInput);
    form.appendChild(jobInput);
    document.body.appendChild(form);
    
    submitFormAjax(form, function(data) {
        showAlert('Evaluation started successfully', 'success');
        setTimeout(function() {
            window.location.reload();
        }, 2000);
    });
    
    document.body.removeChild(form);
}

function viewEvaluation(evaluationId) {
    window.location.href = `/dashboard/evaluations/${evaluationId}`;
}

// Batch operations
function selectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBatchActions();
}

function updateBatchActions() {
    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    const batchActions = document.querySelector('.batch-actions');
    
    if (checkedBoxes.length > 0) {
        if (batchActions) {
            batchActions.style.display = 'block';
        }
    } else {
        if (batchActions) {
            batchActions.style.display = 'none';
        }
    }
}

function batchEvaluate() {
    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    const jobId = document.querySelector('#batch-job-select').value;
    
    if (!jobId) {
        showAlert('Please select a job for evaluation', 'warning');
        return;
    }
    
    if (checkedBoxes.length === 0) {
        showAlert('Please select at least one resume', 'warning');
        return;
    }
    
    const resumeIds = Array.from(checkedBoxes).map(cb => cb.value);
    
    fetch('/api/batch/evaluate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            job_id: parseInt(jobId),
            resume_ids: resumeIds.map(id => parseInt(id))
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert(data.message, 'success');
            setTimeout(function() {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred during batch evaluation', 'danger');
    });
}

// Export functions
function exportEvaluations(format) {
    const params = new URLSearchParams(window.location.search);
    params.set('format', format);
    
    window.location.href = `/api/evaluations/export?${params.toString()}`;
}

// Print functions
function printEvaluation(evaluationId) {
    const printWindow = window.open(`/dashboard/evaluations/${evaluationId}/print`, '_blank');
    printWindow.focus();
}

// Real-time notifications (WebSocket would be used in production)
function initializeNotifications() {
    // This would connect to a WebSocket for real-time updates
    // For now, we'll use polling
    setInterval(function() {
        checkForNewNotifications();
    }, 60000); // Check every minute
}

function checkForNewNotifications() {
    // This would check for new evaluations, system updates, etc.
    // Implementation depends on backend notification system
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add any additional initialization here
    console.log('Resume Evaluator System initialized');
});
