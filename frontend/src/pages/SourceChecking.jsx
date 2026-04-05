import { useNavigate } from 'react-router-dom';
import { CredibilityChecker } from '../components/CredibilityChecker';

function SourceChecking() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: '#faf9f6' }}>
      {/* Header */}
      <header style={{
        padding: '20px 32px',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#ffffff'
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
          <span style={{ color: '#111827', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }}>Source Checker</span>
          <span onClick={() => navigate('/bot-detection')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Bot Detection</span>
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
          background: 'rgba(34, 197, 94, 0.1)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: '999px',
          marginBottom: '24px'
        }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '20px', height: '20px', color: '#22c55e' }}>
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span style={{ color: '#22c55e', fontSize: '14px', fontWeight: '600' }}>Source & Credibility</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: '700',
          color: '#111827',
          margin: '0 0 16px'
        }}>
          Multi-Layer Source Checker
        </h1>

        <p style={{
          fontSize: '18px',
          color: '#6b7280',
          maxWidth: '640px',
          margin: '0 auto',
          lineHeight: '1.6'
        }}>
          Our AI-powered pipeline inspects content through multiple verification layers, 
          from URL safety to final verdict synthesis.
        </p>
      </div>

      {/* Pipeline Steps */}
      <div style={{
        padding: '0 32px 40px',
        maxWidth: '1000px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          {[
            { step: 1, name: 'Inspector' },
            { step: 2, name: 'URL Check' },
            { step: 3, name: 'Bot Detection' },
            { step: 4, name: 'Final Verdict' }
          ].map((item) => (
            <div key={item.step} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 20px',
              background: '#16171d',
              border: '1px solid #2e303a',
              borderRadius: '999px'
            }}>
              <span style={{
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#7c3aed',
                borderRadius: '50%',
                fontSize: '12px',
                fontWeight: '600',
                color: '#fff'
              }}>{item.step}</span>
              <span style={{ color: '#9ca3af', fontSize: '14px', fontWeight: '500' }}>{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Checker Component */}
      <div style={{ padding: '0 32px 80px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <CredibilityChecker />
        </div>
      </div>
    </div>
  );
}

export default SourceChecking;
