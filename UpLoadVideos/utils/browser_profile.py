import random
import json
import os
from typing import Dict, List
from fake_useragent import UserAgent

class BrowserProfile:
    """Gerencia perfis de navegador para evitar detecção"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.load_profiles()
    
    def load_profiles(self):
        """Carrega perfis de navegador predefinidos"""
        self.profiles = {
            "windows_chrome": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "platform": "Win32",
                "language": "pt-BR,pt;q=0.9,en;q=0.8",
                "timezone": "America/Sao_Paulo",
                "screen_resolution": "1920x1080",
                "color_depth": 24,
                "webgl_vendor": "Google Inc. (Intel)",
                "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "windows_firefox": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "platform": "Win32",
                "language": "pt-BR,pt;q=0.9,en;q=0.8",
                "timezone": "America/Sao_Paulo",
                "screen_resolution": "1920x1080",
                "color_depth": 24,
                "webgl_vendor": "Mesa/X.org",
                "webgl_renderer": "Mesa DRI Intel(R) UHD Graphics 620 (KBL GT2)"
            },
            "mac_chrome": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "platform": "MacIntel",
                "language": "pt-BR,pt;q=0.9,en;q=0.8",
                "timezone": "America/Sao_Paulo",
                "screen_resolution": "1440x900",
                "color_depth": 24,
                "webgl_vendor": "Apple Inc.",
                "webgl_renderer": "Apple M1 Pro"
            }
        }
    
    def get_random_profile(self) -> Dict:
        """Retorna um perfil aleatório"""
        profile_name = random.choice(list(self.profiles.keys()))
        return self.profiles[profile_name]
    
    def get_specific_profile(self, profile_name: str) -> Dict:
        """Retorna um perfil específico"""
        return self.profiles.get(profile_name, self.profiles["windows_chrome"])
    
    def generate_random_user_agent(self) -> str:
        """Gera um User-Agent aleatório"""
        return self.ua.random
    
    def get_viewport_size(self) -> Dict[str, int]:
        """Retorna tamanho de viewport aleatório"""
        sizes = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720}
        ]
        return random.choice(sizes)
    
    def get_timezone_offset(self) -> int:
        """Retorna offset de timezone para Brasil"""
        return -180  # UTC-3 (horário de Brasília)
    
    def get_language_preferences(self) -> List[str]:
        """Retorna preferências de idioma"""
        return ["pt-BR", "pt", "en-US", "en"] 