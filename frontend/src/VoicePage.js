import React from 'react';
import { useNavigate } from 'react-router-dom';
import VoicePanel from './components/VoicePanel';
import './VoicePage.css';

function VoicePage() {
  const navigate = useNavigate();

  return (
    <div className="voice-page">
      <h1 className="voice-heading">Proton Voice Assistant</h1>
      <VoicePanel />
      <button className="back-button" onClick={() => navigate('/')}>Back to Home</button>
    </div>
  );
}

export default VoicePage;
