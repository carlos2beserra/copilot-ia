# =============================================================================
# Copilot-IA - Módulo de Ferramentas
# =============================================================================
"""
Ferramentas disponíveis para os agentes/copilotos.

As ferramentas permitem que os agentes executem ações concretas como:
- Análise de código (AST, métricas)
- Operações de arquivo
- Integração com Git
- Busca semântica
"""

from src.tools.code_analysis import CodeAnalysisTool
from src.tools.file_operations import FileOperationsTool
from src.tools.git_tools import GitTool
from src.tools.search_tools import SearchTool

__all__ = [
    "CodeAnalysisTool",
    "FileOperationsTool",
    "GitTool",
    "SearchTool",
]
