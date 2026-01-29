// Global variables
let selectedFiles = [];

// DOM elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filesSection = document.getElementById('filesSection');
const fileCount = document.getElementById('fileCount');
const filesList = document.getElementById('filesList');
const processButton = document.getElementById('processButton');
const resultsSection = document.getElementById('resultsSection');
const processedImages = document.getElementById('processedImages');

// Fixed configuration - no UI controls needed

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Drop zone events
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    dropZone.addEventListener('click', () => fileInput.click());

    // File input events
    fileInput.addEventListener('change', handleFileSelect);

    // Process button
    processButton.addEventListener('click', processImages);
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length > 0) {
        selectedFiles = imageFiles;
        updateFileList();
    }
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    selectedFiles = files;
    updateFileList();
}

// Update file list display
function updateFileList() {
    if (selectedFiles.length === 0) {
        filesSection.style.display = 'none';
        return;
    }

    filesSection.style.display = 'block';
    fileCount.textContent = selectedFiles.length;

    filesList.innerHTML = '';
    selectedFiles.forEach((file) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
        `;
        filesList.appendChild(fileItem);
    });

    processButton.disabled = false;
}

// Get configuration (fixed settings + options)
function getConfig() {
    const aiBackgroundRemoval = document.getElementById('aiBackgroundRemoval').checked;
    return {
        target_width: 1000,
        target_height: 1000,
        quality: 95,
        background_color: '#F3F3F3',
        product_size_ratio: 0.75,
        auto_upscale: false,
        output_format: 'webp',
        target_max_kb: 100,
        min_quality: 60,
        ai_background_removal: aiBackgroundRemoval
    };
}

// Process images
async function processImages() {
    if (selectedFiles.length === 0) {
        return;
    }

    // Update button state
    processButton.disabled = true;
    const btnText = processButton.querySelector('.btn-text');
    const btnIcon = processButton.querySelector('.btn-icon');

    btnIcon.innerHTML = '<div class="loading-spinner"></div>';
    btnText.textContent = 'Zpracovávám...';

    try {
        const config = getConfig();

        if (selectedFiles.length === 1) {
            // Single image processing
            await processSingleImage(selectedFiles[0], config);
        } else {
            // Batch processing
            await processBatchImages(selectedFiles, config);
        }
    } catch (error) {
        console.error('Error processing images:', error);
        alert('Chyba při zpracování obrázků. Zkuste to prosím znovu.');
    } finally {
        // Reset button state
        btnIcon.innerHTML = '<span class="btn-icon">✨</span>';
        btnText.textContent = 'Zpracovat';
        processButton.disabled = false;
    }
}

// Process single image
async function processSingleImage(file, config) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('config', JSON.stringify(config));

    const response = await fetch('/api/process-single', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    displayProcessedImage(file.name, url);
}

// Process batch images
async function processBatchImages(files, config) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('images', file);
    });
    formData.append('config', JSON.stringify(config));

    const response = await fetch('/api/process-batch', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    // Download ZIP file
    const link = document.createElement('a');
    link.href = url;
    link.download = 'processed_images.zip';
    link.click();

    // Show success message
    showBatchSuccess(files.length);
}

// Display processed image
function displayProcessedImage(originalName, imageUrl) {
    resultsSection.style.display = 'block';

    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    resultItem.innerHTML = `
        <img src="${imageUrl}" alt="Zpracovaný obrázek">
        <button class="download-btn" onclick="downloadImage('${imageUrl}', 'processed_${originalName.replace(/\.[^/.]+$/, '.webp')}')">
            💾 Stáhnout
        </button>
    `;

    processedImages.innerHTML = '';
    processedImages.appendChild(resultItem);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show batch success message
function showBatchSuccess(fileCount) {
    resultsSection.style.display = 'block';

    const messageContainer = document.createElement('div');
    messageContainer.className = 'result-item';
    messageContainer.innerHTML = `
        <div style="padding: 40px;">
            <h3 style="font-size: 24px; margin-bottom: 12px;">🎉 Hotovo!</h3>
            <p style="color: #6b7280; font-size: 16px;">${fileCount} obrázků bylo zpracováno a staženo.</p>
        </div>
    `;

    processedImages.innerHTML = '';
    processedImages.appendChild(messageContainer);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Download image
function downloadImage(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
}