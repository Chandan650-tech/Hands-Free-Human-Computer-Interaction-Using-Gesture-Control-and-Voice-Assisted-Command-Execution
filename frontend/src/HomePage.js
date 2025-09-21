import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const navigateToGesture = () => {
    navigate('/gesture');
  };

  const navigateToVoice = () => {
    navigate('/voice');
  };

  return (
    <div className="home-container">
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        Welcome to Laptop Gesture & Proton Control
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        Select your control mode:
      </motion.p>

      <motion.div
        className="nav-buttons"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <button className="nav-button" onClick={navigateToGesture}>Gesture Control</button>
        <button className="nav-button" onClick={navigateToVoice}>Voice Assistant</button>
      </motion.div>
    </div>
  );
}

export default HomePage;
