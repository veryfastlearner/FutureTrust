import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function BotDetection() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/detect-bot', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Request failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze image. Is the server running?');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#22c55e';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getClassIcon = (cls) => {
    const icons = {
      bot: '[BOT]',
      cyborg: '[CYBORG]',
      real: '[REAL]',
      verified: '[VERIFIED]'
    };
    return icons[cls] || '[?]';
  };

  const getClassDescription = (cls) => {
    const descriptions = {
      bot: 'Likely an automated bot account',
      cyborg: 'Mixed automated and human activity',
      real: 'Appears to be a genuine human account',
      verified: 'Verified authentic account'
    };
    return descriptions[cls] || 'Unknown classification';
  };

  return (
    <div style={{ minHeight: '100vh', background: '#faf9f6' }}>
      {/* Header */}
      <header style={{
        padding: '20px 32px',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#ffffff',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div 
          onClick={() => navigate('/')}
          style={{ 
            fontSize: '24px', 
            fontWeight: '700', 
            color: '#111827',
            cursor: 'pointer'
          }}
        >
          FutureTrust
        </div>
        <nav style={{ display: 'flex', gap: '24px' }}>
          <span onClick={() => navigate('/')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Home</span>
          <span onClick={() => navigate('/url-safety')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>URL Safety</span>
          <span onClick={() => navigate('/source-checking')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Source Checker</span>
          <span style={{ color: '#111827', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }}>Bot Detection</span>
        </nav>
      </header>

      {/* Tool Header */}
      <div style={{
        padding: '60px 32px 40px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #ffffff 0%, #faf9f6 100%)'
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 24px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '999px',
          marginBottom: '24px'
        }}>
          <span style={{ color: '#f59e0b', fontSize: '14px', fontWeight: '600' }}>Profile Analysis</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: '700',
          color: '#111827',
          margin: '0 0 16px'
        }}>
          Bot Detection
        </h1>

        <p style={{
          fontSize: '18px',
          color: '#6b7280',
          maxWidth: '640px',
          margin: '0 auto',
          lineHeight: '1.6'
        }}>
          Upload a social media profile picture to classify it as Bot, Cyborg, Real, or Verified using our SigLIP2 AI model.
        </p>
      </div>

      {/* Upload Section */}
      <div style={{ padding: '0 32px 80px' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <form onSubmit={handleSubmit}>
            {/* File Upload Area */}
            <div style={{
              border: '2px dashed #d1d5db',
              borderRadius: '16px',
              padding: '48px 32px',
              textAlign: 'center',
              background: '#ffffff',
              marginBottom: '24px',
              transition: 'all 0.2s',
              cursor: 'pointer'
            }}>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="image-upload"
              />
              <label htmlFor="image-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  background: 'rgba(245, 158, 11, 0.1)',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px'
                }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '32px', height: '32px', color: '#f59e0b' }}>
                    <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <p style={{ color: '#111827', fontSize: '16px', fontWeight: '500', margin: '0 0 8px' }}>
                  {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                </p>
                <p style={{ color: '#6b7280', fontSize: '14px', margin: 0 }}>
                  PNG, JPG, JPEG up to 10MB
                </p>
              </label>
            </div>

            {/* Preview */}
            {preview && (
              <div style={{
                marginBottom: '24px',
                borderRadius: '12px',
                overflow: 'hidden',
                border: '1px solid #e5e7eb'
              }}>
                <img 
                  src={preview} 
                  alt="Preview" 
                  style={{ 
                    width: '100%', 
                    maxHeight: '300px', 
                    objectFit: 'contain',
                    background: '#f9fafb'
                  }} 
                />
              </div>
            )}

            {/* Error */}
            {error && (
              <div style={{
                padding: '12px 16px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                marginBottom: '24px',
                color: '#ef4444',
                fontSize: '14px'
              }}>
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !selectedFile}
              style={{
                width: '100%',
                padding: '16px 32px',
                background: selectedFile && !loading ? '#f59e0b' : '#d1d5db',
                color: '#ffffff',
                border: 'none',
                borderRadius: '999px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: selectedFile && !loading ? 'pointer' : 'not-allowed',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {loading ? (
                <>
                  <span style={{ 
                    width: '20px', 
                    height: '20px', 
                    border: '2px solid #ffffff',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  Analyzing...
                </>
              ) : (
                <>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '20px', height: '20px' }}>
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Analyze Profile
                </>
              )}
            </button>
          </form>

          {/* Results */}
          {result && result.detection && (
            <div style={{
              marginTop: '32px',
              padding: '24px',
              background: '#ffffff',
              borderRadius: '16px',
              border: '1px solid #e5e7eb',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#111827',
                margin: '0 0 24px',
                textAlign: 'center'
              }}>
                Analysis Results
              </h3>

              {/* Top Prediction */}
              <div style={{
                textAlign: 'center',
                padding: '32px',
                background: `linear-gradient(135deg, ${getConfidenceColor(result.detection.top_prediction.confidence)}15 0%, transparent 100%)`,
                borderRadius: '12px',
                marginBottom: '24px'
              }}>
                <div style={{ 
                  fontSize: '48px', 
                  fontWeight: '700',
                  fontFamily: 'monospace',
                  marginBottom: '16px',
                  color: getConfidenceColor(result.detection.top_prediction.confidence)
                }}>
                  {getClassIcon(result.detection.top_prediction.class)}
                </div>
                <div style={{
                  fontSize: '32px',
                  fontWeight: '700',
                  color: getConfidenceColor(result.detection.top_prediction.confidence),
                  textTransform: 'uppercase',
                  marginBottom: '8px'
                }}>
                  {result.detection.top_prediction.class}
                </div>
                <div style={{
                  fontSize: '48px',
                  fontWeight: '700',
                  color: '#111827'
                }}>
                  {Math.round(result.detection.top_prediction.confidence * 100)}%
                </div>
                <p style={{ color: '#6b7280', marginTop: '8px' }}>
                  {getClassDescription(result.detection.top_prediction.class)}
                </p>
              </div>

              {/* All Probabilities */}
              <div style={{ display: 'grid', gap: '12px' }}>
                {Object.entries(result.detection.predictions)
                  .sort(([,a], [,b]) => b - a)
                  .map(([cls, confidence]) => (
                    <div key={cls} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '12px 16px',
                      background: '#f9fafb',
                      borderRadius: '8px'
                    }}>
                      <span style={{ 
                        fontSize: '14px', 
                        fontFamily: 'monospace',
                        fontWeight: '600',
                        color: getConfidenceColor(confidence)
                      }}>{getClassIcon(cls)}</span>
                      <span style={{ 
                        width: '80px',
                        color: '#374151',
                        fontWeight: '500',
                        textTransform: 'capitalize'
                      }}>
                        {cls}
                      </span>
                      <div style={{
                        flex: 1,
                        height: '8px',
                        background: '#e5e7eb',
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${confidence * 100}%`,
                          background: getConfidenceColor(confidence),
                          borderRadius: '4px',
                          transition: 'width 0.5s ease'
                        }} />
                      </div>
                      <span style={{
                        width: '50px',
                        textAlign: 'right',
                        color: '#6b7280',
                        fontSize: '14px',
                        fontWeight: '500'
                      }}>
                        {Math.round(confidence * 100)}%
                      </span>
                    </div>
                  ))
                }
              </div>

              {/* Model Info */}
              <p style={{
                marginTop: '24px',
                paddingTop: '16px',
                borderTop: '1px solid #e5e7eb',
                fontSize: '12px',
                color: '#9ca3af',
                textAlign: 'center'
              }}>
                Model: {result.detection.model}
              </p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default BotDetection;
