import React, { useState, useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

function VoicePanel() {
  const [status, setStatus] = useState('Idle');
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);
  const wakeWord = 'proton';
  const [isListening, setIsListening] = useState(false);
  const isCommandMode = useRef(false); // 🔸 To track whether in command mode

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      toast.error("Speech Recognition not supported in this browser.");
      return;
    }

    if (isListening) return;

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-IN';
    recognitionRef.current = recognition;

    setIsListening(true);

    recognition.onstart = () => {
      setStatus('Listening Wake Word');
      toast.info("🎙️ Listening for wake word: 'Proton'");
    };

    recognition.onresult = async (event) => {
      const text = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
      console.log("Detected: ", text);

      if (!isCommandMode.current && text.includes(wakeWord)) {
        toast.success("🟢 Wake word detected: Proton");
        speak("Yes, I am listening.", () => {
          isCommandMode.current = true;
          setStatus('Listening Command');
        });
      } else if (isCommandMode.current) {
        setTranscript(text);
        toast.success(`🧠 You said: ${text}`);
        setStatus('Processing Command');

        try {
          const response = await axios.post('http://localhost:8001/voice-command', { command: text });
          const reply = response.data.response;

          speak(reply, () => {
            isCommandMode.current = false;
            setStatus('Listening Wake Word');
          });

          if (response.data.url) {
            window.open(response.data.url, '_blank');
          }
        } catch (error) {
          console.error("Voice API error:", error);
          speak("Sorry, there was a problem reaching the assistant.", () => {
            isCommandMode.current = false;
            setStatus('Listening Wake Word');
          });
        }
      }
    };

    recognition.onerror = (err) => {
      console.error(err);
      toast.error('Speech recognition error.');
    };

    recognition.onend = () => {
      if (isListening) {
        recognition.start(); // 🔥 Keep microphone always ON
      } else {
        setStatus('Idle');
        toast.info("Listening stopped. Click start to listen again.");
      }
    };

    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    isCommandMode.current = false;
    setStatus('Idle');
    toast.info('🛑 Proton stopped.');
  };

  const speak = (text, callback) => {
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-IN';

      utterance.onstart = () => {
        setStatus('Speaking');
      };

      utterance.onend = () => {
        if (isListening) {
          if (isCommandMode.current) {
            setStatus('Listening Command');
          } else {
            setStatus('Listening Wake Word');
          }
        } else {
          setStatus('Idle');
        }
        if (callback) callback();
      };

      utterance.onerror = (e) => {
        console.error('Speech synthesis error:', e);
        if (isListening) {
          if (isCommandMode.current) {
            setStatus('Listening Command');
          } else {
            setStatus('Listening Wake Word');
          }
        } else {
          setStatus('Idle');
        }
        if (callback) callback();
      };

      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error('Speech synthesis failed:', error);
      setStatus('Idle');
      if (callback) callback();
    }
  };

  const getAssistantGif = () => {
    switch (status) {
      case 'Listening Wake Word':
        return '/assistant_gifs/listening_wake_word.gif';
      case 'Listening Command':
        return '/assistant_gifs/listening_command.gif';
      case 'Speaking':
        return '/assistant_gifs/speaking.gif';
      default:
        return '/assistant_gifs/idle.gif';
    }
  };

  return (
    <div className="voice-panel">
      <h2>🎤 Proton Voice Assistant</h2>

      <div className={`assistant-face ${status === 'Listening Wake Word' || status === 'Listening Command' || status === 'Speaking' ? 'active' : ''}`}>
        <img src={getAssistantGif()} alt="Assistant Animation" style={{ width: '120px', height: '120px', borderRadius: '50%' }} />
      </div>

      <p>Status: {status}</p>
      {transcript && <p><strong>You:</strong> {transcript}</p>}

      {!isListening && <button onClick={startListening} className="start-button">Start Proton</button>}
      {isListening && <button onClick={stopListening} className="stop-button">Stop Proton</button>}
    </div>
  );
}

export default VoicePanel;
