#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de automação para captura de mensagens do WhatsApp usando Playwright
Permite capturar mensagens individuais ou tela completa com scroll automático
"""

import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import json
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import os
import sys

# Configurar codificação UTF-8 para Windows
if sys.platform == "win32":
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        pass


class WhatsAppScreenshotAutomation:
    def __init__(self, headless=True, output_dir="screenshots"):
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        
    async def start_browser(self):
        """Inicializa o navegador Playwright"""
        self.playwright = await async_playwright().start()
        
        # Configurações do navegador
        browser_options = {
            "headless": self.headless
        }
        
        # Configurações do contexto
        context_options = {
            "viewport": {"width": 414, "height": 896},  # Tamanho mobile
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "device_scale_factor": 2
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_options)
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Configurar timeout
        self.page.set_default_timeout(30000)
        
        print("[OK] Navegador iniciado com sucesso")
        
    async def navigate_to_app(self, url="http://localhost:8089"):
        """Navega para a aplicação WhatsApp"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            print(f"[OK] Navegou para: {url}")
            
            # Aguardar a aplicação carregar
            await self.page.wait_for_selector(".whatsapp-chat", timeout=10000)
            print("[OK] Aplicação WhatsApp carregada")
            
        except Exception as e:
            print(f"[ERROR] Erro ao navegar para a aplicação: {e}")
            raise
            
    async def capture_header(self, filename="header.png"):
        """Captura apenas o header da tela"""
        try:
            header_element = await self.page.wait_for_selector(".chat-header")
            
            # Obter as dimensões do header
            header_box = await header_element.bounding_box()
            
            # Capturar o header
            screenshot_path = self.output_dir / filename
            await self.page.screenshot(
                path=screenshot_path,
                clip={
                    "x": header_box["x"],
                    "y": header_box["y"],
                    "width": header_box["width"],
                    "height": header_box["height"]
                }
            )
            
            print(f"[OK] Header capturado: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar header: {e}")
            return None
            
    async def get_messages(self):
        """Obtém todas as mensagens da tela"""
        try:
            # Aguardar mensagens carregarem
            await self.page.wait_for_selector(".message-wrapper", timeout=10000)
            
            # Buscar todas as mensagens
            messages = await self.page.query_selector_all(".message-wrapper")
            print(f"[OK] Encontradas {len(messages)} mensagens")
            
            return messages
            
        except Exception as e:
            print(f"[ERROR] Erro ao obter mensagens: {e}")
            return []
            
    async def capture_individual_message(self, message_element, index, filename_prefix="message"):
        """Captura uma mensagem individual"""
        try:
            # Garantir que a mensagem esteja visível
            await message_element.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(500)  # Aguardar animação
            
            # Obter as dimensões da mensagem
            message_box = await message_element.bounding_box()
            
            if message_box:
                # Nome do arquivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename_prefix}_{index:03d}_{timestamp}.png"
                screenshot_path = self.output_dir / filename
                
                # Capturar a mensagem
                await message_element.screenshot(path=screenshot_path)
                
                print(f"[OK] Mensagem {index} capturada: {screenshot_path}")
                return screenshot_path
            else:
                print(f"[ERROR] Não foi possível obter dimensões da mensagem {index}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Erro ao capturar mensagem {index}: {e}")
            return None
            
    async def capture_full_screen(self, filename="full_screen.png"):
        """Captura tela completa com scroll automático"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"full_screen_{timestamp}.png"
            screenshot_path = self.output_dir / filename
            
            # Verificar se o container de mensagens existe
            messages_container = await self.page.query_selector(".messages-container")
            if not messages_container:
                print("[ERROR] Container de mensagens não encontrado")
                return None
            
            print("[INFO] Fazendo scroll completo para capturar todas as mensagens...")
            
            # Primeiro, ir para o topo
            await self.page.evaluate("""
                const container = document.querySelector('.messages-container');
                if (container) {
                    container.scrollTop = 0;
                }
            """)
            await self.page.wait_for_timeout(500)
            
            # Fazer scroll completo para baixo, garantindo que tudo seja carregado
            scroll_step = 300
            previous_scroll = 0
            max_attempts = 100
            
            for attempt in range(max_attempts):
                # Fazer scroll
                await self.page.evaluate(f"""
                    const container = document.querySelector('.messages-container');
                    if (container) {{
                        container.scrollTop += {scroll_step};
                    }}
                """)
                await self.page.wait_for_timeout(100)  # Delay menor para ser mais rápido
                
                # Verificar posição atual
                current_scroll = await self.page.evaluate("""
                    const container = document.querySelector('.messages-container');
                    return container ? container.scrollTop : 0;
                """)
                
                # Se não mudou, chegou ao final
                if current_scroll == previous_scroll:
                    print(f"[INFO] Scroll completo após {attempt + 1} tentativas")
                    break
                    
                previous_scroll = current_scroll
            
            # Aguardar um pouco para garantir que tudo carregou
            await self.page.wait_for_timeout(1000)
            
            # Agora voltar para o topo
            await self.page.evaluate("""
                const container = document.querySelector('.messages-container');
                if (container) {
                    container.scrollTop = 0;
                }
            """)
            await self.page.wait_for_timeout(500)
            
            # Capturar tela completa - agora com todo o conteúdo carregado
            await self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"[OK] Tela completa capturada: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"[ERROR] Erro ao capturar tela completa: {e}")
            return None
            
    async def scroll_and_capture(self, scroll_amount=300, delay=1000, capture_parts=True):
        """Scroll da tela e captura por partes ou uma única imagem"""
        try:
            screenshots = []
            
            # Focar no container de mensagens
            messages_container = await self.page.query_selector(".messages-container")
            if not messages_container:
                print("[ERROR] Container de mensagens não encontrado")
                return []
            
            print("[INFO] Fazendo scroll completo das mensagens...")
            
            # Scroll para o topo primeiro
            await self.page.evaluate("""
                const container = document.querySelector('.messages-container');
                if (container) {
                    container.scrollTop = 0;
                }
            """)
            await self.page.wait_for_timeout(500)
            
            if capture_parts:
                # Modo: capturar múltiplas partes
                part_counter = 1
                
                # Capturar primeira parte
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screen_part_{part_counter:03d}_{timestamp}.png"
                screenshot_path = self.output_dir / filename
                await self.page.screenshot(path=screenshot_path)
                screenshots.append(screenshot_path)
                print(f"[OK] Parte {part_counter} capturada: {screenshot_path}")
                
                # Scroll e capturar demais partes
                previous_scroll = 0
                max_attempts = 50
                
                for attempt in range(max_attempts):
                    # Fazer scroll no container de mensagens
                    await self.page.evaluate(f"""
                        const container = document.querySelector('.messages-container');
                        if (container) {{
                            container.scrollTop += {scroll_amount};
                        }}
                    """)
                    await self.page.wait_for_timeout(delay)
                    
                    # Verificar posição atual do scroll
                    current_scroll = await self.page.evaluate("""
                        const container = document.querySelector('.messages-container');
                        return container ? container.scrollTop : 0;
                    """)
                    
                    # Se não houve mudança no scroll, chegou ao final
                    if current_scroll == previous_scroll:
                        print(f"[INFO] Chegou ao final das mensagens após {attempt + 1} tentativas")
                        break
                        
                    previous_scroll = current_scroll
                    part_counter += 1
                    
                    # Capturar nova parte
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screen_part_{part_counter:03d}_{timestamp}.png"
                    screenshot_path = self.output_dir / filename
                    await self.page.screenshot(path=screenshot_path)
                    screenshots.append(screenshot_path)
                    print(f"[OK] Parte {part_counter} capturada: {screenshot_path}")
                    
                print(f"[OK] Captura por scroll concluída: {len(screenshots)} partes")
                
            else:
                # Modo: fazer scroll completo e capturar uma única imagem
                return await self.capture_full_screen("scrolled_full_screen.png")
                
            return screenshots
            
        except Exception as e:
            print(f"[ERROR] Erro no scroll e captura: {e}")
            return []
            
    async def capture_messages_individually(self):
        """Captura todas as mensagens individualmente"""
        try:
            messages = await self.get_messages()
            if not messages:
                print("[ERROR] Nenhuma mensagem encontrada")
                return []
                
            screenshots = []
            
            for i, message in enumerate(messages):
                screenshot_path = await self.capture_individual_message(message, i + 1)
                if screenshot_path:
                    screenshots.append(screenshot_path)
                    
                # Pequeno delay entre capturas
                await self.page.wait_for_timeout(300)
                
            print(f"[OK] Captura individual concluída: {len(screenshots)} mensagens")
            return screenshots
            
        except Exception as e:
            print(f"[ERROR] Erro na captura individual: {e}")
            return []
            
    async def generate_report(self, screenshots):
        """Gera relatório JSON com informações das capturas"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_screenshots": len(screenshots),
                "output_directory": str(self.output_dir),
                "screenshots": []
            }
            
            for screenshot in screenshots:
                file_info = {
                    "filename": screenshot.name,
                    "path": str(screenshot),
                    "size": screenshot.stat().st_size if screenshot.exists() else 0,
                    "created": datetime.fromtimestamp(screenshot.stat().st_ctime).isoformat() if screenshot.exists() else None
                }
                report["screenshots"].append(file_info)
                
            # Salvar relatório
            report_path = self.output_dir / "capture_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            print(f"[OK] Relatório gerado: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"[ERROR] Erro ao gerar relatório: {e}")
            return None
            
    async def close(self):
        """Fecha o navegador"""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            print("[OK] Navegador fechado")


async def main():
    parser = argparse.ArgumentParser(description="Automação de captura de mensagens WhatsApp")
    parser.add_argument("--mode", choices=["individual", "full", "scroll"], default="individual",
                       help="Modo de captura: individual (msg por msg), full (tela completa), scroll (por partes)")
    parser.add_argument("--url", default="http://localhost:8089", help="URL da aplicação")
    parser.add_argument("--output", default="screenshots", help="Diretório de saída")
    parser.add_argument("--headless", action="store_true", help="Executar em modo headless")
    parser.add_argument("--include-header", action="store_true", help="Incluir captura do header")
    parser.add_argument("--scroll-amount", type=int, default=300, help="Quantidade de scroll (pixels)")
    parser.add_argument("--scroll-delay", type=int, default=1000, help="Delay entre scrolls (ms)")
    parser.add_argument("--scroll-single-image", action="store_true", help="Capturar uma única imagem no modo scroll")
    
    args = parser.parse_args()
    
    # Criar instância da automação
    automation = WhatsAppScreenshotAutomation(
        headless=args.headless,
        output_dir=args.output
    )
    
    try:
        print("[INFO] Iniciando automação de captura...")
        
        # Inicializar browser
        await automation.start_browser()
        
        # Navegar para aplicação
        await automation.navigate_to_app(args.url)
        
        screenshots = []
        
        # Capturar header se solicitado
        if args.include_header:
            header_screenshot = await automation.capture_header()
            if header_screenshot:
                screenshots.append(header_screenshot)
                
        # Executar captura baseada no modo
        if args.mode == "individual":
            print("[INFO] Iniciando captura individual das mensagens...")
            msg_screenshots = await automation.capture_messages_individually()
            screenshots.extend(msg_screenshots)
            
        elif args.mode == "full":
            print("[INFO] Iniciando captura de tela completa...")
            full_screenshot = await automation.capture_full_screen()
            if full_screenshot:
                screenshots.append(full_screenshot)
                
        elif args.mode == "scroll":
            if args.scroll_single_image:
                print("[INFO] Iniciando captura por scroll (imagem única)...")
                scroll_screenshot = await automation.scroll_and_capture(
                    scroll_amount=args.scroll_amount,
                    delay=args.scroll_delay,
                    capture_parts=False
                )
                if scroll_screenshot:
                    screenshots.append(scroll_screenshot)
            else:
                print("[INFO] Iniciando captura por scroll (múltiplas partes)...")
                scroll_screenshots = await automation.scroll_and_capture(
                    scroll_amount=args.scroll_amount,
                    delay=args.scroll_delay,
                    capture_parts=True
                )
                screenshots.extend(scroll_screenshots)
            
        # Gerar relatório
        await automation.generate_report(screenshots)
        
        print(f"\n[SUCCESS] Automação concluída com sucesso!")
        print(f"[INFO] Total de capturas: {len(screenshots)}")
        print(f"[INFO] Diretório de saída: {args.output}")
        
    except Exception as e:
        print(f"[ERROR] Erro durante a execução: {e}")
        
    finally:
        # Fechar browser
        await automation.close()


if __name__ == "__main__":
    asyncio.run(main()) 