import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas para a automação"""
    
    # URLs
    TIKTOK_URL = "https://www.tiktok.com"
    
    # Configurações do navegador
    BROWSER_TYPE = "firefox"  # chromium, firefox, webkit
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"  # True para executar sem interface gráfica
    SLOW_MO = 1000  # Delay entre ações em ms
    
    # Configurações de cookies
    COOKIES_FILE = "cookies.json"
    SAVE_COOKIES = True
    LOAD_COOKIES = True
    
    # Configurações de viewport
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Configurações de timeout
    NAVIGATION_TIMEOUT = 30000  # 30 segundos
    ELEMENT_TIMEOUT = 10000     # 10 segundos
    
    # Configurações de proxy (opcional)
    USE_PROXY = False
    PROXY_SERVER = os.getenv("PROXY_SERVER", "")
    PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
    PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")
    
    # Configurações de logs
    LOG_LEVEL = "INFO"
    LOG_FILE = "automation.log" 