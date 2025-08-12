import React, { useState, useRef } from 'react';
import './ImageProcessor.css';

const ImageProcessor = () => {
  const [files, setFiles] = useState([]);
  const [processedImages, setProcessedImages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [config, setConfig] = useState({
    target_width: 1000,
    target_height: 1000,
    quality: 95,
    background_color: '#F3F3F3',
    product_size_ratio: 0.75,
    auto_upscale: false
  });
  const [apiStatus, setApiStatus] = useState('unknown');
  const fileInputRef = useRef(null);

  const API_BASE_URL = 'http://localhost:5000/api';

  // Kontrola API
  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setApiStatus(data.status === 'ok' ? 'connected' : 'error');
      return data.status === 'ok';
    } catch (error) {
      setApiStatus('error');
      return false;
    }
  };

  // Načtení konfigurace z API
  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/config`);
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Chyba při načítání konfigurace:', error);
    }
  };

  // Zpracování jednoho obrázku
  const processSingleImage = async (file) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('config', JSON.stringify(config));

    try {
      const response = await fetch(`${API_BASE_URL}/process-single`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      return {
        originalName: file.name,
        processedUrl: url,
        processedBlob: blob
      };
    } catch (error) {
      console.error('Chyba při zpracování obrázku:', error);
      throw error;
    }
  };

  // Zpracování více obrázků
  const processBatchImages = async () => {
    if (files.length === 0) return;

    setIsProcessing(true);
    const results = [];

    try {
      // Pro více obrázků použijeme batch endpoint
      if (files.length > 1) {
        const formData = new FormData();
        files.forEach(file => {
          formData.append('images', file);
        });
        formData.append('config', JSON.stringify(config));

        const response = await fetch(`${API_BASE_URL}/process-batch`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Stáhnutí ZIP souboru
        const link = document.createElement('a');
        link.href = url;
        link.download = 'processed_images.zip';
        link.click();
        
        setProcessedImages([]);
      } else {
        // Pro jeden obrázek použijeme single endpoint
        const result = await processSingleImage(files[0]);
        setProcessedImages([result]);
      }
    } catch (error) {
      console.error('Chyba při zpracování:', error);
      alert('Chyba při zpracování obrázků: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // Zpracování base64 obrázku (pro drag & drop)
  const processBase64Image = async (base64Data) => {
    try {
      const response = await fetch(`${API_BASE_URL}/process-base64`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Data,
          config: config
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        const blob = await fetch(`data:image/jpeg;base64,${data.processed_image}`).then(r => r.blob());
        const url = URL.createObjectURL(blob);
        
        return {
          originalName: 'uploaded_image.jpg',
          processedUrl: url,
          processedBlob: blob
        };
      }
    } catch (error) {
      console.error('Chyba při zpracování base64 obrázku:', error);
      throw error;
    }
  };

  // Drag & drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    const imageFiles = droppedFiles.filter(file => 
      file.type.startsWith('image/')
    );
    
    if (imageFiles.length > 0) {
      setFiles(imageFiles);
    }
  };

  // Stáhnutí zpracovaného obrázku
  const downloadImage = (processedImage) => {
    const link = document.createElement('a');
    link.href = processedImage.processedUrl;
    link.download = `processed_${processedImage.originalName}`;
    link.click();
  };

  // Inicializace při načtení komponenty
  React.useEffect(() => {
    checkApiHealth();
    loadConfig();
  }, []);

  return (
    <div className="image-processor">
      <div className="header">
        <h1>🖼️ Universal Image Processor</h1>
        <div className={`api-status ${apiStatus}`}>
          API Status: {apiStatus === 'connected' ? '🟢 Připojeno' : 
                      apiStatus === 'error' ? '🔴 Chyba připojení' : '🟡 Kontroluji...'}
        </div>
      </div>

      <div className="config-section">
        <h3>⚙️ Konfigurace</h3>
        <div className="config-grid">
          <div className="config-item">
            <label>Šířka (px):</label>
            <input
              type="number"
              value={config.target_width}
              onChange={(e) => setConfig({...config, target_width: parseInt(e.target.value)})}
            />
          </div>
          <div className="config-item">
            <label>Výška (px):</label>
            <input
              type="number"
              value={config.target_height}
              onChange={(e) => setConfig({...config, target_height: parseInt(e.target.value)})}
            />
          </div>
          <div className="config-item">
            <label>Kvalita (%):</label>
            <input
              type="number"
              min="1"
              max="100"
              value={config.quality}
              onChange={(e) => setConfig({...config, quality: parseInt(e.target.value)})}
            />
          </div>
          <div className="config-item">
            <label>Barva pozadí:</label>
            <input
              type="color"
              value={config.background_color}
              onChange={(e) => setConfig({...config, background_color: e.target.value})}
            />
          </div>
          <div className="config-item">
            <label>Velikost produktu (%):</label>
            <input
              type="number"
              min="0.1"
              max="1"
              step="0.1"
              value={config.product_size_ratio}
              onChange={(e) => setConfig({...config, product_size_ratio: parseFloat(e.target.value)})}
            />
          </div>
          <div className="config-item">
            <label>
              <input
                type="checkbox"
                checked={config.auto_upscale}
                onChange={(e) => setConfig({...config, auto_upscale: e.target.checked})}
              />
              Automatický upscale
            </label>
          </div>
        </div>
      </div>

      <div className="upload-section">
        <div
          className="drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">📁</div>
            <p>Přetáhněte obrázky sem nebo klikněte pro výběr</p>
            <p className="file-info">
              {files.length > 0 ? `Vybráno: ${files.length} souborů` : 'Podporované formáty: JPG, PNG, BMP, TIFF, WebP'}
            </p>
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={(e) => setFiles(Array.from(e.target.files))}
          style={{ display: 'none' }}
        />
      </div>

      {files.length > 0 && (
        <div className="files-section">
          <h3>📋 Vybrané soubory ({files.length})</h3>
          <div className="files-list">
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <span>{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            ))}
          </div>
          
          <button
            className="process-button"
            onClick={processBatchImages}
            disabled={isProcessing || apiStatus !== 'connected'}
          >
            {isProcessing ? '🔄 Zpracovávám...' : '🚀 Zpracovat obrázky'}
          </button>
        </div>
      )}

      {processedImages.length > 0 && (
        <div className="results-section">
          <h3>✅ Zpracované obrázky</h3>
          <div className="processed-images">
            {processedImages.map((image, index) => (
              <div key={index} className="processed-image">
                <img src={image.processedUrl} alt="Zpracovaný obrázek" />
                <div className="image-actions">
                  <button onClick={() => downloadImage(image)}>
                    💾 Stáhnout
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageProcessor; 