import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import SourceChecking from './pages/SourceChecking';
import BotDetection from './pages/BotDetection';
import UrlSafety from './pages/UrlSafety';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/source-checking" element={<SourceChecking />} />
        <Route path="/bot-detection" element={<BotDetection />} />
        <Route path="/url-safety" element={<UrlSafety />} />
      </Routes>
    </Router>
  );
}

export default App;
