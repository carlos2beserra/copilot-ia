# =============================================================================
# Copilot-IA - Módulo de Configuração
# =============================================================================
"""
Módulo de configuração do Copilot-IA.

Este módulo fornece acesso centralizado às configurações do sistema,
incluindo configurações de agentes, prompts e logging.
"""

from pathlib import Path

# Diretório base de configurações
CONFIG_DIR = Path(__file__).parent

# Arquivos de configuração
AGENTS_CONFIG = CONFIG_DIR / "agents_config.yaml"
PROMPTS_CONFIG = CONFIG_DIR / "prompts_config.yaml"
LOGGING_CONFIG = CONFIG_DIR / "logging_config.yaml"

__all__ = [
    "CONFIG_DIR",
    "AGENTS_CONFIG",
    "PROMPTS_CONFIG",
    "LOGGING_CONFIG",
]

