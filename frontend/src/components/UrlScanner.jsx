import { useState } from 'react';
import { Card } from './Cards';

export function UrlScanner() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('http://localhost:5000/check-credibility-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });
      if (!response.ok) throw new Error('Server error');
      const data = await response.json();
      setResult(data);
    } catch {
      setError('Failed to connect. Is Flask running on port 5000?');
    } finally {
      setLoading(false);
    }
  };

  const labels = { 0: 'Benign', 1: 'Defacement', 2: 'Phishing', 3: 'Malware' };
  const colors = { 0: '#22c55e', 1: '#f59e0b', 2: '#ef4444', 3: '#dc2626' };
  const verdictColors = { credible: '#22c55e', mixed: '#f59e0b', false: '#ef4444', doubtful: '#f59e0b', unknown: '#9ca3af' };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', padding: '20px' }}>
      <Card style={{ marginBottom: '16px', padding: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, color: '#c084fc' }}>URL Scanner</h2>
      </Card>

      <Card style={{ marginBottom: '16px', padding: '20px' }}>
        <form onSubmit={handleSubmit}>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL..."
            style={{ width: '100%', padding: '12px', marginBottom: '12px', borderRadius: '8px', border: '1px solid #374151', background: '#1f2028', color: '#f3f4f6' }}
          />
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px', borderRadius: '8px', border: 'none', background: '#7c3aed', color: 'white', cursor: 'pointer' }}>
            {loading ? 'Scanning...' : 'Scan'}
          </button>
        </form>
      </Card>

      {error && <Card style={{ marginBottom: '16px', padding: '16px', color: '#ef4444' }}>{error}</Card>}

      {result && (
        <Card style={{ padding: '20px' }}>
          {/* URL Safety Result */}
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: colors[result.url_safety?.prediction_class ?? 2], marginBottom: '8px' }}>
            {labels[result.url_safety?.prediction_class ?? 2]}
            {result.url_safety?.overridden && <span style={{ fontSize: '12px', color: '#f59e0b', marginLeft: '8px' }}>(Overridden)</span>}
          </div>
          {result.url_safety?.override_reason && (
            <div style={{ color: '#f59e0b', fontSize: '12px', marginBottom: '8px' }}>
              {result.url_safety.override_reason}
            </div>
          )}
          <div style={{ color: '#9ca3af', fontSize: '12px', marginBottom: '16px' }}>
            Class {result.url_safety?.prediction_class ?? 'N/A'}
          </div>

          {/* Content Credibility */}
          {result.content_credibility && (
            <div style={{ marginBottom: '16px', padding: '12px', background: '#1f2028', borderRadius: '8px' }}>
              <div style={{ fontSize: '14px', color: '#9ca3af', marginBottom: '4px' }}>Content Credibility</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: verdictColors[result.content_credibility.verdict] || '#9ca3af' }}>
                {result.content_credibility.verdict?.toUpperCase() || 'UNKNOWN'}
              </div>
              <div style={{ fontSize: '12px', color: '#9ca3af' }}>
                Confidence: {result.content_credibility.confidence || 'low'} | Score: {result.content_credibility.score ?? 'N/A'}
              </div>
              {result.content_credibility.summary && (
                <div style={{ fontSize: '12px', color: '#d1d5db', marginTop: '8px', fontStyle: 'italic' }}>
                  "{result.content_credibility.summary.substring(0, 100)}..."
                </div>
              )}
            </div>
          )}

          {/* Overall Risk */}
          {result.overall_risk && (
            <div style={{ marginBottom: '16px', padding: '12px', background: '#1f2028', borderRadius: '8px' }}>
              <div style={{ fontSize: '14px', color: '#9ca3af', marginBottom: '4px' }}>Overall Risk</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: result.overall_risk.level === 'high' ? '#ef4444' : result.overall_risk.level === 'medium' ? '#f59e0b' : '#22c55e' }}>
                {result.overall_risk.level?.toUpperCase()}
              </div>
              {result.overall_risk.factors?.length > 0 && (
                <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
                  {result.overall_risk.factors.join(', ')}
                </div>
              )}
            </div>
          )}

          <div style={{ color: '#f3f4f6', fontSize: '14px', wordBreak: 'break-all' }}>{result.url}</div>
        </Card>
      )}
    </div>
  );
}
