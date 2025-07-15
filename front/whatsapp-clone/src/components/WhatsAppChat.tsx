import React from 'react';
import { Mensagem } from '../types/Message';
import MessageBubble from './MessageBubble';
import './WhatsAppChat.css';

interface WhatsAppChatProps {
  msgs: Mensagem[];
  contactName: string;
  contactAvatar?: string;
}

const WhatsAppChat: React.FC<WhatsAppChatProps> = ({ msgs, contactName, contactAvatar }) => {
  return (
    <div className="whatsapp-container">
      <div className="whatsapp-chat">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="back-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M15.41 16.59L10.83 12L15.41 7.41L14 6L8 12L14 18L15.41 16.59Z" fill="currentColor"/>
              </svg>
            </div>
            <div className="contact-avatar">
              {contactAvatar ? (
                <img src={contactAvatar} alt={contactName} />
              ) : (
                <div className="default-avatar">
                  {contactName.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className="contact-info">
              <div className="contact-name">{contactName}</div>
              <div className="contact-status">online</div>
            </div>
          </div>
          <div className="header-actions">
            <button className="action-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M17 10.5V7C17 4.24 14.76 2 12 2S7 4.24 7 7V10.5C6.45 10.5 6 10.95 6 11.5V18.5C6 19.05 6.45 19.5 7 19.5H17C17.55 19.5 18 19.05 18 18.5V11.5C18 10.95 17.55 10.5 17 10.5ZM8.5 7C8.5 5.07 10.07 3.5 12 3.5S15.5 5.07 15.5 7V10.5H8.5V7Z" fill="currentColor"/>
              </svg>
            </button>
            <button className="action-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 8C13.1 8 14 7.1 14 6S13.1 4 12 4 10 4.9 10 6 10.9 8 12 8ZM12 10C10.9 10 10 10.9 10 12S10.9 14 12 14 14 13.1 14 12 13.1 10 12 10ZM12 16C10.9 16 10 16.9 10 18S10.9 20 12 20 14 19.1 14 18 13.1 16 12 16Z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-container">
          <div className="messages-list">
            {msgs.map((mensagem) => (
              <MessageBubble key={mensagem.id} mensagem={mensagem} />
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <button className="attach-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M16.5 6V17.5C16.5 19.43 14.93 21 13 21S9.5 19.43 9.5 17.5V5C9.5 3.62 10.62 2.5 12 2.5S14.5 3.62 14.5 5V15.5C14.5 16.05 14.05 16.5 13.5 16.5S12.5 16.05 12.5 15.5V6H11V15.5C11 16.88 12.12 18 13.5 18S16 16.88 16 15.5V5C16 2.79 14.21 1 12 1S8 2.79 8 5V17.5C8 20.26 10.24 22.5 13 22.5S18 20.26 18 17.5V6H16.5Z" fill="currentColor"/>
              </svg>
            </button>
            <div className="text-input">
              <input type="text" placeholder="Mensagem" disabled />
            </div>
            <button className="emoji-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
                <path d="8 14s1.5 2 4 2 4-2 4-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="9" y1="9" x2="9.01" y2="9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="15" y1="9" x2="15.01" y2="9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
            <button className="send-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppChat; 