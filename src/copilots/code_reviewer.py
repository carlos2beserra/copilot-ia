# =============================================================================
# Copilot-IA - Code Reviewer Copilot
# =============================================================================
"""
Copiloto especializado em revisão e análise de código.

Este copiloto analisa código fonte e fornece feedback detalhado sobre:
- Bugs e erros potenciais
- Problemas de segurança
- Otimizações de performance
- Legibilidade e manutenibilidade
- Conformidade com boas práticas
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.agents.base import AgentResponse, BaseCopilotAgent, ModelConfig
from src.tools.code_analysis import CodeAnalysisTool
from src.tools.file_operations import FileOperationsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class IssueSeverity(str, Enum):
    """Severidade dos problemas encontrados."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Categorias de problemas."""

    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    COMPLEXITY = "complexity"


class CodeIssue(BaseModel):
    """Problema identificado no código."""

    severity: IssueSeverity
    category: IssueCategory
    line: int | None = None
    message: str
    suggestion: str | None = None
    code_snippet: str | None = None


class ReviewResult(BaseModel):
    """Resultado da revisão de código."""

    file_path: str
    language: str
    issues: list[CodeIssue] = Field(default_factory=list)
    summary: str
    score: float = Field(ge=0, le=10, description="Score de qualidade (0-10)")
    recommendations: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class CodeReviewerCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em revisão de código.

    Analisa código fonte e fornece feedback construtivo sobre qualidade,
    bugs potenciais, segurança e boas práticas.

    Example:
        >>> reviewer = CodeReviewerCopilot()
        >>> result = reviewer.analyze_file("src/main.py")
        >>> print(result.summary)
        >>> for issue in result.issues:
        ...     print(f"[{issue.severity}] {issue.message}")
    """

    INSTRUCTIONS = """
    Você é um revisor de código experiente e detalhista.
    
    Seu objetivo é analisar código e fornecer feedback construtivo e acionável.
    
    ## Áreas de Análise
    
    1. **Bugs e Erros Potenciais**
       - Erros lógicos
       - Null pointer exceptions
       - Race conditions
       - Memory leaks
       - Tratamento inadequado de exceções
    
    2. **Segurança**
       - Vulnerabilidades de injeção
       - Exposição de dados sensíveis
       - Autenticação/autorização inadequada
       - Validação de entrada insuficiente
    
    3. **Performance**
       - Loops ineficientes
       - Consultas N+1
       - Uso excessivo de memória
       - Operações bloqueantes desnecessárias
    
    4. **Legibilidade e Manutenibilidade**
       - Nomenclatura clara
       - Funções muito longas
       - Complexidade ciclomática alta
       - Falta de documentação
    
    5. **Boas Práticas**
       - Princípios SOLID
       - DRY (Don't Repeat Yourself)
       - KISS (Keep It Simple)
       - Padrões da linguagem
    
    ## Formato da Resposta
    
    Forneça sua análise em Markdown com:
    - Resumo executivo
    - Lista de problemas encontrados (com severidade)
    - Sugestões de correção
    - Score de qualidade (0-10)
    - Recomendações gerais
    """

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o Code Reviewer Copilot.

        Args:
            model_config: Configurações do modelo LLM
        """
        # Configuração específica para revisão de código
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.2,  # Baixa para análises precisas
                max_tokens=4096,
            )

        # Ferramentas disponíveis
        tools = [
            CodeAnalysisTool(),
            FileOperationsTool(),
        ]

        super().__init__(
            name="Code Reviewer",
            description="Analisa código, identifica problemas e sugere melhorias",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e executa a revisão.

        Args:
            input_data: Pode ser:
                - str: Caminho do arquivo ou código direto
                - dict: {"code": str, "language": str, "filename": str}

        Returns:
            AgentResponse com o resultado da revisão
        """
        if isinstance(input_data, dict):
            code = input_data.get("code", "")
            language = input_data.get("language", "python")
            filename = input_data.get("filename", "unknown")
            message = input_data.get("message", "")

            if message:
                prompt = f"""
                Solicitação: {message}
                
                Arquivo: {filename}
                Linguagem: {language}
                
                Código:
                ```{language}
                {code}
                ```
                
                Por favor, realize uma revisão completa do código.
                """
            else:
                prompt = f"""
                Analise o seguinte código:
                
                Arquivo: {filename}
                Linguagem: {language}
                
                ```{language}
                {code}
                ```
                """
        else:
            prompt = f"Analise o seguinte código:\n\n{input_data}"

        return self.run(prompt)

    def analyze_file(self, file_path: str) -> AgentResponse:
        """
        Analisa um arquivo de código.

        Args:
            file_path: Caminho para o arquivo

        Returns:
            AgentResponse com a análise
        """
        path = Path(file_path)

        if not path.exists():
            return AgentResponse(
                success=False,
                content=f"Arquivo não encontrado: {file_path}",
                metadata={"error": "file_not_found"},
            )

        code = path.read_text(encoding="utf-8")
        language = self._detect_language(path.suffix)

        return self.process(
            {
                "code": code,
                "language": language,
                "filename": path.name,
            }
        )

    def analyze_code(
        self, code: str, language: str = "python", focus: list[IssueCategory] | None = None
    ) -> AgentResponse:
        """
        Analisa um trecho de código.

        Args:
            code: Código a ser analisado
            language: Linguagem de programação
            focus: Categorias específicas para focar

        Returns:
            AgentResponse com a análise
        """
        focus_str = ""
        if focus:
            focus_str = f"\n\nFoque especialmente em: {', '.join(f.value for f in focus)}"

        prompt = f"""
        Analise o seguinte código {language}:
        
        ```{language}
        {code}
        ```
        {focus_str}
        
        Forneça uma revisão detalhada seguindo as diretrizes.
        """

        return self.run(prompt)

    def analyze_diff(self, diff: str, context: str | None = None) -> AgentResponse:
        """
        Analisa um diff/patch de código.

        Args:
            diff: Conteúdo do diff
            context: Contexto adicional sobre a mudança

        Returns:
            AgentResponse com a análise do diff
        """
        context_str = f"\n\nContexto: {context}" if context else ""

        prompt = f"""
        Analise as seguintes alterações de código:
        
        ```diff
        {diff}
        ```
        {context_str}
        
        Avalie:
        1. As mudanças introduzem bugs?
        2. Há problemas de segurança?
        3. O código segue boas práticas?
        4. Sugestões de melhoria
        """

        return self.run(prompt)

    def quick_review(self, code: str, language: str = "python") -> AgentResponse:
        """
        Realiza uma revisão rápida focando nos problemas mais críticos.

        Args:
            code: Código a ser revisado
            language: Linguagem de programação

        Returns:
            AgentResponse com os top 5 problemas
        """
        prompt = f"""
        Faça uma revisão RÁPIDA do código abaixo.
        Liste apenas os TOP 5 problemas mais importantes.
        Seja conciso e direto.
        
        ```{language}
        {code}
        ```
        """

        return self.run(prompt)

    def _detect_language(self, extension: str) -> str:
        """Detecta a linguagem pela extensão do arquivo."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".c": "c",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".vue": "vue",
            ".sql": "sql",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
        }
        return language_map.get(extension.lower(), "text")
