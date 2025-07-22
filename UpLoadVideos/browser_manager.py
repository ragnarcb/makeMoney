import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, List
import random
import time

from config import Config
from utils.browser_profile import BrowserProfile
from utils.logger import automation_logger
from utils.cookie_manager import CookieManager

class BrowserManager:
    """Gerencia o navegador e contexto para automação"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.browser_profile = BrowserProfile()
        self.cookie_manager = CookieManager()
        self.logger = automation_logger
    
    async def start_browser(self, profile_name: str = None) -> bool:
        """Inicia o navegador com configurações anti-detecção"""
        try:
            self.logger.info("Iniciando navegador...")
            
            # Inicia o Playwright
            self.playwright = await async_playwright().start()
            
            # Seleciona perfil
            if profile_name:
                profile = self.browser_profile.get_specific_profile(profile_name)
            else:
                profile = self.browser_profile.get_random_profile()
            
            # Configurações do navegador - anti-fingerprint avançado
            browser_args = [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--mute-audio",
                "--no-zygote",
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-default-apps",
                "--disable-domain-reliability",
                "--disable-extensions",
                "--disable-features=AudioServiceOutOfProcess",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--no-first-run",
                "--password-store=basic",
                "--use-mock-keychain",
                "--disable-blink-features",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-default-apps",
                "--disable-domain-reliability",
                "--disable-extensions",
                "--disable-features=AudioServiceOutOfProcess",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--no-first-run",
                "--password-store=basic",
                "--use-mock-keychain"
            ]
            
            # Configurações do contexto
            context_options = {
                "viewport": self.browser_profile.get_viewport_size(),
                "user_agent": profile["user_agent"],
                "locale": "pt-BR",
                "timezone_id": profile["timezone"],
                "permissions": ["geolocation"],
                "extra_http_headers": {
                    "Accept-Language": profile["language"],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            }
            
            # Adiciona proxy se configurado
            if Config.USE_PROXY and Config.PROXY_SERVER:
                context_options["proxy"] = {
                    "server": Config.PROXY_SERVER,
                    "username": Config.PROXY_USERNAME,
                    "password": Config.PROXY_PASSWORD
                }
            
            # Inicia o navegador
            if Config.BROWSER_TYPE == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=Config.HEADLESS,
                    slow_mo=Config.SLOW_MO,
                    args=browser_args
                )
            elif Config.BROWSER_TYPE == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=Config.HEADLESS,
                    slow_mo=Config.SLOW_MO
                )
            else:
                self.browser = await self.playwright.webkit.launch(
                    headless=Config.HEADLESS,
                    slow_mo=Config.SLOW_MO
                )
            
            # Cria contexto
            self.context = await self.browser.new_context(**context_options)
            
            # Cria página
            self.page = await self.context.new_page()
            
            # Configura timeouts
            self.page.set_default_timeout(Config.NAVIGATION_TIMEOUT)
            self.page.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
            
            # Carrega cookies se configurado
            if Config.LOAD_COOKIES:
                await self.cookie_manager.load_cookies(self.context)
            
            # Injeta scripts para evitar detecção
            await self._inject_stealth_scripts()
            
            self.logger.success("Navegador iniciado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar navegador: {str(e)}")
            return False
    
    async def _inject_stealth_scripts(self):
        """Injeta scripts para evitar detecção de automação"""
        try:
            # Remove propriedades que indicam automação
            await self.page.add_init_script("""
                // Remove propriedades de automação
                delete navigator.__proto__.webdriver;
                delete window.navigator.webdriver;
                
                // Modifica userAgent para parecer mais natural
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Simula plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Simula languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en'],
                });
                
                // Simula hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                // Simula device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
            """)
            
            self.logger.debug("Scripts de stealth injetados com sucesso")
            
        except Exception as e:
            self.logger.warning(f"Erro ao injetar scripts de stealth: {str(e)}")
    
    async def navigate_to_tiktok(self) -> bool:
        """Navega para o TikTok"""
        try:
            self.logger.info("Navegando para o TikTok...")
            
            # Adiciona delay aleatório para parecer mais humano
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navega para o TikTok
            await self.page.goto(Config.TIKTOK_URL, wait_until="networkidle")
            
            # Aguarda carregamento da página
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Simula comportamento humano
            await self._simulate_human_behavior()
            
            self.logger.success("Navegação para TikTok concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao navegar para TikTok: {str(e)}")
            return False
    
    async def _simulate_human_behavior(self):
        """Simula comportamento humano na página"""
        try:
            # Scroll aleatório
            for _ in range(random.randint(2, 5)):
                await self.page.mouse.wheel(0, random.randint(100, 500))
                await asyncio.sleep(random.uniform(0.5, 2))
            
            # Move o mouse aleatoriamente
            await self.page.mouse.move(
                random.randint(100, 800),
                random.randint(100, 600)
            )
            
            self.logger.debug("Comportamento humano simulado")
            
        except Exception as e:
            self.logger.warning(f"Erro ao simular comportamento humano: {str(e)}")
    
    async def close_browser(self):
        """Fecha o navegador"""
        try:
            # SEMPRE salva cookies antes de fechar
            if self.context:
                await self.save_cookies_before_close()
            
            # Fecha página
            if self.page:
                await self.page.close()
            
            # Fecha contexto
            if self.context:
                await self.context.close()
            
            # Fecha navegador
            if self.browser:
                await self.browser.close()
            
            # Para o Playwright
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("Navegador fechado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar navegador: {str(e)}")
            # Tenta salvar cookies mesmo em caso de erro
            try:
                if self.context:
                    await self.save_cookies_before_close()
            except:
                pass
    
    async def take_screenshot(self, filename: str = None) -> str:
        """Tira screenshot da página atual"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            await self.page.screenshot(path=filename, full_page=True)
            self.logger.info(f"Screenshot salvo: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro ao tirar screenshot: {str(e)}")
            return ""
    
    # ===== MÉTODOS DE GERENCIAMENTO DE COOKIES =====
    
    async def save_cookies(self, domain: str = None) -> bool:
        """Salva cookies do contexto atual"""
        if not self.context:
            self.logger.error("Contexto não disponível")
            return False
        return await self.cookie_manager.save_cookies(self.context, domain)
    
    async def load_cookies(self) -> bool:
        """Carrega cookies salvos no contexto"""
        if not self.context:
            self.logger.error("Contexto não disponível")
            return False
        return await self.cookie_manager.load_cookies(self.context)
    
    async def extract_cookies_from_page(self, domain: str = None) -> List[Dict]:
        """Extrai cookies da página atual"""
        if not self.page:
            self.logger.error("Página não disponível")
            return []
        return await self.cookie_manager.extract_cookies_from_page(self.page, domain)
    
    async def clear_cookies(self) -> bool:
        """Limpa todos os cookies do contexto"""
        if not self.context:
            self.logger.error("Contexto não disponível")
            return False
        return await self.cookie_manager.clear_cookies(self.context)
    
    def get_cookies_info(self) -> Dict:
        """Obtém informações sobre cookies salvos"""
        return self.cookie_manager.get_cookies_info()
    
    def delete_cookies_file(self) -> bool:
        """Deleta o arquivo de cookies"""
        return self.cookie_manager.delete_cookies_file()
    
    def validate_cookies(self, cookies: List[Dict]) -> Dict:
        """Valida cookies e retorna informações de qualidade"""
        return self.cookie_manager.validate_cookies(cookies)
    
    async def save_cookies_before_close(self):
        """Salva cookies antes de fechar o navegador"""
        try:
            if Config.SAVE_COOKIES and self.context:
                self.logger.info("Salvando cookies antes de fechar...")
                
                # Salva cookies do TikTok
                await self.save_cookies("tiktok.com")
                
                # Salva cookies de domínios relacionados
                await self.save_cookies("tiktokv.com")
                await self.save_cookies("musical.ly")
                
                # Salva todos os cookies como backup
                await self.save_cookies()
                
                self.logger.success("Cookies salvos com sucesso!")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao salvar cookies: {str(e)}")
            return False 