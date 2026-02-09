# =============================================================================
# Copilot-IA - Ferramenta de Análise de Código
# =============================================================================
"""
Ferramenta para análise estática de código.

Fornece funcionalidades como:
- Parsing de código (AST)
- Métricas de complexidade
- Detecção de padrões
- Extração de símbolos
"""

import ast
import re
from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class CodeMetrics(BaseModel):
    """Métricas de código."""

    lines_of_code: int = Field(description="Total de linhas")
    lines_of_code_logical: int = Field(description="Linhas lógicas (sem comentários/vazias)")
    num_functions: int = Field(description="Número de funções")
    num_classes: int = Field(description="Número de classes")
    num_imports: int = Field(description="Número de imports")
    avg_function_length: float = Field(description="Média de linhas por função")
    max_function_length: int = Field(description="Função mais longa")
    cyclomatic_complexity: float | None = Field(
        default=None, description="Complexidade ciclomática média"
    )


class FunctionInfo(BaseModel):
    """Informações sobre uma função."""

    name: str
    line_start: int
    line_end: int
    num_args: int
    has_docstring: bool
    is_async: bool
    decorators: list[str] = Field(default_factory=list)


class ClassInfo(BaseModel):
    """Informações sobre uma classe."""

    name: str
    line_start: int
    line_end: int
    base_classes: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    has_docstring: bool


# -----------------------------------------------------------------------------
# Ferramenta
# -----------------------------------------------------------------------------
class CodeAnalysisTool:
    """
    Ferramenta para análise estática de código.

    Permite aos agentes analisar código fonte para obter
    métricas, estrutura e informações úteis.

    Example:
        >>> tool = CodeAnalysisTool()
        >>> metrics = tool.get_metrics(code, "python")
        >>> functions = tool.extract_functions(code, "python")
    """

    name = "code_analysis"
    description = "Analisa código fonte e extrai métricas, funções, classes e padrões"

    def __init__(self):
        """Inicializa a ferramenta de análise."""
        logger.debug("CodeAnalysisTool inicializada")

    def get_metrics(self, code: str, language: str = "python") -> CodeMetrics:
        """
        Calcula métricas do código.

        Args:
            code: Código fonte
            language: Linguagem de programação

        Returns:
            CodeMetrics com as métricas calculadas
        """
        lines = code.split("\n")
        total_lines = len(lines)

        # Linhas lógicas (não vazias, não comentários)
        logical_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
                logical_lines += 1

        # Análise específica por linguagem
        if language == "python":
            return self._analyze_python(code, total_lines, logical_lines)
        else:
            # Análise genérica
            return CodeMetrics(
                lines_of_code=total_lines,
                lines_of_code_logical=logical_lines,
                num_functions=code.count("def ") + code.count("function "),
                num_classes=code.count("class "),
                num_imports=code.count("import "),
                avg_function_length=0.0,
                max_function_length=0,
            )

    def _analyze_python(self, code: str, total_lines: int, logical_lines: int) -> CodeMetrics:
        """Análise específica para Python."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return CodeMetrics(
                lines_of_code=total_lines,
                lines_of_code_logical=logical_lines,
                num_functions=0,
                num_classes=0,
                num_imports=0,
                avg_function_length=0.0,
                max_function_length=0,
            )

        functions = []
        classes = []
        imports = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
                functions.append(func_lines)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1

        avg_func_length = sum(functions) / len(functions) if functions else 0
        max_func_length = max(functions) if functions else 0

        return CodeMetrics(
            lines_of_code=total_lines,
            lines_of_code_logical=logical_lines,
            num_functions=len(functions),
            num_classes=len(classes),
            num_imports=imports,
            avg_function_length=round(avg_func_length, 2),
            max_function_length=max_func_length,
        )

    def extract_functions(self, code: str, language: str = "python") -> list[FunctionInfo]:
        """
        Extrai informações sobre funções no código.

        Args:
            code: Código fonte
            language: Linguagem de programação

        Returns:
            Lista de FunctionInfo
        """
        if language != "python":
            return []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Verifica docstring
                has_docstring = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )

                # Decorators
                decorators = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorators.append(dec.id)
                    elif isinstance(dec, ast.Attribute):
                        decorators.append(
                            f"{dec.value.id}.{dec.attr}"
                            if isinstance(dec.value, ast.Name)
                            else dec.attr
                        )

                functions.append(
                    FunctionInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        num_args=len(node.args.args),
                        has_docstring=has_docstring,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                        decorators=decorators,
                    )
                )

        return functions

    def extract_classes(self, code: str, language: str = "python") -> list[ClassInfo]:
        """
        Extrai informações sobre classes no código.

        Args:
            code: Código fonte
            language: Linguagem de programação

        Returns:
            Lista de ClassInfo
        """
        if language != "python":
            return []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(
                            f"{base.value.id}.{base.attr}"
                            if isinstance(base.value, ast.Name)
                            else base.attr
                        )

                # Methods
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)

                # Docstring
                has_docstring = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )

                classes.append(
                    ClassInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        base_classes=bases,
                        methods=methods,
                        has_docstring=has_docstring,
                    )
                )

        return classes

    def find_patterns(self, code: str, patterns: list[str]) -> dict[str, list[int]]:
        """
        Encontra padrões (regex) no código.

        Args:
            code: Código fonte
            patterns: Lista de padrões regex

        Returns:
            Dicionário com padrão -> lista de linhas
        """
        results = {}
        lines = code.split("\n")

        for pattern in patterns:
            results[pattern] = []
            try:
                regex = re.compile(pattern)
                for i, line in enumerate(lines, 1):
                    if regex.search(line):
                        results[pattern].append(i)
            except re.error:
                pass

        return results

    def detect_language(self, file_path: str) -> str:
        """
        Detecta a linguagem de programação pelo arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Nome da linguagem
        """
        path = Path(file_path)
        extension = path.suffix.lower()

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
            ".md": "markdown",
        }

        return language_map.get(extension, "text")

    def get_imports(self, code: str, language: str = "python") -> list[str]:
        """
        Extrai lista de imports do código.

        Args:
            code: Código fonte
            language: Linguagem de programação

        Returns:
            Lista de módulos importados
        """
        if language != "python":
            return []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def __repr__(self) -> str:
        return f"<CodeAnalysisTool(name='{self.name}')>"
