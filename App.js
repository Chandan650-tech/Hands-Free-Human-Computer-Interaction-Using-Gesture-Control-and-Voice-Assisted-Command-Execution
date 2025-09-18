import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import GesturePage from './GesturePage';
import VoicePage from './VoicePage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/gesture" element={<GesturePage />} />
        <Route path="/voice" element={<VoicePage />} />
      </Routes>
    </Router>
  );
}

export default App;
