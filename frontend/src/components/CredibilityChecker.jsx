import { useState } from 'react';
import { Card } from './Cards';

export function CredibilityChecker() {
  const [input, setInput] = useState('');
  const [inputType, setInputType] = useState('claim');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) {
      setError('Please enter some content to check');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/analyze-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content: input.trim()
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Request failed');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to check credibility. Is the server running?');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict) => {
    const colors = {
      credible: '#22c55e',
      mixed: '#f59e0b',
      doubtful: '#ef4444',
      false: '#dc2626',
      insufficient_evidence: '#6b7280'
    };
    return colors[verdict] || '#9ca3af';
  };

  const getVerdictLabel = (verdict) => {
    const labels = {
      credible: 'Credible',
      mixed: 'Mixed Evidence',
      doubtful: 'Doubtful',
      false: 'False',
      insufficient_evidence: 'Insufficient Evidence'
    };
    return labels[verdict] || verdict;
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#22c55e';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto', padding: '20px' }}>
      {/* Header Card */}
      <Card style={{ marginBottom: '16px', padding: '20px', textAlign: 'center' }}>
        <h2 style={{ margin: 0, color: '#7c3aed' }}>Credibility Checker</h2>
        <p style={{ margin: '8px 0 0 0', color: '#6b7280', fontSize: '14px' }}>
          Check if news, claims, or content is trustworthy
        </p>
      </Card>

      {/* Input Card */}
      <Card style={{ marginBottom: '16px', padding: '20px' }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ color: '#374151', fontSize: '12px', display: 'block', marginBottom: '6px' }}>
              Content Type
            </label>
            <select
              value={inputType}
              onChange={(e) => setInputType(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                background: '#ffffff',
                color: '#111827',
                fontSize: '14px'
              }}
            >
              <option value="claim">Claim (e.g., "Vaccines cause autism")</option>
              <option value="headline">Headline (e.g., "Breaking: Major earthquake...")</option>
              <option value="url">URL (e.g., https://example.com/article)</option>
              <option value="article">Article Text</option>
              <option value="post">Social Media Post</option>
            </select>
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Enter ${inputType} to check...`}
            rows={4}
            style={{
              width: '100%',
              padding: '12px',
              marginBottom: '12px',
              borderRadius: '8px',
              border: '1px solid #d1d5db',
              background: '#ffffff',
              color: '#111827',
              fontSize: '14px',
              resize: 'vertical',
              minHeight: '80px'
            }}
          />

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: 'none',
              background: loading ? '#d1d5db' : '#7c3aed',
              color: 'white',
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Analyzing...' : 'Check Credibility'}
          </button>
        </form>
      </Card>

      {/* Error Card */}
      {error && (
        <Card style={{ marginBottom: '16px', padding: '16px', color: '#ef4444', background: '#fef2f2' }}>
          {error}
        </Card>
      )}

      {/* Result Card - Multi Layer */}
      {result && (
        <Card style={{ padding: '20px' }}>
          {/* Final Verdict */}
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                borderRadius: '999px',
                background: result.final_verdict === 'trustworthy' ? 'rgba(34, 197, 94, 0.2)' : 
                           result.final_verdict === 'suspicious' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                border: `2px solid ${result.final_verdict === 'trustworthy' ? '#22c55e' : 
                         result.final_verdict === 'suspicious' ? '#f59e0b' : '#ef4444'}`,
                color: result.final_verdict === 'trustworthy' ? '#22c55e' : 
                       result.final_verdict === 'suspicious' ? '#f59e0b' : '#ef4444',
                fontWeight: 'bold',
                fontSize: '18px',
                textTransform: 'uppercase'
              }}
            >
              {result.final_verdict} • {result.final_confidence} confidence
            </div>
            
            <p style={{ color: '#374151', fontSize: '14px', marginTop: '12px', lineHeight: '1.6' }}>
              {result.final_summary}
            </p>
          </div>

          {/* Layer 1: Content Inspector */}
          {result.layers?.layer_1_inspector && (
            <div style={{ marginBottom: '16px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Layer 1: Content Inspector</div>
              <div style={{ fontSize: '14px', color: '#111827' }}>
                Found {result.layers.layer_1_inspector.urls_count} URLs, {result.layers.layer_1_inspector.accounts_count} accounts
              </div>
              {result.layers.layer_1_inspector.red_flags_count > 0 && (
                <div style={{ fontSize: '12px', color: '#ef4444', marginTop: '4px' }}>
                  {result.layers.layer_1_inspector.red_flags_count} red flags detected
                </div>
              )}
            </div>
          )}

          {/* Layer 2: URL Safety */}
          {result.layers?.layer_2_url_check && (
            <div style={{ marginBottom: '16px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Layer 2: URL Safety Check</div>
              <div style={{ fontSize: '14px', color: '#111827' }}>
                {result.layers.layer_2_url_check.prediction_label || 'Unknown'} 
                ({result.layers.layer_2_url_check.confidence?.toFixed(1) || 0}% confidence)
              </div>
            </div>
          )}

          {/* Layer 4: Final Verdict */}
          {result.layers?.layer_4_final_verdict && (
            <div style={{ marginBottom: '16px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Layer 4: Final Frontier Agent</div>
              <div style={{ fontSize: '14px', color: '#111827' }}>
                Risk Level: <span style={{ 
                  color: result.risk_level === 'critical' ? '#ef4444' : 
                         result.risk_level === 'high' ? '#ef4444' :
                         result.risk_level === 'medium' ? '#f59e0b' : '#22c55e'
                }}>{result.risk_level?.toUpperCase()}</span>
              </div>
            </div>
          )}

          {/* Recommendation */}
          {result.recommendation && (
            <div style={{ padding: '12px', background: 'rgba(124, 58, 237, 0.08)', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#7c3aed', marginBottom: '4px' }}>Recommendation</div>
              <div style={{ fontSize: '14px', color: '#374151' }}>{result.recommendation}</div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
