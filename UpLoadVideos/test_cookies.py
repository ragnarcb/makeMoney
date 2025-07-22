#!/usr/bin/env python3
"""
Script de teste para funcionalidades de cookies
"""

import asyncio
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_manager import BrowserManager
from utils.logger import automation_logger
from config import Config

class CookieTest:
    """Teste de funcionalidades de cookies"""
    
    def __init__(self):
        self.browser_manager = BrowserManager()
        self.logger = automation_logger
    
    async def test_cookie_management(self):
        """Testa gerenciamento de cookies"""
        try:
            self.logger.info("=== TESTE DE GERENCIAMENTO DE COOKIES ===")
            
            # 1. Inicia navegador
            success = await self.browser_manager.start_browser()
            if not success:
                self.logger.error("Falha ao iniciar navegador")
                return False
            
            # 2. Navega para TikTok
            success = await self.browser_manager.navigate_to_tiktok()
            if not success:
                self.logger.error("Falha ao navegar para TikTok")
                return False
            
            # 3. Aguarda carregamento
            await asyncio.sleep(5)
            
            # 4. Testa extração de cookies
            self.logger.info("Testando extração de cookies...")
            cookies = await self.browser_manager.extract_cookies_from_page("tiktok.com")
            
            if cookies:
                self.logger.success(f"✅ {len(cookies)} cookies extraídos")
                
                # Valida cookies
                validation = self.browser_manager.validate_cookies(cookies)
                self.logger.info(f"📊 Qualidade dos cookies: {validation['quality_score']}/100")
                self.logger.info(f"🔒 Cookies seguros: {validation['secure_cookies']}")
                self.logger.info(f"🍪 Cookies importantes: {validation['important_cookies']}")
                
                # Salva cookies
                success = await self.browser_manager.save_cookies("tiktok.com")
                if success:
                    self.logger.success("✅ Cookies salvos com sucesso")
                else:
                    self.logger.error("❌ Falha ao salvar cookies")
            else:
                self.logger.warning("⚠️ Nenhum cookie extraído")
            
            # 5. Testa informações de cookies
            cookies_info = self.browser_manager.get_cookies_info()
            if cookies_info.get("exists"):
                self.logger.info(f"📁 Arquivo de cookies: {cookies_info['file_size']} bytes")
                self.logger.info(f"⏰ Idade dos cookies: {cookies_info['age_hours']:.1f} horas")
            
            # 6. Aguarda um pouco
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no teste: {str(e)}")
            return False
        
        finally:
            await self.browser_manager.close_browser()
    
    async def test_cookie_reload(self):
        """Testa recarregamento de cookies"""
        try:
            self.logger.info("=== TESTE DE RECARREGAMENTO DE COOKIES ===")
            
            # 1. Inicia navegador
            success = await self.browser_manager.start_browser()
            if not success:
                return False
            
            # 2. Carrega cookies salvos
            success = await self.browser_manager.load_cookies()
            if success:
                self.logger.success("✅ Cookies carregados com sucesso")
            else:
                self.logger.warning("⚠️ Nenhum cookie para carregar")
            
            # 3. Navega para TikTok
            success = await self.browser_manager.navigate_to_tiktok()
            if not success:
                return False
            
            # 4. Verifica se os cookies foram aplicados
            await asyncio.sleep(3)
            cookies = await self.browser_manager.extract_cookies_from_page("tiktok.com")
            
            if cookies:
                self.logger.success(f"✅ {len(cookies)} cookies ativos após carregamento")
            else:
                self.logger.warning("⚠️ Nenhum cookie ativo")
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no teste de recarregamento: {str(e)}")
            return False
        
        finally:
            await self.browser_manager.close_browser()

async def main():
    """Função principal"""
    test = CookieTest()
    
    # Testa gerenciamento de cookies
    success1 = await test.test_cookie_management()
    
    # Aguarda um pouco entre testes
    await asyncio.sleep(2)
    
    # Testa recarregamento de cookies
    success2 = await test.test_cookie_reload()
    
    if success1 and success2:
        test.logger.success("🎉 Todos os testes de cookies passaram!")
        sys.exit(0)
    else:
        test.logger.error("❌ Alguns testes falharam")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 