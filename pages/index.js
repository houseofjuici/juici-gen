import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

export default function Home() {
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [chatHistory, setShowChatHistory] = useState(true);
  const [expandedView, setExpandedView] = useState(false);
  
  const messageContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize
  useEffect(() => {
    // Initialize marked.js for markdown rendering
    marked.setOptions({
      highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
      },
      langPrefix: 'hljs language-',
      breaks: true,
      gfm: true
    });

    // Add welcome message
    setMessages([{
      content: 'Hello! I\'m juici gen, your high-performance assistant. How can I help you today?',
      role: 'assistant'
    }]);
    
    // Focus input field
    if (inputRef.current) {
      inputRef.current.focus();
    }
    
    // Load Manrope font
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Manrope:wght@200;400;600;800&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { content: input, role: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      // Handle normal or specialized modes
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: input.trim(),
          mode: currentMode
        })
      });

      const data = await response.json();

      if (data.success) {
        setMessages(prev => [...prev, { content: data.data, role: 'assistant' }]);
      } else {
        setMessages(prev => [...prev, { 
          content: `Error: ${data.error || 'Something went wrong'}`, 
          role: 'assistant' 
        }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        content: 'Sorry, there was an error processing your request.', 
        role: 'assistant' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Download chat as text file
  const downloadChat = () => {
    const chatText = messages.map(msg => `${msg.role === 'user' ? 'You' : 'Juici'}: ${msg.content}`).join('\n\n');
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `juici-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Toggle expanded view
  const toggleExpandedView = () => {
    setExpandedView(!expandedView);
  };

  // Typing animation component
  const TypingIndicator = () => (
    <div className="typing-indicator">
      <div className="dot"></div>
      <div className="dot"></div>
      <div className="dot"></div>
    </div>
  );

  return (
    <div className="app-container">
      <Head>
        <title>Juici Gen</title>
        <meta name="description" content="Juici Gen - High-performance AI assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="app-header">
        <div className="logo">
          <div className="logo-icon">
            <span className="logo-text">juici</span>
          </div>
        </div>
        <div className="header-controls">
          <button className="icon-btn" onClick={downloadChat} aria-label="Download chat">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </button>
          <button className="icon-btn" onClick={toggleExpandedView} aria-label="Toggle view">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {expandedView ? (
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
              ) : (
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"></path>
              )}
            </svg>
          </button>
          <button className="icon-btn" onClick={() => setShowSettings(!showSettings)} aria-label="Settings">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </button>
        </div>
      </header>

      <main className={`app-main ${expandedView ? 'expanded' : ''}`}>
        {chatHistory && (
          <div className="chat-history">
            <div className="history-header">
              <h2>Conversations</h2>
            </div>
            <div className="history-list">
              <div className="history-item active">
                <span>Current Chat</span>
              </div>
              <div className="history-item">
                <span>New Chat</span>
              </div>
            </div>
          </div>
        )}

        <div className="chat-container">
          <div className="message-container" ref={messageContainerRef}>
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-content">
                  {msg.role === 'assistant' ? (
                    <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.content) }} />
                  ) : (
                    <div>{msg.content}</div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <div className="message-content typing-content">
                  <TypingIndicator />
                </div>
              </div>
            )}
          </div>

          <div className="input-container">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Message Juici..."
              rows={1}
            />
            <button 
              onClick={handleSendMessage} 
              className="send-button"
              disabled={!input.trim() || loading}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>

        {expandedView && (
          <div className="expanded-pane">
            <div className="expanded-header">
              <h2>Response Details</h2>
            </div>
            <div className="expanded-content">
              {messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
                <div dangerouslySetInnerHTML={{ __html: marked.parse(messages[messages.length - 1].content) }} />
              )}
            </div>
          </div>
        )}
      </main>

      {showSettings && (
        <div className="settings-modal">
          <div className="modal-content">
            <h2>Juici Settings</h2>
            <div className="settings-section">
              <h3>Response Mode</h3>
              <div className="mode-buttons">
                <button 
                  className={`mode-btn ${currentMode === null ? 'active' : ''}`}
                  onClick={() => setCurrentMode(null)}
                >
                  Standard
                </button>
                <button 
                  className={`mode-btn ${currentMode === 'summarize' ? 'active' : ''}`}
                  onClick={() => setCurrentMode('summarize')}
                >
                  Summarize
                </button>
                <button 
                  className={`mode-btn ${currentMode === 'expand' ? 'active' : ''}`}
                  onClick={() => setCurrentMode('expand')}
                >
                  Expand
                </button>
                <button 
                  className={`mode-btn ${currentMode === 'rewrite' ? 'active' : ''}`}
                  onClick={() => setCurrentMode('rewrite')}
                >
                  Rewrite
                </button>
                <button 
                  className={`mode-btn ${currentMode === 'task' ? 'active' : ''}`}
                  onClick={() => setCurrentMode('task')}
                >
                  Task
                </button>
              </div>
            </div>
            <div className="settings-section">
              <h3>Display Options</h3>
              <div className="toggle-option">
                <label>
                  <input 
                    type="checkbox" 
                    checked={chatHistory}
                    onChange={() => setShowChatHistory(!chatHistory)}
                  />
                  <span>Show Chat History</span>
                </label>
              </div>
            </div>
            <div className="settings-footer">
              <button className="close-btn" onClick={() => setShowSettings(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }
        
        html, body {
          font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
          background-color: #000000;
          color: #F3F4F6;
          height: 100%;
          overflow: hidden;
        }
        
        /* App container */
        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          max-height: 100vh;
          overflow: hidden;
        }
        
        /* Header */
        .app-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 2rem;
          background-color: rgba(10, 10, 10, 0.8);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          position: relative;
          z-index: 10;
        }
        
        .app-header::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, rgba(106, 27, 154, 0), rgba(106, 27, 154, 0.5), rgba(0, 137, 123, 0.5), rgba(106, 27, 154, 0));
        }
        
        .logo {
          display: flex;
          align-items: center;
        }
        
        .logo-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, #6A1B9A, #00897B);
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          overflow: hidden;
          animation: pulse 4s infinite ease-in-out;
        }
        
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 10px rgba(106, 27, 154, 0.5); }
          50% { box-shadow: 0 0 20px rgba(0, 137, 123, 0.7); }
        }
        
        .logo-icon:hover {
          animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
          0% { box-shadow: 0 0 10px rgba(252, 211, 77, 0.3); }
          50% { box-shadow: 0 0 20px rgba(252, 211, 77, 0.7); }
          100% { box-shadow: 0 0 10px rgba(252, 211, 77, 0.3); }
        }
        
        .logo-text {
          font-weight: 800;
          font-size: 1.2rem;
          background: linear-gradient(90deg, #F3F4F6, #FCD34D);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        
        .header-controls {
          display: flex;
          gap: 1rem;
        }
        
        .icon-btn {
          background: none;
          border: none;
          color: #F3F4F6;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .icon-btn:hover {
          background: rgba(106, 27, 154, 0.2);
          box-shadow: 0 0 10px rgba(106, 27, 154, 0.5);
          color: #FCD34D;
        }
        
        /* Main content */
        .app-main {
          flex: 1;
          display: flex;
          overflow: hidden;
        }
        
        .app-main.expanded {
          grid-template-columns: 250px 1fr 400px;
        }
        
        /* Chat history */
        .chat-history {
          width: 250px;
          background-color: rgba(10, 10, 10, 0.8);
          border-right: 1px solid rgba(255, 255, 255, 0.05);
          display: flex;
          flex-direction: column;
        }
        
        .history-header {
          padding: 1rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .history-header h2 {
          font-size: 1rem;
          font-weight: 600;
          color: #F3F4F6;
        }
        
        .history-list {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }
        
        .history-item {
          padding: 0.75rem;
          border-radius: 6px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.2s ease;
          font-weight: 200;
          font-size: 0.9rem;
        }
        
        .history-item:hover {
          background-color: rgba(255, 255, 255, 0.05);
        }
        
        .history-item.active {
          background-color: rgba(0, 137, 123, 0.2);
          border-left: 2px solid #00897B;
        }
        
        /* Chat container */
        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: relative;
        }
        
        .message-container {
          flex: 1;
          padding: 1rem 2rem;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          scroll-behavior: smooth;
        }
        
        .message-container::-webkit-scrollbar {
          width: 6px;
        }
        
        .message-container::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .message-container::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        
        .message-container::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
        
        .message {
          display: flex;
          max-width: 80%;
          animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
          align-self: flex-end;
        }
        
        .message.assistant {
          align-self: flex-start;
        }
        
        .message-content {
          padding: 1rem 1.5rem;
          border-radius: 12px;
          font-weight: 200;
          line-height: 1.6;
          position: relative;
          overflow: hidden;
        }
        
        .message.user .message-content {
          background-color: rgba(20, 20, 20, 0.8);
          border: 1px solid #00897B;
        }
        
        .message.assistant .message-content {
          background: linear-gradient(135deg, rgba(106, 27, 154, 0.2), rgba(0, 137, 123, 0.2));
          border: 1px solid rgba(255, 255, 255, 0.05);
          font-weight: 400;
          position: relative;
        }
        
        .message.assistant .message-content::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(circle at center, rgba(106, 27, 154, 0.05) 0%, transparent 70%);
          animation: pulse-bg 4s infinite ease-in-out;
          z-index: -1;
        }
        
        @keyframes pulse-bg {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.6; }
        }
        
        .typing-content {
          min-height: 24px;
          min-width: 60px;
        }
        
        .typing-indicator {
          display: flex;
          align-items: center;
          gap: 5px;
        }
        
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: linear-gradient(135deg, #6A1B9A, #00897B);
          animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.6; }
          40% { transform: scale(1); opacity: 1; }
        }
        
        /* Expanded pane */
        .expanded-pane {
          width: 400px;
          background-color: rgba(10, 10, 10, 0.8);
          border-left: 1px solid rgba(255, 255, 255, 0.05);
          display: flex;
          flex-direction: column;
        }
        
        .expanded-header {
          padding: 1rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .expanded-header h2 {
          font-size: 1rem;
          font-weight: 600;
          color: #F3F4F6;
        }
        
        .expanded-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }
        
        /* Input container */
        .input-container {
          padding: 1.5rem 2rem;
          display: flex;
          align-items: center;
          background-color: rgba(10, 10, 10, 0.8);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          position: relative;
        }
        
        .input-container::before {
          content: '';
          position: absolute;
          top: -1px;
          left: 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, rgba(106, 27, 154, 0), rgba(106, 27, 154, 0.5), rgba(0, 137, 123, 0.5), rgba(106, 27, 154, 0));
        }
        
        textarea {
          flex: 1;
          background-color: rgba(30, 30, 30, 0.5);
          border: none;
          border-radius: 8px;
          color: #F3F4F6;
          font-family: 'Manrope', sans-serif;
          font-size: 1rem;
          font-weight: 200;
          padding: 0.75rem 1rem;
          resize: none;
          outline: none;
          transition: all 0.2s ease;
        }
        
        textarea:focus {
          background-color: rgba(40, 40, 40, 0.7);
          box-shadow: 0 0 0 1px rgba(0, 137, 123, 0.5);
        }
        
        .send-button {
          background: none;
          border: none;
          color: #F3F4F6;
          cursor: pointer;
          margin-left: 0.75rem;
          padding: 0.5rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        
        .send-button:hover:not(:disabled) {
          color: #FCD34D;
          background: rgba(106, 27, 154, 0.2);
          box-shadow: 0 0 10px rgba(106, 27, 154, 0.5);
        }
        
        .send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        /* Settings modal */
        .settings-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(5px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 100;
          animation: fadeIn 0.2s ease-out;
        }
        
        .modal-content {
          background-color: rgba(20, 20, 20, 0.95);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 2rem;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
          position: relative;
          overflow: hidden;
        }
        
        .modal-content::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, #6A1B9A, #00897B);
        }
        
        .settings-modal h2 {
          font-weight: 800;
          margin-bottom: 1.5rem;
          color: #FCD34D;
        }
        
        .settings-section {
          margin-bottom: 1.5rem;
        }
        
        .settings-section h3 {
          font-weight: 600;
          margin-bottom: 1rem;
          color: #F3F4F6;
        }
        
        .mode-buttons {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
          gap: 0.75rem;
        }
        
        .mode-btn {
          background-color: rgba(40, 40, 40, 0.8);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: #F3F4F6;
          padding: 0.75rem;
          cursor: pointer;
          font-weight: 400;
          transition: all 0.2s ease;
        }
        
        .mode-btn:hover {
          background-color: rgba(60, 60, 60, 0.8);
          border-color: rgba(0, 137, 123, 0.5);
        }
        
        .mode-btn.active {
          background: linear-gradient(135deg, rgba(106, 27, 154, 0.3), rgba(0, 137, 123, 0.3));
          border-color: rgba(252, 211, 77, 0.5);
          color: #FCD34D;
        }
        
        .toggle-option {
          margin-bottom: 0.75rem;
        }
        
        .toggle-option label {
          display: flex;
          align-items: center;
          cursor: pointer;
        }
        
        .toggle-option input {
          margin-right: 0.75rem;
        }
        
        .settings-footer {
          display: flex;
          justify-content: flex-end;
          margin-top: 2rem;
        }
        
        .close-btn {
          background: linear-gradient(135deg, #6A1B9A, #00897B);
          border: none;
          border-radius: 6px;
          color: #F3F4F6;
          padding: 0.75rem 1.5rem;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.2s ease;
        }
        
        .close-btn:hover {
          box-shadow: 0 0 10px rgba(106, 27, 154, 0.5);
          transform: translateY(-1px);
        }
        
        /* Code blocks styling */
        pre {
          background-color: rgba(30, 30, 30, 0.8) !important;
          border-radius: 6px;
          padding: 1rem;
          overflow-x: auto;
          margin: 1rem 0;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        code {
          font-family: 'Fira Code', monospace;
          font-size: 0.9rem;
        }
        
        /* Markdown content styling */
        .message-content h1, 
        .message-content h2, 
        .message-content h3, 
        .message-content h4 {
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
          font-weight: 600;
        }
        
        .message-content p {
          margin-bottom: 1rem;
        }
        
        .message-content ul, 
        .message-content ol {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }
        
        .message-content li {
          margin-bottom: 0.5rem;
        }
        
        .message-content a {
          color: #00897B;
          text-decoration: none;
          border-bottom: 1px dotted #00897B;
        }
        
        .message-content a:hover {
          color: #FCD34D;
          border-bottom: 1px dotted #FCD34D;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
          .app-header {
            padding: 0.75rem 1rem;
          }
          
          .message-container {
            padding: 1rem;
          }
          
          .message {
            max-width: 90%;
          }
          
          .input-container {
            padding: 1rem;
          }
          
          .modal-content {
            width: 95%;
            padding: 1.5rem;
          }
          
          .mode-buttons {
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          }
        }
        
        @media (max-width: 480px) {
          .logo-text {
            font-size: 1rem;
          }
          
          .logo-icon {
            width: 36px;
            height: 36px;
          }
          
          .message {
            max-width: 95%;
          }
          
          .message-content {
            padding: 0.75rem 1rem;
          }
          
          .mode-buttons {
            grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
          }
        }
      `}</style>
    </div>
  );
}