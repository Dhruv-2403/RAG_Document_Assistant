// API Base URL
const API_BASE = '';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const queryForm = document.getElementById('queryForm');
const questionInput = document.getElementById('questionInput');
const askBtn = document.getElementById('askBtn');
const queryStatus = document.getElementById('queryStatus');
const answerSection = document.getElementById('answerSection');
const answerText = document.getElementById('answerText');
const sourcesContainer = document.getElementById('sourcesContainer');
const docListItems = document.getElementById('docListItems');
const clearBtn = document.getElementById('clearBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Query form submit
    queryForm.addEventListener('submit', handleQuery);

    // Clear button
    clearBtn.addEventListener('click', handleClearDocuments);
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

// Handle file upload
async function handleFileUpload(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(file.type)) {
        showStatus(uploadStatus, 'Only PDF and TXT files are supported', 'error');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showStatus(uploadStatus, 'File size exceeds 10MB limit', 'error');
        return;
    }

    // Show loading
    showStatus(uploadStatus, 'Uploading and processing document...', 'loading');

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(
                uploadStatus,
                `${data.filename} uploaded successfully! (${data.chunks} chunks created)`,
                'success'
            );
            loadDocuments();
            fileInput.value = ''; // Reset input
        } else {
            showStatus(uploadStatus, `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, `Upload failed: ${error.message}`, 'error');
    }
}

// Handle query submission
async function handleQuery(e) {
    e.preventDefault();

    const question = questionInput.value.trim();
    if (!question) return;

    // Show loading
    showStatus(queryStatus, 'Searching documents and generating answer...', 'loading');
    askBtn.disabled = true;
    askBtn.innerHTML = '<span class="spinner"></span> Processing...';
    answerSection.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (response.ok) {
            displayAnswer(data);
            queryStatus.style.display = 'none';
        } else {
            showStatus(queryStatus, `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(queryStatus, `Query failed: ${error.message}`, 'error');
    } finally {
        askBtn.disabled = false;
        askBtn.textContent = 'Ask Question';
    }
}

// Display answer and sources
function displayAnswer(data) {
    answerSection.style.display = 'block';

    // Display answer
    answerText.textContent = data.answer;

    // Display sources
    sourcesContainer.innerHTML = '';
    if (data.sources && data.sources.length > 0) {
        data.sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';

            const sourceContent = document.createElement('div');
            sourceContent.className = 'source-content';
            sourceContent.textContent = source.content;

            const sourceMetadata = document.createElement('div');
            sourceMetadata.className = 'source-metadata';
            sourceMetadata.textContent = `Source: ${source.metadata.source} (Chunk ${source.metadata.chunk_id})`;

            sourceItem.appendChild(sourceContent);
            sourceItem.appendChild(sourceMetadata);
            sourcesContainer.appendChild(sourceItem);
        });
    } else {
        sourcesContainer.innerHTML = '<p>No sources found</p>';
    }

    // Scroll to answer
    answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Load documents list
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/api/documents`);
        const data = await response.json();

        docListItems.innerHTML = '';

        if (data.documents && data.documents.length > 0) {
            data.documents.forEach(doc => {
                const li = document.createElement('li');
                li.textContent = doc;
                docListItems.appendChild(li);
            });
        } else {
            docListItems.innerHTML = '<li style="opacity: 0.6;">No documents uploaded yet</li>';
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

// Handle clear documents
async function handleClearDocuments() {
    if (!confirm('Are you sure you want to clear all documents? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/clear`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(uploadStatus, 'All documents cleared', 'success');
            loadDocuments();
            answerSection.style.display = 'none';
        } else {
            showStatus(uploadStatus, `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, `Clear failed: ${error.message}`, 'error');
    }
}

// Show status message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
    element.style.display = 'block';

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}
