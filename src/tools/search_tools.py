# =============================================================================
# Copilot-IA - Ferramenta de Busca
# =============================================================================
"""
Ferramenta para busca em código e documentação.

Fornece funcionalidades para:
- Busca por texto/regex
- Busca por símbolos
- Busca semântica (com embeddings)
"""

import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class SearchMatch(BaseModel):
    """Resultado de uma busca."""

    file_path: str
    line_number: int
    line_content: str
    match_start: int = 0
    match_end: int = 0
    context_before: list[str] = Field(default_factory=list)
    context_after: list[str] = Field(default_factory=list)


class SymbolInfo(BaseModel):
    """Informações sobre um símbolo encontrado."""

    name: str
    type: str  # function, class, variable, constant
    file_path: str
    line_number: int
    signature: str | None = None


# -----------------------------------------------------------------------------
# Ferramenta
# -----------------------------------------------------------------------------
class SearchTool:
    """
    Ferramenta para busca em código.

    Permite aos agentes buscar texto, padrões e símbolos
    no código do projeto.

    Example:
        >>> tool = SearchTool()
        >>> results = tool.search_text("def process", "src/")
        >>> symbols = tool.find_symbol("MyClass")
    """

    name = "search_tools"
    description = "Busca texto, padrões e símbolos no código"

    # Extensões de arquivo para busca
    CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".cs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".swift",
        ".kt",
        ".scala",
        ".vue",
        ".sql",
        ".sh",
    }

    # Diretórios ignorados
    IGNORED_DIRS = {
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".next",
        "coverage",
    }

    def __init__(self, workspace_root: str | None = None):
        """
        Inicializa a ferramenta de busca.

        Args:
            workspace_root: Diretório raiz do workspace
        """
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        logger.debug(f"SearchTool inicializada com root: {self.workspace_root}")

    def search_text(
        self,
        query: str,
        path: str = ".",
        case_sensitive: bool = False,
        max_results: int = 100,
        context_lines: int = 2,
        file_pattern: str | None = None,
    ) -> list[SearchMatch]:
        """
        Busca texto em arquivos.

        Args:
            query: Texto a buscar
            path: Diretório ou arquivo para buscar
            case_sensitive: Busca case sensitive
            max_results: Número máximo de resultados
            context_lines: Linhas de contexto antes/depois
            file_pattern: Padrão glob para filtrar arquivos

        Returns:
            Lista de SearchMatch
        """
        search_path = self._resolve_path(path)

        if not search_path.exists():
            return []

        # Compilar regex
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(re.escape(query), flags)
        except re.error:
            return []

        matches = []

        # Buscar em arquivos
        files = self._get_files(search_path, file_pattern)

        for file_path in files:
            if len(matches) >= max_results:
                break

            file_matches = self._search_in_file(
                file_path, pattern, context_lines, max_results - len(matches)
            )
            matches.extend(file_matches)

        return matches

    def search_regex(
        self, pattern: str, path: str = ".", max_results: int = 100, context_lines: int = 2
    ) -> list[SearchMatch]:
        """
        Busca usando expressão regular.

        Args:
            pattern: Padrão regex
            path: Diretório ou arquivo
            max_results: Número máximo de resultados
            context_lines: Linhas de contexto

        Returns:
            Lista de SearchMatch
        """
        search_path = self._resolve_path(path)

        if not search_path.exists():
            return []

        try:
            regex = re.compile(pattern)
        except re.error as e:
            logger.error(f"Regex inválido: {e}")
            return []

        matches = []
        files = self._get_files(search_path)

        for file_path in files:
            if len(matches) >= max_results:
                break

            file_matches = self._search_in_file(
                file_path, regex, context_lines, max_results - len(matches)
            )
            matches.extend(file_matches)

        return matches

    def find_symbol(
        self, symbol_name: str, path: str = ".", symbol_type: str | None = None
    ) -> list[SymbolInfo]:
        """
        Busca por definição de símbolo (função, classe, variável).

        Args:
            symbol_name: Nome do símbolo
            path: Diretório para buscar
            symbol_type: Tipo específico (function, class, variable)

        Returns:
            Lista de SymbolInfo
        """
        search_path = self._resolve_path(path)

        if not search_path.exists():
            return []

        symbols = []

        # Padrões para diferentes linguagens
        patterns = self._get_symbol_patterns(symbol_name, symbol_type)

        files = self._get_files(search_path)

        for file_path in files:
            ext = file_path.suffix.lower()

            if ext not in patterns:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.split("\n")

                for pattern_info in patterns[ext]:
                    regex = re.compile(pattern_info["pattern"])

                    for i, line in enumerate(lines, 1):
                        match = regex.search(line)
                        if match:
                            symbols.append(
                                SymbolInfo(
                                    name=symbol_name,
                                    type=pattern_info["type"],
                                    file_path=str(file_path),
                                    line_number=i,
                                    signature=line.strip(),
                                )
                            )
            except (UnicodeDecodeError, PermissionError):
                pass

        return symbols

    def find_references(
        self, symbol_name: str, path: str = ".", max_results: int = 100
    ) -> list[SearchMatch]:
        """
        Encontra referências a um símbolo.

        Args:
            symbol_name: Nome do símbolo
            path: Diretório para buscar
            max_results: Número máximo de resultados

        Returns:
            Lista de SearchMatch
        """
        # Usa busca de texto com word boundary
        pattern = rf"\b{re.escape(symbol_name)}\b"

        try:
            regex = re.compile(pattern)
        except re.error:
            return []

        search_path = self._resolve_path(path)
        matches = []
        files = self._get_files(search_path)

        for file_path in files:
            if len(matches) >= max_results:
                break

            file_matches = self._search_in_file(file_path, regex, 1, max_results - len(matches))
            matches.extend(file_matches)

        return matches

    def find_todos(self, path: str = ".") -> list[SearchMatch]:
        """
        Encontra comentários TODO, FIXME, HACK, etc.

        Args:
            path: Diretório para buscar

        Returns:
            Lista de SearchMatch com TODOs
        """
        pattern = r"\b(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]*(.+)"
        return self.search_regex(pattern, path, max_results=200, context_lines=0)

    def _get_files(self, path: Path, file_pattern: str | None = None) -> list[Path]:
        """Obtém lista de arquivos para busca."""
        files = []

        if path.is_file():
            return [path]

        for root, dirs, filenames in os.walk(path):
            # Filtrar diretórios ignorados
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.startswith(".")]

            for filename in filenames:
                filepath = Path(root) / filename

                # Filtrar por extensão
                if filepath.suffix.lower() not in self.CODE_EXTENSIONS:
                    continue

                # Filtrar por padrão
                if file_pattern and not filepath.match(file_pattern):
                    continue

                files.append(filepath)

        return files

    def _search_in_file(
        self, file_path: Path, pattern: re.Pattern, context_lines: int, max_matches: int
    ) -> list[SearchMatch]:
        """Busca padrão em um arquivo."""
        matches = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            return []

        lines = content.split("\n")

        for i, line in enumerate(lines):
            if len(matches) >= max_matches:
                break

            match = pattern.search(line)
            if match:
                # Contexto
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)

                matches.append(
                    SearchMatch(
                        file_path=str(file_path),
                        line_number=i + 1,
                        line_content=line,
                        match_start=match.start(),
                        match_end=match.end(),
                        context_before=lines[start:i],
                        context_after=lines[i + 1 : end],
                    )
                )

        return matches

    def _get_symbol_patterns(
        self, symbol_name: str, symbol_type: str | None
    ) -> dict[str, list[dict]]:
        """Retorna padrões de busca por linguagem."""
        patterns = {
            ".py": [
                {"pattern": rf"^\s*def\s+{re.escape(symbol_name)}\s*\(", "type": "function"},
                {
                    "pattern": rf"^\s*async\s+def\s+{re.escape(symbol_name)}\s*\(",
                    "type": "function",
                },
                {"pattern": rf"^\s*class\s+{re.escape(symbol_name)}\s*[\(:]", "type": "class"},
                {"pattern": rf"^\s*{re.escape(symbol_name)}\s*=", "type": "variable"},
            ],
            ".js": [
                {"pattern": rf"function\s+{re.escape(symbol_name)}\s*\(", "type": "function"},
                {"pattern": rf"const\s+{re.escape(symbol_name)}\s*=", "type": "variable"},
                {"pattern": rf"let\s+{re.escape(symbol_name)}\s*=", "type": "variable"},
                {"pattern": rf"class\s+{re.escape(symbol_name)}\s*[\{{]", "type": "class"},
            ],
            ".ts": [
                {"pattern": rf"function\s+{re.escape(symbol_name)}\s*[\(<]", "type": "function"},
                {"pattern": rf"const\s+{re.escape(symbol_name)}\s*[=:]", "type": "variable"},
                {"pattern": rf"class\s+{re.escape(symbol_name)}\s*[\{{<]", "type": "class"},
                {"pattern": rf"interface\s+{re.escape(symbol_name)}\s*[\{{<]", "type": "interface"},
            ],
        }

        # Adicionar mesmos padrões para extensões similares
        patterns[".tsx"] = patterns[".ts"]
        patterns[".jsx"] = patterns[".js"]

        # Filtrar por tipo se especificado
        if symbol_type:
            for ext in patterns:
                patterns[ext] = [p for p in patterns[ext] if p["type"] == symbol_type]

        return patterns

    def _resolve_path(self, path: str) -> Path:
        """Resolve caminho relativo ao workspace."""
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def __repr__(self) -> str:
        return f"<SearchTool(workspace='{self.workspace_root}')>"
