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
      const response = await fetch('http://localhost:5000/predict', {
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
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: colors[result.prediction_class], marginBottom: '8px' }}>
            {labels[result.prediction_class]}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '12px', marginBottom: '16px' }}>Class {result.prediction_class}</div>
          <div style={{ color: '#f3f4f6', fontSize: '14px', wordBreak: 'break-all' }}>{result.url}</div>
          {result.probabilities && (
            <div style={{ marginTop: '16px' }}>
              {Object.entries(result.probabilities).map(([cls, prob]) => (
                <div key={cls} style={{ marginBottom: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#9ca3af' }}>
                    <span>{cls}</span><span>{prob}%</span>
                  </div>
                  <div style={{ height: '4px', background: '#2e303a' }}>
                    <div style={{ width: `${prob}%`, height: '100%', background: colors[result.prediction_class] }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
