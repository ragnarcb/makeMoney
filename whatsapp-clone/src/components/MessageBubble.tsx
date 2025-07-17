import React from 'react';
import { Mensagem } from '../types/Message';
import './MessageBubble.css';

interface MessageBubbleProps {
  mensagem: Mensagem;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ mensagem }) => {
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`message-wrapper ${mensagem.isMine ? 'mine' : 'theirs'}`}>
      <div className="message-bubble">
        <div className="message-content">
          {!mensagem.isMine && (
            <div className="sender-name">{mensagem.usuario.nome}</div>
          )}
          <div className="message-text">{mensagem.texto}</div>
          <div className="message-meta">
            <span className="message-time">{formatTime(mensagem.timestamp)}</span>
            {mensagem.isMine && (
              <div className="message-status">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M1.5 8.5L5.5 12.5L14.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M5.5 8.5L9.5 12.5L18.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble; 