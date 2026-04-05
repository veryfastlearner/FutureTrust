import { useState } from 'react';

export function SimpleScanner() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const normalizeUrl = (value) => {
    const trimmed = value.trim();
    if (!/^https?:\/\//i.test(trimmed)) {
      return `https://${trimmed}`;
    }
    return trimmed;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const cleanUrl = normalizeUrl(url);

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: cleanUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Request failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (label) => {
    const value = String(label || '').toLowerCase();
    if (value.includes('phishing') || value.includes('malware') || value.includes('defacement')) {
      return '#ef4444';
    }
    if (value.includes('benign')) {
      return '#22c55e';
    }
    return '#f59e0b';
  };

  return (
    <div style={{ maxWidth: '700px', margin: '2rem auto', padding: '0 1rem' }}>
      <h2 style={{ color: '#f3f4f6', marginBottom: '1rem' }}>URL Scanner</h2>

      <form
        onSubmit={handleSubmit}
        style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}
      >
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL, e.g. google.com"
          style={{
            flex: 1,
            padding: '0.75rem',
            background: '#1f2028',
            border: '1px solid #2e303a',
            borderRadius: '8px',
            color: '#f3f4f6',
            fontSize: '1rem',
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#aa3bff',
            border: 'none',
            borderRadius: '8px',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </form>

      {error && (
        <div
          style={{
            padding: '1rem',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            color: '#ef4444',
            marginBottom: '1rem',
          }}
        >
          Error: {error}
        </div>
      )}

      {result && (
        <div
          style={{
            padding: '1.5rem',
            background: '#1f2028',
            border: '1px solid #2e303a',
            borderRadius: '12px',
            color: '#f3f4f6',
          }}
        >
          <h3 style={{ margin: '0 0 0.75rem 0', color: '#c084fc' }}>
            Prediction
          </h3>

          <div
            style={{
              display: 'inline-block',
              padding: '0.5rem 0.9rem',
              borderRadius: '999px',
              background: 'rgba(255,255,255,0.06)',
              border: `1px solid ${getRiskColor(result.prediction_label)}`,
              color: getRiskColor(result.prediction_label),
              fontWeight: 700,
              marginBottom: '1rem',
            }}
          >
            {result.prediction_label ?? `Class ${result.prediction_class}`}
          </div>

          <p style={{ marginTop: 0, marginBottom: '0.75rem', color: '#d1d5db' }}>
            <strong>URL:</strong> {result.url}
          </p>

          <p style={{ marginTop: 0, marginBottom: '1rem', color: '#9ca3af' }}>
            <strong>Raw class:</strong> {String(result.prediction_class)}
          </p>

          {result.probabilities && (
            <div style={{ marginBottom: '1rem' }}>
              <h4
                style={{
                  margin: '0 0 0.75rem 0',
                  color: '#9ca3af',
                  fontSize: '0.95rem',
                }}
              >
                Confidence Scores
              </h4>

              {Object.entries(result.probabilities).map(([label, prob]) => (
                <div key={label} style={{ marginBottom: '0.75rem' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.9rem',
                      marginBottom: '0.25rem',
                    }}
                  >
                    <span>{label}</span>
                    <span>{prob}%</span>
                  </div>

                  <div
                    style={{
                      height: '9px',
                      background: '#2e303a',
                      borderRadius: '999px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${prob}%`,
                        height: '100%',
                        background: prob > 50 ? '#ef4444' : prob > 30 ? '#f59e0b' : '#22c55e',
                        borderRadius: '999px',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {result.features && (
            <details style={{ marginBottom: '1rem' }}>
              <summary
                style={{
                  color: '#9ca3af',
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  marginBottom: '0.5rem',
                }}
              >
                Extracted Features
              </summary>
              <pre
                style={{
                  background: '#16171d',
                  padding: '1rem',
                  borderRadius: '8px',
                  overflow: 'auto',
                  fontSize: '0.8rem',
                  marginTop: '0.5rem',
                }}
              >
                {JSON.stringify(result.features, null, 2)}
              </pre>
            </details>
          )}

          <details>
            <summary
              style={{
                color: '#9ca3af',
                fontSize: '0.9rem',
                cursor: 'pointer',
              }}
            >
              Raw Response
            </summary>
            <pre
              style={{
                background: '#16171d',
                padding: '1rem',
                borderRadius: '8px',
                overflow: 'auto',
                fontSize: '0.8rem',
                marginTop: '0.5rem',
              }}
            >
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}