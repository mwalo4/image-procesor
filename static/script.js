// Global variables
let selectedFiles = [];
let apiConnected = false;

// DOM elements
const apiStatus = document.getElementById('apiStatus');
const statusIndicator = apiStatus.querySelector('.status-indicator');
const statusText = apiStatus.querySelector('.status-text');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const filesSection = document.getElementById('filesSection');
const fileCount = document.getElementById('fileCount');
const filesList = document.getElementById('filesList');
const processButton = document.getElementById('processButton');
const resultsSection = document.getElementById('resultsSection');
const processedImages = document.getElementById('processedImages');

// Fixed configuration - no UI controls needed

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    checkApiHealth();
    setupEventListeners();
});

// API Health Check
async function checkApiHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'ok') {
            apiConnected = true;
            statusIndicator.textContent = '🟢';
            statusText.textContent = 'API připojeno';
            processButton.disabled = false;
        } else {
            throw new Error('API status not ok');
        }
    } catch (error) {
        console.error('API health check failed:', error);
        apiConnected = false;
        statusIndicator.textContent = '🔴';
        statusText.textContent = 'Chyba připojení k API';
        processButton.disabled = true;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Drop zone events
    dropZone.addEventListener('dragover', handleDragOver);
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

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length > 0) {
        selectedFiles = imageFiles;
        updateFileList();
    } else {
        alert('Prosím vyberte pouze obrázkové soubory.');
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
        fileInfo.textContent = 'Podporované formáty: JPG, PNG, BMP, TIFF, WebP';
        return;
    }

    filesSection.style.display = 'block';
    fileCount.textContent = selectedFiles.length;
    fileInfo.textContent = `Vybráno: ${selectedFiles.length} souborů`;

    filesList.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <span class="file-size">(${(file.size / 1024).toFixed(1)} KB)</span>
        `;
        filesList.appendChild(fileItem);
    });

    processButton.disabled = !apiConnected;
}

// Get configuration (fixed settings)
function getConfig() {
    return {
        target_width: 1000,
        target_height: 1000,
        quality: 95,
        background_color: '#F3F3F3',
        product_size_ratio: 0.75,
        auto_upscale: false,
        output_format: 'webp',
        target_max_kb: 100,
        min_quality: 60
    };
}

// Process images
async function processImages() {
    if (selectedFiles.length === 0) {
        alert('Prosím vyberte alespoň jeden obrázek.');
        return;
    }

    if (!apiConnected) {
        alert('API není dostupné. Zkontrolujte připojení.');
        return;
    }

    // Update button state
    processButton.disabled = true;
    processButton.innerHTML = '<span class="loading"></span> Zpracovávám...';

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
        alert('Chyba při zpracování obrázků: ' + error.message);
    } finally {
        // Reset button state
        processButton.disabled = false;
        processButton.textContent = '🚀 Zpracovat obrázky';
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

    displayProcessedImage(file.name, url, blob);
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
function displayProcessedImage(originalName, imageUrl, blob) {
    resultsSection.style.display = 'block';

    const imageContainer = document.createElement('div');
    imageContainer.className = 'processed-image';
    imageContainer.innerHTML = `
        <img src="${imageUrl}" alt="Zpracovaný obrázek">
        <div class="image-actions">
            <button onclick="downloadImage('${imageUrl}', 'processed_${originalName}')">
                💾 Stáhnout
            </button>
        </div>
    `;

    processedImages.appendChild(imageContainer);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show batch success message
function showBatchSuccess(fileCount) {
    resultsSection.style.display = 'block';

    const messageContainer = document.createElement('div');
    messageContainer.className = 'processed-image';
    messageContainer.innerHTML = `
        <div style="padding: 40px; text-align: center;">
            <h3 style="color: #10b981; margin-bottom: 10px;">✅ Úspěšně zpracováno!</h3>
            <p>${fileCount} obrázků bylo zpracováno a staženo jako ZIP soubor.</p>
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

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
} 