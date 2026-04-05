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
      const response = await fetch('http://localhost:5000/check-credibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          input: input.trim(),
          type: inputType,
          max_results: 6
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
        <h2 style={{ margin: 0, color: '#c084fc' }}>🔍 Credibility Checker</h2>
        <p style={{ margin: '8px 0 0 0', color: '#9ca3af', fontSize: '14px' }}>
          Check if news, claims, or content is trustworthy
        </p>
      </Card>

      {/* Input Card */}
      <Card style={{ marginBottom: '16px', padding: '20px' }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ color: '#9ca3af', fontSize: '12px', display: 'block', marginBottom: '6px' }}>
              Content Type
            </label>
            <select
              value={inputType}
              onChange={(e) => setInputType(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #374151',
                background: '#1f2028',
                color: '#f3f4f6',
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
              border: '1px solid #374151',
              background: '#1f2028',
              color: '#f3f4f6',
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
              background: loading ? '#6b7280' : '#7c3aed',
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
        <Card style={{ marginBottom: '16px', padding: '16px', color: '#ef4444' }}>
          {error}
        </Card>
      )}

      {/* Result Card */}
      {result && (
        <Card style={{ padding: '20px' }}>
          {/* Verdict Badge */}
          <div
            style={{
              display: 'inline-block',
              padding: '10px 20px',
              borderRadius: '999px',
              background: 'rgba(255,255,255,0.06)',
              border: `2px solid ${getVerdictColor(result.verdict)}`,
              color: getVerdictColor(result.verdict),
              fontWeight: 'bold',
              fontSize: '16px',
              marginBottom: '16px'
            }}
          >
            {getVerdictLabel(result.verdict)}
          </div>

          {/* Credibility Score */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>Credibility Score</span>
              <span style={{ color: getScoreColor(result.credibility_score), fontWeight: 'bold' }}>
                {result.credibility_score}/100
              </span>
            </div>
            <div style={{ height: '8px', background: '#2e303a', borderRadius: '4px' }}>
              <div
                style={{
                  width: `${result.credibility_score}%`,
                  height: '100%',
                  background: getScoreColor(result.credibility_score),
                  borderRadius: '4px',
                  transition: 'width 0.3s ease'
                }}
              />
            </div>
          </div>

          {/* Summary */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#c084fc', margin: '0 0 8px 0', fontSize: '14px' }}>Summary</h4>
            <p style={{ color: '#f3f4f6', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
              {result.summary}
            </p>
          </div>

          {/* Confidence */}
          <div style={{ marginBottom: '16px' }}>
            <span style={{ color: '#9ca3af', fontSize: '12px' }}>
              Confidence: <strong style={{ color: '#f3f4f6' }}>{result.confidence}</strong>
            </span>
          </div>

          {/* Red Flags */}
          {result.red_flags && result.red_flags.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ color: '#ef4444', margin: '0 0 8px 0', fontSize: '14px' }}>
                ⚠️ Red Flags
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#f3f4f6', fontSize: '13px' }}>
                {result.red_flags.map((flag, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{flag}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Supporting Signals */}
          {result.supporting_signals && result.supporting_signals.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ color: '#22c55e', margin: '0 0 8px 0', fontSize: '14px' }}>
                ✅ Supporting Evidence
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#f3f4f6', fontSize: '13px' }}>
                {result.supporting_signals.map((signal, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{signal}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended Action */}
          {result.recommended_action && (
            <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(124, 58, 237, 0.1)', borderRadius: '8px' }}>
              <h4 style={{ color: '#c084fc', margin: '0 0 4px 0', fontSize: '13px' }}>
                💡 Recommendation
              </h4>
              <p style={{ color: '#f3f4f6', fontSize: '13px', margin: 0 }}>
                {result.recommended_action}
              </p>
            </div>
          )}

          {/* Sources */}
          {result.sources && result.sources.length > 0 && (
            <details style={{ marginTop: '16px' }}>
              <summary style={{ color: '#9ca3af', fontSize: '13px', cursor: 'pointer' }}>
                📚 Sources Checked ({result.sources.length})
              </summary>
              <div style={{ marginTop: '12px' }}>
                {result.sources.map((source, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '10px',
                      marginBottom: '8px',
                      background: '#16171d',
                      borderRadius: '6px',
                      borderLeft: `3px solid ${
                        source.stance === 'supports' ? '#22c55e' :
                        source.stance === 'contradicts' ? '#ef4444' : '#9ca3af'
                      }`
                    }}
                  >
                    <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#f3f4f6', marginBottom: '4px' }}>
                      {source.title}
                    </div>
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>
                      {source.domain} • Trust: {source.trust_score}/100 • Stance: {source.stance}
                    </div>
                    {source.notes && (
                      <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px', fontStyle: 'italic' }}>
                        {source.notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* Model Info */}
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #2e303a' }}>
            <span style={{ color: '#6b7280', fontSize: '11px' }}>
              Analyzed by: {result.model_used}
            </span>
          </div>
        </Card>
      )}
    </div>
  );
}
