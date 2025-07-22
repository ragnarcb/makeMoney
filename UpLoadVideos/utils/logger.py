import sys
from loguru import logger
from config import Config

class AutomationLogger:
    """Sistema de logging personalizado para automação"""
    
    def __init__(self):
        self.setup_logger()
    
    def setup_logger(self):
        """Configura o sistema de logging"""
        # Remove handlers padrão
        logger.remove()
        
        # Adiciona handler para console
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=Config.LOG_LEVEL,
            colorize=True
        )
        
        # Adiciona handler para arquivo
        logger.add(
            Config.LOG_FILE,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=Config.LOG_LEVEL,
            rotation="10 MB",
            retention="7 days"
        )
    
    def info(self, message: str):
        """Log de informação"""
        logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        logger.warning(message)
    
    def error(self, message: str):
        """Log de erro"""
        logger.error(message)
    
    def debug(self, message: str):
        """Log de debug"""
        logger.debug(message)
    
    def success(self, message: str):
        """Log de sucesso"""
        logger.success(message)

# Instância global do logger
automation_logger = AutomationLogger() 