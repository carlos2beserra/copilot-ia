# =============================================================================
# Copilot-IA - Módulo de Copilotos Especializados
# =============================================================================
"""
Copilotos especializados para diferentes tarefas de desenvolvimento.

Cada copiloto é um agente de IA focado em uma área específica:
- CodeReviewerCopilot: Revisão e análise de código
- DocumentationCopilot: Geração de documentação
- TestingCopilot: Criação de testes
- DebugCopilot: Assistência em depuração
- RefactoringCopilot: Refatoração de código
- ArchitectureCopilot: Consultoria arquitetural
- SecurityCopilot: Análise de segurança
"""

from src.copilots.architecture import ArchitectureCopilot
from src.copilots.code_reviewer import CodeReviewerCopilot
from src.copilots.debug import DebugCopilot
from src.copilots.documentation import DocumentationCopilot
from src.copilots.refactoring import RefactoringCopilot
from src.copilots.security import SecurityCopilot
from src.copilots.testing import TestingCopilot

__all__ = [
    "CodeReviewerCopilot",
    "DocumentationCopilot",
    "TestingCopilot",
    "DebugCopilot",
    "RefactoringCopilot",
    "ArchitectureCopilot",
    "SecurityCopilot",
]
