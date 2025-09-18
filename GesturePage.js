import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './GesturePage.css';

function GesturePage() {
  const [isTracking, setIsTracking] = useState(false);
  const [gestureLogs, setGestureLogs] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const startTracking = async () => {
    try {
      setError('');
      await axios.get('http://localhost:8000/start');
      setIsTracking(true);
    } catch (err) {
      console.error('Error starting tracking:', err);
      setError('Failed to start gesture tracking.');
    }
  };

  const stopTracking = async () => {
    try {
      setError('');
      await axios.get('http://localhost:8000/stop');
      setIsTracking(false);
    } catch (err) {
      console.error('Error stopping tracking:', err);
      setError('Failed to stop gesture tracking.');
    }
  };

  const getLogs = async () => {
    try {
      setError('');
      const response = await axios.get('http://localhost:8000/logs');
      if (Array.isArray(response.data.logs)) {
        setGestureLogs(response.data.logs.reverse());
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to fetch gesture logs.');
    }
  };

  useEffect(() => {
    let interval;
    if (isTracking) {
      interval = setInterval(getLogs, 3000);
    }
    return () => clearInterval(interval);
  }, [isTracking]);

  return (
    <div className="gesture-page">
      <h1>Gesture Control</h1>

      <div className="gesture-controls">
        <button className="gesture-button" onClick={startTracking} disabled={isTracking}>
          Start
        </button>
        <button className="gesture-button" onClick={stopTracking} disabled={!isTracking}>
          Stop
        </button>
        <button className="gesture-button" onClick={getLogs}>
          Recent Logs
        </button>
      </div>

      {error && <p className="gesture-error">{error}</p>}

      <div className="gesture-logs">
        <h3>Detected Gestures</h3>
        {gestureLogs.length > 0 ? (
          <ul className="gesture-list">
            {gestureLogs.map((log, index) => (
              <li key={index} className="gesture-item">
                {log}
              </li>
            ))}
          </ul>
        ) : (
          <p className="gesture-error">No gestures detected yet.</p>
        )}
      </div>

      {/* Back to Home Button - Positioned at bottom center */}
      <div className="back-home-container">
        <button className="gesture-button back-button" onClick={() => navigate('/')}>
          ⬅ Back to Home
        </button>
      </div>
    </div>
  );
}

export default GesturePage;
