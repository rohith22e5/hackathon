import React, { useState, useRef, useEffect } from 'react';
import { FaCommentDots, FaPaperPlane, FaTimes, FaRobot, FaMicrophone } from 'react-icons/fa';
import { LiveAPIProvider } from "../contexts/LiveAPIContext";
import ControlTray from "./control-tray/ControlTray";
import cn from "classnames";
import type { LiveClientOptions } from "../types";

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showVoiceComponent, setShowVoiceComponent] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hi! I'm your educational assistant. How can I help you learn today?", sender: 'bot' }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Live API related state and refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleVoiceClick = () => {
    setShowVoiceComponent(!showVoiceComponent);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { id: Date.now(), text: input, sender: 'user' };
    const updatedMessages = [...messages, userMsg];
    
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages.slice(1).map(msg => ({
        text: msg.text,
        sender: msg.sender
      }));
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMsg.text,
          history: history
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      
      const botMsg: Message = { 
        id: Date.now() + 1, 
        text: data.response, 
        sender: 'bot' 
      };
      
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting right now. Please check if the backend is running.",
        sender: 'bot'
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // API setup for Live API
  const API_KEY = import.meta.env.VITE_GEMINI_API_KEY as string;
  if (typeof API_KEY !== "string" || !API_KEY) {
    console.warn("VITE_GEMINI_API_KEY not set in environment variables");
    // For now, we'll use a placeholder or disable the live API functionality
  }

  const apiOptions: LiveClientOptions = {
    apiKey: API_KEY || "",
  };

  return (
    <div className="fixed bottom-20 right-4 z-[60] flex flex-col items-end sm:bottom-20 sm:right-6">
      {isOpen && (
        <div className="mb-4 flex h-[500px] w-[90vw] flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-xl sm:w-[350px]">
          <div className="flex items-center justify-between bg-blue-600 p-4 text-white">
            <div className="flex items-center gap-2">
              <FaRobot className="text-xl" />
              <h3 className="font-semibold">EduSupport</h3>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={handleVoiceClick} className="text-white hover:text-gray-200">
                <FaMicrophone />
              </button>
              <button onClick={toggleChat} className="text-white hover:text-gray-200">
                <FaTimes />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto bg-gray-50 p-4">
            {showVoiceComponent ? (
              // Voice Mode - Live API Integration
              <div className="h-full w-full bg-white rounded-lg overflow-hidden relative">
                <LiveAPIProvider options={apiOptions}>
                  <div className="streaming-console h-full relative">
                    <main className="h-full flex flex-col relative">
                      <div className="main-app-area flex-1 relative">
                        <video
                          className={cn("stream w-full h-full object-cover", {
                            hidden: !videoRef.current || !videoStream,
                          })}
                          ref={videoRef}
                          autoPlay
                          playsInline
                        />
                      </div>
                      <div className="relative">
                        <ControlTray
                          videoRef={videoRef}
                          supportsVideo={true}
                          onVideoStreamChange={setVideoStream}
                          enableEditingSettings={true}
                        />
                      </div>
                    </main>
                  </div>
                </LiveAPIProvider>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`mb-3 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                        msg.sender === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-800 shadow-sm border border-gray-100'
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white text-gray-500 shadow-sm border border-gray-100 rounded-lg px-4 py-2 text-sm">
                      Thinking...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {!showVoiceComponent && (
            <form onSubmit={handleSend} className="border-t border-gray-200 bg-white p-3">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question..."
                  disabled={isLoading}
                  className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="rounded-full bg-blue-600 p-2 text-white hover:bg-blue-700 transition-colors disabled:bg-blue-400"
                >
                  <FaPaperPlane className="text-sm" />
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      <button
        onClick={toggleChat}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-transform hover:scale-105 hover:bg-blue-700 focus:outline-none"
        aria-label="Open chat"
      >
        {isOpen ? <FaTimes className="text-2xl" /> : <FaCommentDots className="text-2xl" />}
      </button>
    </div>
  );
};

export default ChatWidget;