#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a automação de captura WhatsApp
"""

import sys
import subprocess
import importlib.util
from pathlib import Path
import urllib.request
import socket

# Configurar codificação UTF-8 para Windows
if sys.platform == "win32":
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        pass

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        return False, f"Python {version.major}.{version.minor} (requer 3.7+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_package_installed(package_name):
    """Verifica se um pacote Python está instalado"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ImportError:
        return False

def check_url_accessible(url, timeout=5):
    """Verifica se uma URL está acessível"""
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except:
        return False

def check_port_open(host, port, timeout=3):
    """Verifica se uma porta está aberta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def run_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTE DE AUTOMACAO WHATSAPP")
    print("=" * 60)
    print()
    
    # Teste 1: Versão do Python
    print("[1] Verificando versão do Python...")
    python_ok, python_version = check_python_version()
    if python_ok:
        print(f"    [OK] {python_version}")
    else:
        print(f"    [ERROR] {python_version}")
        return False
    
    # Teste 2: Arquivos necessários
    print("\n[2] Verificando arquivos necessários...")
    required_files = [
        "whatsapp_screenshot_automation.py",
        "run_capture.py",
        "requirements.txt"
    ]
    
    all_files_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"    [OK] {file}")
        else:
            print(f"    [ERROR] {file} não encontrado")
            all_files_ok = False
    
    if not all_files_ok:
        return False
    
    # Teste 3: Dependências Python
    print("\n[3] Verificando dependências Python...")
    required_packages = ["playwright", "asyncio", "argparse", "pathlib", "json"]
    
    for package in required_packages:
        if check_package_installed(package):
            print(f"    [OK] {package}")
        else:
            print(f"    [WARNING] {package} não instalado (será instalado automaticamente)")
    
    # Teste 4: Conectividade com aplicação
    print("\n[4] Verificando conectividade com aplicação...")
    url = "http://localhost:8089"
    if check_url_accessible(url):
        print(f"    [OK] {url} acessível")
    else:
        print(f"    [WARNING] {url} não acessível")
        print(f"    [INFO] Certifique-se de que o WhatsApp Clone está rodando")
        
        # Verificar se a porta está aberta
        if check_port_open("localhost", 8089):
            print(f"    [INFO] Porta 8089 está aberta")
        else:
            print(f"    [INFO] Porta 8089 não está aberta")
    
    # Teste 5: Teste de execução básica
    print("\n[5] Testando execução básica...")
    try:
        # Testar ajuda do script principal
        result = subprocess.run([
            sys.executable, 
            "whatsapp_screenshot_automation.py", 
            "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("    [OK] Script principal executável")
        else:
            print("    [ERROR] Erro ao executar script principal")
            print(f"    [INFO] Erro: {result.stderr}")
            
    except Exception as e:
        print(f"    [ERROR] Erro ao testar execução: {e}")
    
    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES")
    print("=" * 60)
    
    # Resumo
    print("\n[RESUMO]")
    print("- Se todos os testes passaram: Execute 'python run_capture.py'")
    print("- Se há warnings sobre dependências: Elas serão instaladas automaticamente")
    print("- Se a URL não está acessível: Inicie o WhatsApp Clone primeiro")
    print("- Para iniciar o WhatsApp Clone: 'cd front/whatsapp-clone && npm start'")
    
    print("\n[COMANDOS RAPIDOS]")
    print("- Teste interativo: python run_capture.py")
    print("- Ajuda completa: python whatsapp_screenshot_automation.py --help")
    print("- Modo Windows: duplo clique em run_capture.bat")
    
    return True

def main():
    """Função principal"""
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\n[INFO] Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n[ERROR] Erro durante os testes: {e}")

if __name__ == "__main__":
    main() 