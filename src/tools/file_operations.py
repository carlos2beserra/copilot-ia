# =============================================================================
# Copilot-IA - Ferramenta de Operações de Arquivo
# =============================================================================
"""
Ferramenta para operações de sistema de arquivos.

Fornece funcionalidades seguras para:
- Leitura de arquivos
- Listagem de diretórios
- Busca de arquivos
- Análise de estrutura de projeto
"""

import fnmatch
import os
from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class FileInfo(BaseModel):
    """Informações sobre um arquivo."""

    path: str
    name: str
    extension: str
    size_bytes: int
    is_directory: bool
    last_modified: float | None = None


class DirectoryStructure(BaseModel):
    """Estrutura de diretório."""

    path: str
    files: list[str] = Field(default_factory=list)
    directories: list[str] = Field(default_factory=list)
    total_files: int = 0
    total_size: int = 0


# -----------------------------------------------------------------------------
# Ferramenta
# -----------------------------------------------------------------------------
class FileOperationsTool:
    """
    Ferramenta para operações de arquivo seguras.

    Permite aos agentes ler arquivos e explorar a estrutura
    de diretórios do projeto.

    Example:
        >>> tool = FileOperationsTool()
        >>> content = tool.read_file("src/main.py")
        >>> structure = tool.get_directory_structure("src/")
    """

    name = "file_operations"
    description = "Lê arquivos e explora estrutura de diretórios"

    # Extensões permitidas para leitura
    ALLOWED_EXTENSIONS = {
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
        ".bash",
        ".zsh",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".xml",
        ".html",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".md",
        ".txt",
        ".rst",
        ".ini",
        ".cfg",
        ".conf",
        ".env",
        ".gitignore",
        ".dockerignore",
        "Dockerfile",
        "Makefile",
        "requirements.txt",
        "package.json",
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
        ".env",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".next",
        "coverage",
        ".coverage",
        "htmlcov",
        ".idea",
        ".vscode",
    }

    # Tamanho máximo de arquivo para leitura (em bytes)
    MAX_FILE_SIZE = 1_000_000  # 1 MB

    def __init__(self, workspace_root: str | None = None):
        """
        Inicializa a ferramenta.

        Args:
            workspace_root: Diretório raiz do workspace (opcional)
        """
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        logger.debug(f"FileOperationsTool inicializada com root: {self.workspace_root}")

    def read_file(self, file_path: str, max_lines: int | None = None) -> str:
        """
        Lê o conteúdo de um arquivo.

        Args:
            file_path: Caminho do arquivo (relativo ou absoluto)
            max_lines: Número máximo de linhas a ler

        Returns:
            Conteúdo do arquivo

        Raises:
            FileNotFoundError: Se arquivo não existe
            PermissionError: Se arquivo não permitido
            ValueError: Se arquivo muito grande
        """
        path = self._resolve_path(file_path)

        # Validações de segurança
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        if not path.is_file():
            raise ValueError(f"Não é um arquivo: {file_path}")

        if not self._is_allowed_file(path):
            raise PermissionError(f"Tipo de arquivo não permitido: {file_path}")

        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Arquivo muito grande ({file_size} bytes). Máximo: {self.MAX_FILE_SIZE}"
            )

        # Ler arquivo
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")

        if max_lines:
            lines = content.split("\n")
            content = "\n".join(lines[:max_lines])
            if len(lines) > max_lines:
                content += f"\n\n... ({len(lines) - max_lines} linhas omitidas)"

        return content

    def get_file_info(self, file_path: str) -> FileInfo:
        """
        Obtém informações sobre um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            FileInfo com informações do arquivo
        """
        path = self._resolve_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        stat = path.stat()

        return FileInfo(
            path=str(path),
            name=path.name,
            extension=path.suffix,
            size_bytes=stat.st_size,
            is_directory=path.is_dir(),
            last_modified=stat.st_mtime,
        )

    def list_directory(self, dir_path: str = ".", include_hidden: bool = False) -> list[FileInfo]:
        """
        Lista arquivos em um diretório.

        Args:
            dir_path: Caminho do diretório
            include_hidden: Incluir arquivos ocultos

        Returns:
            Lista de FileInfo
        """
        path = self._resolve_path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {dir_path}")

        if not path.is_dir():
            raise ValueError(f"Não é um diretório: {dir_path}")

        items = []
        for item in path.iterdir():
            # Ignorar ocultos se não solicitado
            if not include_hidden and item.name.startswith("."):
                continue

            # Ignorar diretórios na lista de ignorados
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                continue

            try:
                stat = item.stat()
                items.append(
                    FileInfo(
                        path=str(item),
                        name=item.name,
                        extension=item.suffix,
                        size_bytes=stat.st_size,
                        is_directory=item.is_dir(),
                        last_modified=stat.st_mtime,
                    )
                )
            except PermissionError:
                pass

        return sorted(items, key=lambda x: (not x.is_directory, x.name.lower()))

    def get_directory_structure(
        self, dir_path: str = ".", max_depth: int = 3, include_files: bool = True
    ) -> str:
        """
        Gera uma representação em árvore da estrutura de diretórios.

        Args:
            dir_path: Caminho do diretório
            max_depth: Profundidade máxima
            include_files: Incluir arquivos (não só diretórios)

        Returns:
            String com estrutura em formato de árvore
        """
        path = self._resolve_path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {dir_path}")

        lines = [path.name + "/"]
        self._build_tree(path, lines, "", max_depth, include_files, 0)

        return "\n".join(lines)

    def _build_tree(
        self,
        path: Path,
        lines: list[str],
        prefix: str,
        max_depth: int,
        include_files: bool,
        current_depth: int,
    ):
        """Constrói a árvore recursivamente."""
        if current_depth >= max_depth:
            return

        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        # Filtrar itens
        filtered = []
        for item in items:
            if item.name.startswith("."):
                continue
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                continue
            if not include_files and not item.is_dir():
                continue
            filtered.append(item)

        for i, item in enumerate(filtered):
            is_last = i == len(filtered) - 1
            connector = "└── " if is_last else "├── "

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree(
                    item, lines, new_prefix, max_depth, include_files, current_depth + 1
                )
            else:
                lines.append(f"{prefix}{connector}{item.name}")

    def find_files(self, pattern: str, dir_path: str = ".", recursive: bool = True) -> list[str]:
        """
        Encontra arquivos que correspondem a um padrão.

        Args:
            pattern: Padrão glob (ex: "*.py", "test_*.py")
            dir_path: Diretório inicial
            recursive: Buscar recursivamente

        Returns:
            Lista de caminhos de arquivos
        """
        path = self._resolve_path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {dir_path}")

        matches = []

        if recursive:
            for root, dirs, files in os.walk(path):
                # Filtrar diretórios ignorados
                dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.startswith(".")]

                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(os.path.join(root, filename))
        else:
            for item in path.iterdir():
                if item.is_file() and fnmatch.fnmatch(item.name, pattern):
                    matches.append(str(item))

        return sorted(matches)

    def get_project_summary(self, dir_path: str = ".") -> dict:
        """
        Gera um resumo do projeto.

        Args:
            dir_path: Diretório do projeto

        Returns:
            Dicionário com resumo do projeto
        """
        path = self._resolve_path(dir_path)

        # Contadores
        file_counts = {}
        total_lines = 0
        total_size = 0

        for root, dirs, files in os.walk(path):
            # Filtrar diretórios ignorados
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS and not d.startswith(".")]

            for filename in files:
                filepath = Path(root) / filename

                if filename.startswith("."):
                    continue

                ext = filepath.suffix or filename
                file_counts[ext] = file_counts.get(ext, 0) + 1

                try:
                    total_size += filepath.stat().st_size

                    if self._is_allowed_file(filepath):
                        try:
                            content = filepath.read_text(encoding="utf-8")
                            total_lines += len(content.split("\n"))
                        except (UnicodeDecodeError, PermissionError):
                            pass
                except (OSError, PermissionError):
                    pass

        return {
            "total_files": sum(file_counts.values()),
            "total_lines": total_lines,
            "total_size_bytes": total_size,
            "total_size_human": self._human_readable_size(total_size),
            "file_types": dict(sorted(file_counts.items(), key=lambda x: -x[1])),
        }

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve caminho relativo ao workspace."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.workspace_root / path
        return path.resolve()

    def _is_allowed_file(self, path: Path) -> bool:
        """Verifica se o arquivo é permitido para leitura."""
        # Verificar extensão
        if path.suffix in self.ALLOWED_EXTENSIONS:
            return True

        # Verificar nome completo (para arquivos sem extensão como Dockerfile)
        if path.name in self.ALLOWED_EXTENSIONS:
            return True

        return False

    def _human_readable_size(self, size_bytes: int) -> str:
        """Converte bytes para formato legível."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def __repr__(self) -> str:
        return f"<FileOperationsTool(workspace='{self.workspace_root}')>"
