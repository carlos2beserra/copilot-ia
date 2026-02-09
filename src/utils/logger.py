# =============================================================================
# Copilot-IA - Sistema de Logging
# =============================================================================
"""
Configuração centralizada de logging para o projeto.
"""

import logging
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Carregar variáveis de ambiente do .env automaticamente
load_dotenv()


# Console para output rico
console = Console()

# Cache de loggers
_loggers: dict[str, logging.Logger] = {}


def setup_logging(
    level: str = "INFO", log_file: str | None = None, json_format: bool = False
) -> None:
    """
    Configura o sistema de logging.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        log_file: Arquivo de log (opcional)
        json_format: Usar formato JSON
    """
    # Nível de log
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Formato
    if json_format:
        format_str = '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    else:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Handler de console com Rich
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(log_level)

    handlers = [console_handler]

    # Handler de arquivo
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(format_str))
        handlers.append(file_handler)

    # Configurar root logger
    logging.basicConfig(
        level=log_level,
        format=format_str,
        handlers=handlers,
    )

    # Silenciar loggers verbosos
    for logger_name in ["httpx", "httpcore", "openai", "anthropic"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado.

    Args:
        name: Nome do logger (geralmente __name__)

    Returns:
        Logger configurado
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Prefixo para identificação
    if name.startswith("src."):
        name_short = name.replace("src.", "copilot.")
    else:
        name_short = name

    _loggers[name] = logger
    return logger


class LoggerMixin:
    """Mixin para adicionar logging a classes."""

    @property
    def logger(self) -> logging.Logger:
        """Retorna logger para a classe."""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger
