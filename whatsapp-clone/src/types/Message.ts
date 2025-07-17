export interface Usuario {
  id: string;
  nome: string;
  avatar?: string;
}

export interface Mensagem {
  id: string;
  texto: string;
  usuario: Usuario;
  timestamp: string;
  isMine: boolean;
} 