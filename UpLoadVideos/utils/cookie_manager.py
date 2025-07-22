import json
import os
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from playwright.async_api import Page, BrowserContext

from config import Config
from utils.logger import automation_logger

class CookieManager:
    """Gerencia cookies para automação"""
    
    def __init__(self):
        self.logger = automation_logger
        self.cookies_file = Config.COOKIES_FILE
    
    async def save_cookies(self, context: BrowserContext, domain: str = None) -> bool:
        """Salva cookies do contexto atual"""
        try:
            self.logger.info("Salvando cookies...")
            
            # Obtém cookies do contexto
            cookies = await context.cookies()
            
            if not cookies:
                self.logger.warning("Nenhum cookie encontrado para salvar")
                return False
            
            # Filtra cookies por domínio se especificado
            if domain:
                cookies = [cookie for cookie in cookies if domain in cookie.get('domain', '')]
            
            # Adiciona metadados
            cookie_data = {
                "timestamp": datetime.now().isoformat(),
                "domain": domain or "all",
                "cookies": cookies,
                "total_cookies": len(cookies)
            }
            
            # Salva em arquivo JSON
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            self.logger.success(f"Cookies salvos: {len(cookies)} cookies em {self.cookies_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar cookies: {str(e)}")
            return False
    
    async def load_cookies(self, context: BrowserContext) -> bool:
        """Carrega cookies salvos no contexto"""
        try:
            if not os.path.exists(self.cookies_file):
                self.logger.warning(f"Arquivo de cookies não encontrado: {self.cookies_file}")
                return False
            
            self.logger.info("Carregando cookies...")
            
            # Carrega cookies do arquivo
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get('cookies', [])
            
            if not cookies:
                self.logger.warning("Nenhum cookie encontrado no arquivo")
                return False
            
            # Aplica cookies ao contexto
            await context.add_cookies(cookies)
            
            self.logger.success(f"Cookies carregados: {len(cookies)} cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar cookies: {str(e)}")
            return False
    
    def get_cookies_info(self) -> Dict:
        """Obtém informações sobre cookies salvos"""
        try:
            if not os.path.exists(self.cookies_file):
                return {"exists": False, "message": "Arquivo não encontrado"}
            
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            timestamp = cookie_data.get('timestamp', '')
            total_cookies = cookie_data.get('total_cookies', 0)
            domain = cookie_data.get('domain', 'all')
            
            # Calcula idade dos cookies
            if timestamp:
                cookie_time = datetime.fromisoformat(timestamp)
                age = datetime.now() - cookie_time
                age_hours = age.total_seconds() / 3600
            else:
                age_hours = 0
            
            return {
                "exists": True,
                "timestamp": timestamp,
                "age_hours": age_hours,
                "total_cookies": total_cookies,
                "domain": domain,
                "file_size": os.path.getsize(self.cookies_file)
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    async def extract_cookies_from_page(self, page: Page, domain: str = None) -> List[Dict]:
        """Extrai cookies diretamente da página atual"""
        try:
            self.logger.info("Extraindo cookies da página...")
            
            # Executa JavaScript para obter cookies
            cookies_js = await page.evaluate("""
                () => {
                    return document.cookie.split(';').map(cookie => {
                        const [name, value] = cookie.trim().split('=');
                        return { name, value };
                    }).filter(cookie => cookie.name && cookie.value);
                }
            """)
            
            # Obtém cookies via Playwright também
            playwright_cookies = await page.context.cookies()
            
            # Combina e filtra cookies
            all_cookies = []
            
            # Adiciona cookies do JavaScript
            for cookie in cookies_js:
                all_cookies.append({
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": page.url,
                    "path": "/"
                })
            
            # Adiciona cookies do Playwright
            for cookie in playwright_cookies:
                if domain is None or domain in cookie.get('domain', ''):
                    all_cookies.append(cookie)
            
            # Remove duplicatas
            unique_cookies = []
            seen_names = set()
            
            for cookie in all_cookies:
                name = cookie.get('name', '')
                if name and name not in seen_names:
                    unique_cookies.append(cookie)
                    seen_names.add(name)
            
            self.logger.success(f"Cookies extraídos: {len(unique_cookies)} cookies únicos")
            return unique_cookies
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair cookies: {str(e)}")
            return []
    
    async def clear_cookies(self, context: BrowserContext) -> bool:
        """Limpa todos os cookies do contexto"""
        try:
            self.logger.info("Limpando cookies...")
            await context.clear_cookies()
            self.logger.success("Cookies limpos com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cookies: {str(e)}")
            return False
    
    def delete_cookies_file(self) -> bool:
        """Deleta o arquivo de cookies"""
        try:
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
                self.logger.success(f"Arquivo de cookies deletado: {self.cookies_file}")
                return True
            else:
                self.logger.warning("Arquivo de cookies não existe")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao deletar arquivo de cookies: {str(e)}")
            return False
    
    def validate_cookies(self, cookies: List[Dict]) -> Dict:
        """Valida cookies e retorna informações de qualidade"""
        try:
            if not cookies:
                return {"valid": False, "message": "Nenhum cookie fornecido"}
            
            # Conta tipos de cookies
            session_cookies = 0
            persistent_cookies = 0
            secure_cookies = 0
            http_only_cookies = 0
            
            for cookie in cookies:
                if cookie.get('httpOnly'):
                    http_only_cookies += 1
                if cookie.get('secure'):
                    secure_cookies += 1
                if cookie.get('expires'):
                    persistent_cookies += 1
                else:
                    session_cookies += 1
            
            # Verifica cookies importantes
            important_cookies = ['session', 'auth', 'token', 'csrf', 'login']
            found_important = []
            
            for cookie in cookies:
                name = cookie.get('name', '').lower()
                for important in important_cookies:
                    if important in name:
                        found_important.append(name)
                        break
            
            return {
                "valid": True,
                "total_cookies": len(cookies),
                "session_cookies": session_cookies,
                "persistent_cookies": persistent_cookies,
                "secure_cookies": secure_cookies,
                "http_only_cookies": http_only_cookies,
                "important_cookies": found_important,
                "quality_score": min(100, len(found_important) * 20 + len(cookies) * 2)
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)} 