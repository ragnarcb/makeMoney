import React, { useState, useEffect } from 'react';
import WhatsAppChat from './components/WhatsAppChat';
import { Mensagem } from './types/Message';
import './App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Mensagem[]>([]);
  const [contactName, setContactName] = useState<string>('Ana');

  // Load messages from server on component mount
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const response = await fetch('/api/messages');
        const data = await response.json();
        
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages);
          // Set contact name from first message that's not mine
          const otherUser = data.messages.find((msg: Mensagem) => !msg.isMine);
          if (otherUser) {
            setContactName(otherUser.usuario.nome);
          }
        } else {
          // Fallback to example messages if no messages from server
          setMessages(mensagensExemplo);
          setContactName('Prof. Marina (28 anos)');
        }
      } catch (error) {
        console.error('Failed to load messages from server:', error);
        // Fallback to example messages
        setMessages(mensagensExemplo);
        setContactName('Prof. Marina (28 anos)');
      }
    };

    loadMessages();

    // Listen for message updates from the server
    const handleMessageUpdate = (event: CustomEvent) => {
      const { messages: newMessages, participants } = event.detail;
      setMessages(newMessages);
      
      // Update contact name from participants
      if (participants && participants.length > 0) {
        const otherUser = newMessages.find((msg: Mensagem) => !msg.isMine);
        if (otherUser) {
          setContactName(otherUser.usuario.nome);
        }
      }
    };

    window.addEventListener('updateMessages', handleMessageUpdate as EventListener);

    return () => {
      window.removeEventListener('updateMessages', handleMessageUpdate as EventListener);
    };
  }, []);

  // Example messages (fallback)
  const mensagensExemplo: Mensagem[] = [
    {
      id: '1',
      texto: 'Oi professora! Preciso conversar sobre minha nota na prova de literatura... 😅',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:30:00Z',
      isMine: false,
    },
    {
      id: '2',
      texto: 'Olá Lucas! Claro, podemos conversar. Qual foi sua dúvida sobre a prova?',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:32:00Z',
      isMine: true,
    },
    {
      id: '3',
      texto: 'Bom, tirei 6.5 e queria saber se tem como melhorar... Talvez uma revisão extra? 😏',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:33:00Z',
      isMine: false,
    },
    {
      id: '4',
      texto: 'Hmm, posso te ajudar com aulas particulares. Que tal amanhã após as aulas?',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:35:00Z',
      isMine: true,
    },
    {
      id: '5',
      texto: 'Perfeito! Mas professora... você sempre fica tão linda quando explica as coisas... 😍',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:36:00Z',
      isMine: false,
    },
    {
      id: '6',
      texto: 'Lucas, vamos manter o foco nos estudos, ok? 😊',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:38:00Z',
      isMine: true,
    },
    {
      id: '7',
      texto: 'Desculpa professora! Mas é que você tem uma voz tão... envolvente quando fala sobre poesia 🥵',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:40:00Z',
      isMine: false,
    },
    {
      id: '8',
      texto: 'Lucas, isso não é apropriado. Vamos focar na literatura, não em... outras coisas 😳',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:42:00Z',
      isMine: true,
    },
    {
      id: '9',
      texto: 'Mas professora, você não sente essa... tensão entre nós? Quando você passa perto da minha mesa... 😈',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:45:00Z',
      isMine: false,
    },
    {
      id: '10',
      texto: 'Lucas, isso é completamente inapropriado! Sou sua professora! 😤',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:47:00Z',
      isMine: true,
    },
    {
      id: '11',
      texto: 'Mas professora, você também sente, não sente? Vejo como você me olha durante as aulas... 😏',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:50:00Z',
      isMine: false,
    },
    {
      id: '12',
      texto: 'Lucas, pare com isso imediatamente! Isso pode custar meu emprego! 😰',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:52:00Z',
      isMine: true,
    },
    {
      id: '13',
      texto: 'Mas professora, imagine só... você e eu, sozinhos na sala de aula... depois do horário... 😈',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T14:55:00Z',
      isMine: false,
    },
    {
      id: '14',
      texto: 'Lucas, vou ter que reportar isso para a direção! Isso é assédio! 😡',
      usuario: {
        id: 'professora',
        nome: 'Prof. Marina (28 anos)',
      },
      timestamp: '2024-01-15T14:57:00Z',
      isMine: true,
    },
    {
      id: '15',
      texto: 'Desculpa professora! Foi só uma brincadeira... Mas você sabe que sente algo, né? 😉',
      usuario: {
        id: 'aluno',
        nome: 'Lucas (22 anos)',
      },
      timestamp: '2024-01-15T15:00:00Z',
      isMine: false,
    },
  ];

  return (
    <div className="App">
      <WhatsAppChat 
        msgs={messages}
        contactName={contactName}
      />
    </div>
  );
};

export default App; 