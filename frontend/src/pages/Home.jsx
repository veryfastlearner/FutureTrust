import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  const axes = [
    {
      id: 'source',
      title: 'Source & Credibility',
      subtitle: 'Multi-layer verification',
      description: 'Our AI Inspector analyzes content through multiple layers: URL safety checks, account verification, and a Final Frontier Agent that synthesizes all findings into a readable verdict.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: '48px', height: '48px' }}>
          <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      color: '#22c55e',
      available: true
    },
    {
      id: 'misinformation',
      title: 'Misinformation Detection',
      description: 'Advanced pipeline of agents that cross-reference claims against trusted sources, detect narrative patterns, and identify coordinated disinformation campaigns.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: '48px', height: '48px' }}>
          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
        </svg>
      ),
      color: '#f59e0b',
      available: false
    },
    {
      id: 'ai-detection',
      title: 'AI Generation Detection',
      description: 'Detect synthetic media, AI-generated text, and deepfakes. Verify content authenticity and establish provenance chains for digital assets.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: '48px', height: '48px' }}>
          <path d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      color: '#8b5cf6',
      available: false
    }
  ];

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
          <span onClick={() => navigate('/')} style={{ color: '#111827', textDecoration: 'none', fontSize: '14px', cursor: 'pointer', fontWeight: 500 }}>Home</span>
          <span onClick={() => navigate('/url-safety')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>URL Safety</span>
          <span onClick={() => navigate('/source-checking')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Source Checker</span>
          <span onClick={() => navigate('/bot-detection')} style={{ color: '#6b7280', textDecoration: 'none', fontSize: '14px', cursor: 'pointer' }}>Bot Detection</span>
        </nav>
      </header>
      <section style={{
        padding: '120px 24px 80px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #ffffff 0%, #faf9f6 100%)'
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          background: 'rgba(124, 58, 237, 0.1)',
          border: '1px solid rgba(124, 58, 237, 0.3)',
          borderRadius: '999px',
          marginBottom: '32px'
        }}>
          
        </div>

        <h1 style={{
          fontSize: 'clamp(40px, 8vw, 72px)',
          fontWeight: '700',
          lineHeight: '1.1',
          color: '#111827',
          margin: '0 0 24px',
          letterSpacing: '-0.02em'
        }}>
          FutureTrust
        </h1>
        
        <h2 style={{
          fontSize: 'clamp(24px, 4vw, 40px)',
          fontWeight: '500',
          lineHeight: '1.3',
          color: '#4b5563',
          margin: '0 0 32px',
          maxWidth: '800px',
          marginLeft: 'auto',
          marginRight: 'auto'
        }}>
          Intelligent verification systems for the age of misinformation
        </h2>

        <p style={{
          fontSize: '18px',
          lineHeight: '1.7',
          color: '#6b7280',
          maxWidth: '640px',
          margin: '0 auto 48px'
        }}>
          Verify sources, detect misinformation, and authenticate content with our AI-powered pipeline. 
          Built for journalists, researchers, and anyone who values information integrity.
        </p>

        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => navigate('/source-checking')}
            style={{
              padding: '16px 32px',
              background: '#7c3aed',
              color: '#ffffff',
              border: 'none',
              borderRadius: '999px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = '#6d28d9';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#7c3aed';
              e.target.style.transform = 'translateY(0)';
            }}
          >
            Try Source Checker
          </button>
        </div>
      </section>

      {/* Three Axes Section */}
      <section style={{ padding: '80px 24px', background: '#faf9f6' }}>
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <h3 style={{
            fontSize: 'clamp(32px, 5vw, 48px)',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 16px'
          }}>
            Three pillars of trust
          </h3>
          <p style={{
            fontSize: '18px',
            color: '#6b7280',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            Comprehensive verification across sources, narratives, and synthetic content
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 16px'
        }}>
          {axes.map((axis) => (
            <div
              key={axis.id}
              onClick={() => axis.available && navigate('/source-checking')}
              style={{
                padding: '32px',
                background: '#ffffff',
                border: `1px solid ${axis.available ? axis.color : '#e5e7eb'}`,
                borderRadius: '16px',
                cursor: axis.available ? 'pointer' : 'default',
                transition: 'all 0.3s',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)'
              }}
              onMouseEnter={(e) => {
                if (axis.available) {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = `0 20px 40px ${axis.color}15`;
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)';
              }}
            >
            
              <div style={{
                width: '80px',
                height: '80px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `${axis.color}15`,
                borderRadius: '20px',
                marginBottom: '24px',
                color: axis.color
              }}>
                {axis.icon}
              </div>

              <h4 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#111827',
                margin: '0 0 8px'
              }}>
                {axis.title}
              </h4>

              <p style={{
                fontSize: '14px',
                color: axis.color,
                fontWeight: '500',
                margin: '0 0 16px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                {axis.subtitle}
              </p>

              <p style={{
                fontSize: '15px',
                lineHeight: '1.6',
                color: '#6b7280',
                margin: 0
              }}>
                {axis.description}
              </p>

              {axis.available && (
                <div style={{
                  marginTop: '24px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: axis.color,
                  fontSize: '14px',
                  fontWeight: '500'
                }}>
                  <span>Try it now</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section style={{ padding: '80px 24px', background: '#111118' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h3 style={{
            fontSize: '32px',
            fontWeight: '600',
            color: '#fff',
            margin: '0 0 48px'
          }}>
            How Source Checking Works
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {[
              { num: '01', title: 'Content Inspector', desc: 'First layer scans for URLs, accounts, and obvious red flags' },
              { num: '02', title: 'URL Safety Check', desc: 'RF model + AI agent verify link credibility and content' },
              { num: '03', title: 'Final Frontier Agent', desc: 'Synthesizes all findings into a readable verdict' }
            ].map((step, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '24px',
                padding: '24px',
                background: '#16171d',
                borderRadius: '12px',
                textAlign: 'left'
              }}>
                <span style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#7c3aed',
                  minWidth: '48px'
                }}>{step.num}</span>
                <div>
                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: '#fff',
                    margin: '0 0 8px'
                  }}>{step.title}</h4>
                  <p style={{
                    fontSize: '15px',
                    color: '#9ca3af',
                    margin: 0,
                    lineHeight: '1.6'
                  }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
