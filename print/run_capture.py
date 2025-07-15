#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script helper para executar diferentes modos de captura de mensagens WhatsApp
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import os

# Configurar codificação UTF-8 para Windows
if sys.platform == "win32":
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        pass

class WhatsAppCaptureHelper:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.main_script = self.script_dir / "whatsapp_screenshot_automation.py"
        
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        try:
            import playwright
            print("[OK] Playwright instalado")
            return True
        except ImportError:
            print("[INFO] Playwright não encontrado. Instalando...")
            self.install_dependencies()
            return False
            
    def install_dependencies(self):
        """Instala as dependências necessárias"""
        try:
            # Instalar playwright
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            
            # Instalar browsers do playwright
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            
            print("[OK] Dependências instaladas com sucesso")
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Erro ao instalar dependências: {e}")
            sys.exit(1)
            
    def run_capture(self, mode="individual", headless=True, include_header=True, url="http://localhost:8089", scroll_single_image=False):
        """Executa a captura com os parâmetros especificados"""
        cmd = [
            sys.executable,
            str(self.main_script),
            "--mode", mode,
            "--url", url,
            "--output", f"screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ]
        
        if headless:
            cmd.append("--headless")
            
        if include_header:
            cmd.append("--include-header")
            
        if scroll_single_image:
            cmd.append("--scroll-single-image")
            
        try:
            print(f"[INFO] Executando: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Erro na execução: {e}")
            print(f"Saída de erro: {e.stderr}")
            
    def interactive_menu(self):
        """Menu interativo para seleção de opções"""
        print("\n" + "="*60)
        print("AUTOMAÇÃO DE CAPTURA WHATSAPP")
        print("="*60)
        
        # Verificar dependências
        if not self.check_dependencies():
            return
            
        print("\n[MENU] ESCOLHA O MODO DE CAPTURA:")
        print("1. Individual (cada mensagem separada)")
        print("2. Tela completa")
        print("3. Scroll (captura por partes)")
        print("4. Personalizado")
        print("5. Sair")
        
        while True:
            try:
                choice = input("\n> Escolha uma opção (1-5): ").strip()
                
                if choice == "1":
                    print("\n[INFO] Captura Individual Selecionada")
                    headless = input("Executar em modo headless? (s/N): ").strip().lower() == 's'
                    include_header = input("Incluir captura do header? (S/n): ").strip().lower() != 'n'
                    url = input("URL da aplicação (Enter para padrão): ").strip() or "http://localhost:8089"
                    
                    self.run_capture(mode="individual", headless=headless, include_header=include_header, url=url)
                    break
                    
                elif choice == "2":
                    print("\n[INFO] Captura de Tela Completa Selecionada")
                    headless = input("Executar em modo headless? (s/N): ").strip().lower() == 's'
                    include_header = input("Incluir captura do header? (S/n): ").strip().lower() != 'n'
                    url = input("URL da aplicação (Enter para padrão): ").strip() or "http://localhost:8089"
                    
                    self.run_capture(mode="full", headless=headless, include_header=include_header, url=url)
                    break
                    
                elif choice == "3":
                    print("\n[INFO] Captura por Scroll Selecionada")
                    headless = input("Executar em modo headless? (s/N): ").strip().lower() == 's'
                    include_header = input("Incluir captura do header? (S/n): ").strip().lower() != 'n'
                    url = input("URL da aplicação (Enter para padrão): ").strip() or "http://localhost:8089"
                    
                    print("\n[OPCOES DE SCROLL]")
                    print("1. Múltiplas imagens (uma para cada parte)")
                    print("2. Uma única imagem (toda a conversa)")
                    scroll_choice = input("Escolha (1/2): ").strip()
                    
                    scroll_single_image = (scroll_choice == "2")
                    
                    self.run_capture(mode="scroll", headless=headless, include_header=include_header, url=url, scroll_single_image=scroll_single_image)
                    break
                    
                elif choice == "4":
                    print("\n[INFO] Modo Personalizado")
                    print("Execute manualmente o script com as opções desejadas:")
                    print(f"python {self.main_script} --help")
                    break
                    
                elif choice == "5":
                    print("\n[INFO] Saindo...")
                    break
                    
                else:
                    print("[ERROR] Opção inválida. Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n\n[INFO] Saindo...")
                break
                
    def quick_commands(self):
        """Mostra comandos rápidos disponíveis"""
        print("\n" + "="*60)
        print("COMANDOS RÁPIDOS")
        print("="*60)
        
        print("\n[INDIVIDUAL] CAPTURA INDIVIDUAL (msg por msg):")
        print(f"python {self.main_script} --mode individual --headless --include-header")
        
        print("\n[FULL] CAPTURA TELA COMPLETA:")
        print(f"python {self.main_script} --mode full --headless --include-header")
        
        print("\n[SCROLL] CAPTURA POR SCROLL (múltiplas partes):")
        print(f"python {self.main_script} --mode scroll --headless --include-header")
        
        print("\n[SCROLL] CAPTURA POR SCROLL (imagem única):")
        print(f"python {self.main_script} --mode scroll --headless --include-header --scroll-single-image")
        
        print("\n[CUSTOM] CAPTURA PERSONALIZADA:")
        print(f"python {self.main_script} --mode individual --url http://localhost:8089 --output meu_diretorio --scroll-amount 500 --scroll-delay 2000")
        
        print("\n[HELP] AJUDA COMPLETA:")
        print(f"python {self.main_script} --help")


def main():
    if len(sys.argv) > 1:
        # Modo comando direto
        if sys.argv[1] == "--quick":
            helper = WhatsAppCaptureHelper()
            helper.quick_commands()
        else:
            print("Uso: python run_capture.py [--quick]")
    else:
        # Modo interativo
        helper = WhatsAppCaptureHelper()
        helper.interactive_menu()


if __name__ == "__main__":
    main() 