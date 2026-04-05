import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UrlScanner } from '../components/UrlScanner';

function UrlSafety() {
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
          <span style={{ color: '#111827', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }}>URL Safety</span>
          <span onClick={() => navigate('/source-checking')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Source Checker</span>
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
          <span style={{ color: '#22c55e', fontSize: '14px', fontWeight: '600' }}>URL Safety Check</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 48px)',
          fontWeight: '700',
          color: '#111827',
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
