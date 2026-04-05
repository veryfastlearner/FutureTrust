import { useState } from 'react'
import { UrlScanner } from './components/UrlScanner'
import { CredibilityChecker } from './components/CredibilityChecker'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('url') // 'url' or 'credibility'

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">FT</span>
          <span className="logo-text">FutureTrust</span>
        </div>
      </header>

      <main className="app-main">
        {/* Tab Navigation */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '8px', 
          marginBottom: '20px',
          padding: '0 20px'
        }}>
          <button
            onClick={() => setActiveTab('url')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'url' ? '#7c3aed' : '#2e303a',
              color: 'white',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'url' ? 'bold' : 'normal'
            }}
          >
            🔒 URL Scanner
          </button>
          <button
            onClick={() => setActiveTab('credibility')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'credibility' ? '#7c3aed' : '#2e303a',
              color: 'white',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'credibility' ? 'bold' : 'normal'
            }}
          >
            🔍 Credibility Checker
          </button>
        </div>

        {/* Active Component */}
        {activeTab === 'url' ? <UrlScanner /> : <CredibilityChecker />}
      </main>
    </div>
  )
}

export default App
