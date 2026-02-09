# =============================================================================
# Copilot-IA - Módulo de Agentes
# =============================================================================
"""
Módulo contendo os agentes base e o coordenador multiagente.
"""

from src.agents.base import BaseCopilotAgent
from src.agents.coordinator import CopilotCoordinator

__all__ = [
    "BaseCopilotAgent",
    "CopilotCoordinator",
]
