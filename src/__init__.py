# =============================================================================
# Copilot-IA - Módulo Principal
# =============================================================================
"""
Copilot-IA: Plataforma de Copilotos de Desenvolvimento Inteligentes

Este pacote fornece uma coleção de agentes de IA especializados para auxiliar
no desenvolvimento de software, incluindo:

- Code Reviewer: Revisão e análise de código
- Documentation: Geração de documentação
- Testing: Criação de testes automatizados
- Debug: Assistência em depuração
- Refactoring: Refatoração de código
- Architecture: Consultoria arquitetural
- Security: Análise de segurança

Uso básico:
    from src.copilots import CodeReviewerCopilot

    reviewer = CodeReviewerCopilot()
    resultado = reviewer.analyze("caminho/para/arquivo.py")
"""

__version__ = "0.1.0"
__author__ = "Copilot-IA Team"

from src.agents import CopilotCoordinator
from src.copilots import (
    ArchitectureCopilot,
    CodeReviewerCopilot,
    DebugCopilot,
    DocumentationCopilot,
    RefactoringCopilot,
    SecurityCopilot,
    TestingCopilot,
)

__all__ = [
    "CodeReviewerCopilot",
    "DocumentationCopilot",
    "TestingCopilot",
    "DebugCopilot",
    "RefactoringCopilot",
    "ArchitectureCopilot",
    "SecurityCopilot",
    "CopilotCoordinator",
]
