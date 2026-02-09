# =============================================================================
# Copilot-IA - Documentation Copilot
# =============================================================================
"""
Copiloto especializado em geração de documentação.

Este copiloto gera documentação de código incluindo:
- Docstrings (Google, NumPy, Sphinx styles)
- README files
- Documentação de API
- Comentários explicativos
"""

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from src.agents.base import AgentResponse, BaseCopilotAgent, ModelConfig
from src.tools.file_operations import FileOperationsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class DocstringStyle(str, Enum):
    """Estilos de docstring suportados."""

    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"


class DocumentationType(str, Enum):
    """Tipos de documentação."""

    DOCSTRING = "docstring"
    README = "readme"
    API = "api"
    INLINE_COMMENTS = "inline"
    CHANGELOG = "changelog"


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class DocumentationCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em geração de documentação.

    Gera documentação clara e informativa para código, incluindo
    docstrings, READMEs, documentação de API e comentários.

    Example:
        >>> doc_copilot = DocumentationCopilot()
        >>>
        >>> # Gerar docstring
        >>> result = doc_copilot.generate_docstring(code, style="google")
        >>>
        >>> # Gerar README
        >>> result = doc_copilot.generate_readme(project_info)
    """

    INSTRUCTIONS = """
    Você é um escritor técnico especializado em documentação de software.
    
    ## Suas Responsabilidades
    
    1. **Docstrings**
       - Gerar docstrings claras e informativas
       - Seguir o estilo especificado (Google, NumPy, Sphinx)
       - Incluir parâmetros, retornos, exceções e exemplos
    
    2. **README Files**
       - Criar READMEs completos e bem estruturados
       - Incluir badges, instalação, uso, exemplos
       - Adaptar ao contexto do projeto
    
    3. **Documentação de API**
       - Documentar endpoints e funções públicas
       - Incluir exemplos de requisição/resposta
       - Especificar tipos e formatos
    
    4. **Comentários de Código**
       - Adicionar comentários explicativos quando necessário
       - Explicar lógica complexa
       - Manter código autodocumentado
    
    ## Princípios
    
    - Clareza: Documentação deve ser fácil de entender
    - Completude: Cobrir todos os aspectos importantes
    - Atualização: Manter documentação sincronizada com o código
    - Exemplos: Incluir exemplos práticos sempre que possível
    
    ## Formato
    
    Use Markdown para formatação. Seja preciso com tipos e descrições.
    """

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        default_style: DocstringStyle = DocstringStyle.GOOGLE,
    ):
        """
        Inicializa o Documentation Copilot.

        Args:
            model_config: Configurações do modelo LLM
            default_style: Estilo padrão de docstring
        """
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.4,
                max_tokens=4096,
            )

        self.default_style = default_style

        tools = [
            FileOperationsTool(),
        ]

        super().__init__(
            name="Documentation Writer",
            description="Gera documentação, docstrings e README",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e gera documentação.

        Args:
            input_data: Dicionário com informações para documentação

        Returns:
            AgentResponse com a documentação gerada
        """
        if isinstance(input_data, dict):
            doc_type = input_data.get("type", "docstring")
            code = input_data.get("code", "")
            message = input_data.get("message", "")

            if doc_type == "docstring":
                return self.generate_docstring(code)
            elif doc_type == "readme":
                return self.generate_readme(input_data)
            elif message:
                return self.run(f"{message}\n\nCódigo:\n```\n{code}\n```")

        return self.run(f"Gere documentação para:\n{input_data}")

    def generate_docstring(
        self, code: str, language: str = "python", style: DocstringStyle | None = None
    ) -> AgentResponse:
        """
        Gera docstring para uma função ou classe.

        Args:
            code: Código da função/classe
            language: Linguagem de programação
            style: Estilo de docstring (Google, NumPy, Sphinx)

        Returns:
            AgentResponse com a docstring gerada
        """
        style = style or self.default_style

        prompt = f"""
        Gere uma docstring completa no estilo **{style.value}** para o seguinte código:
        
        ```{language}
        {code}
        ```
        
        A docstring deve incluir:
        - Descrição clara do propósito
        - Parâmetros com tipos e descrições
        - Retorno com tipo e descrição
        - Exceções que podem ser levantadas
        - Exemplo de uso (se aplicável)
        
        Retorne APENAS a docstring, formatada corretamente para {language}.
        """

        return self.run(prompt)

    def generate_readme(self, project_info: dict) -> AgentResponse:
        """
        Gera um README.md completo para um projeto.

        Args:
            project_info: Dicionário com informações do projeto:
                - name: Nome do projeto
                - description: Descrição
                - language: Linguagem principal
                - features: Lista de features
                - installation: Instruções de instalação
                - file_structure: Estrutura de arquivos

        Returns:
            AgentResponse com o README gerado
        """
        name = project_info.get("name", "Projeto")
        description = project_info.get("description", "")
        language = project_info.get("language", "Python")
        features = project_info.get("features", [])
        file_structure = project_info.get("file_structure", "")

        features_str = "\n".join(f"- {f}" for f in features) if features else ""

        prompt = f"""
        Gere um README.md completo e profissional para o seguinte projeto:
        
        **Nome do Projeto:** {name}
        **Descrição:** {description}
        **Linguagem Principal:** {language}
        
        **Features:**
        {features_str}
        
        **Estrutura de Arquivos:**
        ```
        {file_structure}
        ```
        
        O README deve incluir:
        1. Título com badges (build, version, license)
        2. Descrição do projeto
        3. Features/Funcionalidades
        4. Pré-requisitos
        5. Instalação
        6. Uso básico com exemplos
        7. Configuração
        8. Estrutura do projeto
        9. Contribuição
        10. Licença
        
        Use português brasileiro e Markdown bem formatado.
        """

        return self.run(prompt)

    def generate_api_docs(
        self,
        code: str,
        language: str = "python",
        format: Literal["markdown", "openapi", "asyncapi"] = "markdown",
    ) -> AgentResponse:
        """
        Gera documentação de API.

        Args:
            code: Código dos endpoints/funções
            language: Linguagem de programação
            format: Formato da documentação

        Returns:
            AgentResponse com a documentação de API
        """
        prompt = f"""
        Gere documentação de API no formato **{format}** para o seguinte código:
        
        ```{language}
        {code}
        ```
        
        Inclua:
        - Descrição de cada endpoint/função
        - Parâmetros aceitos (tipos, obrigatório/opcional)
        - Exemplos de requisição
        - Exemplos de resposta
        - Códigos de erro possíveis
        """

        return self.run(prompt)

    def add_inline_comments(self, code: str, language: str = "python") -> AgentResponse:
        """
        Adiciona comentários inline explicativos ao código.

        Args:
            code: Código a ser comentado
            language: Linguagem de programação

        Returns:
            AgentResponse com o código comentado
        """
        prompt = f"""
        Adicione comentários explicativos ao seguinte código.
        
        ```{language}
        {code}
        ```
        
        Regras:
        - Comente lógica complexa ou não óbvia
        - Não comente o óbvio
        - Mantenha comentários concisos
        - Use o estilo de comentário apropriado para {language}
        
        Retorne o código completo com os comentários adicionados.
        """

        return self.run(prompt)

    def generate_changelog(self, commits: list[dict], version: str = "0.0.0") -> AgentResponse:
        """
        Gera um CHANGELOG baseado em commits.

        Args:
            commits: Lista de commits com message e date
            version: Versão para o changelog

        Returns:
            AgentResponse com o CHANGELOG
        """
        commits_str = "\n".join(f"- {c.get('message', '')} ({c.get('date', '')})" for c in commits)

        prompt = f"""
        Gere uma entrada de CHANGELOG para a versão {version} baseado nos seguintes commits:
        
        {commits_str}
        
        Use o formato Keep a Changelog:
        - Added: para novas features
        - Changed: para mudanças em funcionalidades existentes
        - Deprecated: para features que serão removidas
        - Removed: para features removidas
        - Fixed: para correções de bugs
        - Security: para correções de vulnerabilidades
        """

        return self.run(prompt)

    def document_file(
        self, file_path: str, style: DocstringStyle | None = None
    ) -> AgentResponse:
        """
        Documenta todas as funções e classes de um arquivo.

        Args:
            file_path: Caminho do arquivo
            style: Estilo de docstring

        Returns:
            AgentResponse com o arquivo documentado
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
        style = style or self.default_style

        prompt = f"""
        Analise o seguinte arquivo e adicione/melhore a documentação:
        
        **Arquivo:** {path.name}
        **Linguagem:** {language}
        **Estilo de Docstring:** {style.value}
        
        ```{language}
        {code}
        ```
        
        Para cada função e classe:
        1. Adicione docstring completa se não existir
        2. Melhore docstrings existentes se incompletas
        3. Mantenha docstrings boas como estão
        
        Retorne o arquivo completo com a documentação.
        """

        return self.run(prompt)

    def _detect_language(self, extension: str) -> str:
        """Detecta a linguagem pela extensão."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
        }
        return language_map.get(extension.lower(), "text")
