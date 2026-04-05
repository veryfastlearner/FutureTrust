import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UrlScanner } from '../components/UrlScanner';

function UrlSafety() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0f' }}>
      {/* Header */}
      <header style={{
        padding: '20px 32px',
        borderBottom: '1px solid #1f2937',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#0a0a0f',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div 
          onClick={() => navigate('/')}
          style={{ 
            fontSize: '24px', 
            fontWeight: '700', 
            color: '#fff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '28px', height: '28px', color: '#7c3aed' }}>
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          FutureTrust
        </div>
        <nav style={{ display: 'flex', gap: '24px' }}>
          <span onClick={() => navigate('/')} style={{ color: '#9ca3af', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Home</span>
          <span onClick={() => navigate('/source-checking')} style={{ color: '#9ca3af', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Source Checker</span>
          <span onClick={() => navigate('/bot-detection')} style={{ color: '#9ca3af', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Bot Detection</span>
          <span style={{ color: '#fff', textDecoration: 'none', fontSize: '14px' }}>URL Safety</span>
        </nav>
      </header>

      {/* Tool Header */}
      <div style={{
        padding: '60px 32px 40px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #111118 0%, #0a0a0f 100%)'
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
          <span style={{ color: '#22c55e', fontSize: '14px', fontWeight: '600' }}>URL Safety Check</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: '700',
          color: '#fff',
          margin: '0 0 16px'
        }}>
          URL Scanner
        </h1>

        <p style={{
          fontSize: '18px',
          color: '#6b7280',
          maxWidth: '640px',
          margin: '0 auto',
          lineHeight: '1.6'
        }}>
          Check URLs for malicious content, phishing attempts, and credibility using our ML model and AI verification.
        </p>
      </div>

      {/* URL Scanner Component */}
      <div style={{ padding: '0 32px 80px' }}>
        <UrlScanner />
      </div>
    </div>
  );
}

export default UrlSafety;
