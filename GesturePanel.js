import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../App.css';
import './GesturePanel.css';

function GesturePanel() {
  const [isTracking, setIsTracking] = useState(false);
  const [gestureLogs, setGestureLogs] = useState([]);
  const [error, setError] = useState('');

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
    <div className="gesture-panel">
      <h2>🖐️ Gesture Control</h2>
      <div className="controls">
        <button onClick={startTracking} disabled={isTracking}>Start</button>
        <button onClick={stopTracking} disabled={!isTracking}>Stop</button>
        <button onClick={getLogs}>Recent Logs</button>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="log-panel">
        <h3>Detected Gestures</h3>
        {gestureLogs.length > 0 ? (
          <ul>
            {gestureLogs.map((log, index) => (
              <li key={index}>{log}</li>
            ))}
          </ul>
        ) : <p>No gestures detected.</p>}
      </div>
    </div>
  );
}

export default GesturePanel;
