# =============================================================================
# Copilot-IA - Ferramenta de Git
# =============================================================================
"""
Ferramenta para integração com Git.

Fornece funcionalidades para:
- Obter informações de commits
- Analisar diffs
- Listar branches
- Histórico de alterações
"""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class CommitInfo(BaseModel):
    """Informações sobre um commit."""

    hash: str = Field(description="Hash do commit")
    short_hash: str = Field(description="Hash curto")
    message: str = Field(description="Mensagem do commit")
    author: str = Field(description="Autor do commit")
    author_email: str = Field(description="Email do autor")
    date: datetime = Field(description="Data do commit")
    files_changed: int = Field(default=0, description="Arquivos alterados")


class FileChange(BaseModel):
    """Alteração em um arquivo."""

    path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0


class BranchInfo(BaseModel):
    """Informações sobre uma branch."""

    name: str
    is_current: bool = False
    last_commit: str | None = None
    tracking: str | None = None


# -----------------------------------------------------------------------------
# Ferramenta
# -----------------------------------------------------------------------------
class GitTool:
    """
    Ferramenta para operações Git.

    Permite aos agentes obter informações do repositório Git
    como commits, diffs, branches e histórico.

    Example:
        >>> tool = GitTool()
        >>> commits = tool.get_recent_commits(limit=10)
        >>> diff = tool.get_diff("HEAD~1", "HEAD")
    """

    name = "git_tools"
    description = "Obtém informações de repositório Git como commits, diffs e branches"

    def __init__(self, repo_path: str | None = None):
        """
        Inicializa a ferramenta Git.

        Args:
            repo_path: Caminho do repositório (opcional)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._repo = None
        self._init_repo()

    def _init_repo(self):
        """Inicializa o repositório Git."""
        try:
            from git import Repo

            self._repo = Repo(self.repo_path)
            logger.debug(f"Repositório Git inicializado: {self.repo_path}")
        except ImportError:
            logger.warning("GitPython não instalado. Funcionalidades Git limitadas.")
        except Exception as e:
            logger.warning(f"Não foi possível inicializar repositório Git: {e}")

    def is_git_repo(self) -> bool:
        """Verifica se é um repositório Git válido."""
        return self._repo is not None

    def get_recent_commits(self, limit: int = 10, branch: str = "HEAD") -> list[CommitInfo]:
        """
        Obtém commits recentes.

        Args:
            limit: Número máximo de commits
            branch: Branch ou referência

        Returns:
            Lista de CommitInfo
        """
        if not self._repo:
            return []

        commits = []
        try:
            for commit in self._repo.iter_commits(branch, max_count=limit):
                commits.append(
                    CommitInfo(
                        hash=commit.hexsha,
                        short_hash=commit.hexsha[:7],
                        message=commit.message.strip(),
                        author=commit.author.name,
                        author_email=commit.author.email,
                        date=datetime.fromtimestamp(commit.committed_date),
                        files_changed=len(commit.stats.files),
                    )
                )
        except Exception as e:
            logger.error(f"Erro ao obter commits: {e}")

        return commits

    def get_commit_details(self, commit_hash: str) -> CommitInfo | None:
        """
        Obtém detalhes de um commit específico.

        Args:
            commit_hash: Hash do commit

        Returns:
            CommitInfo ou None
        """
        if not self._repo:
            return None

        try:
            commit = self._repo.commit(commit_hash)
            return CommitInfo(
                hash=commit.hexsha,
                short_hash=commit.hexsha[:7],
                message=commit.message.strip(),
                author=commit.author.name,
                author_email=commit.author.email,
                date=datetime.fromtimestamp(commit.committed_date),
                files_changed=len(commit.stats.files),
            )
        except Exception as e:
            logger.error(f"Erro ao obter commit {commit_hash}: {e}")
            return None

    def get_diff(
        self, from_ref: str = "HEAD~1", to_ref: str = "HEAD", file_path: str | None = None
    ) -> str:
        """
        Obtém diff entre duas referências.

        Args:
            from_ref: Referência inicial
            to_ref: Referência final
            file_path: Filtrar por arquivo específico

        Returns:
            String com o diff
        """
        if not self._repo:
            return ""

        try:
            if file_path:
                return self._repo.git.diff(from_ref, to_ref, "--", file_path)
            return self._repo.git.diff(from_ref, to_ref)
        except Exception as e:
            logger.error(f"Erro ao obter diff: {e}")
            return ""

    def get_staged_diff(self) -> str:
        """
        Obtém diff dos arquivos staged.

        Returns:
            String com o diff staged
        """
        if not self._repo:
            return ""

        try:
            return self._repo.git.diff("--cached")
        except Exception as e:
            logger.error(f"Erro ao obter staged diff: {e}")
            return ""

    def get_file_history(self, file_path: str, limit: int = 10) -> list[CommitInfo]:
        """
        Obtém histórico de commits de um arquivo.

        Args:
            file_path: Caminho do arquivo
            limit: Número máximo de commits

        Returns:
            Lista de CommitInfo
        """
        if not self._repo:
            return []

        commits = []
        try:
            for commit in self._repo.iter_commits(paths=file_path, max_count=limit):
                commits.append(
                    CommitInfo(
                        hash=commit.hexsha,
                        short_hash=commit.hexsha[:7],
                        message=commit.message.strip(),
                        author=commit.author.name,
                        author_email=commit.author.email,
                        date=datetime.fromtimestamp(commit.committed_date),
                    )
                )
        except Exception as e:
            logger.error(f"Erro ao obter histórico do arquivo: {e}")

        return commits

    def get_branches(self, include_remote: bool = False) -> list[BranchInfo]:
        """
        Lista branches do repositório.

        Args:
            include_remote: Incluir branches remotas

        Returns:
            Lista de BranchInfo
        """
        if not self._repo:
            return []

        branches = []
        try:
            # Branch atual
            current = self._repo.active_branch.name if not self._repo.head.is_detached else None

            # Branches locais
            for branch in self._repo.branches:
                branches.append(
                    BranchInfo(
                        name=branch.name,
                        is_current=branch.name == current,
                        last_commit=branch.commit.hexsha[:7],
                        tracking=(
                            branch.tracking_branch().name if branch.tracking_branch() else None
                        ),
                    )
                )

            # Branches remotas
            if include_remote:
                for ref in self._repo.remotes.origin.refs:
                    branches.append(
                        BranchInfo(
                            name=ref.name,
                            is_current=False,
                            last_commit=ref.commit.hexsha[:7],
                        )
                    )
        except Exception as e:
            logger.error(f"Erro ao listar branches: {e}")

        return branches

    def get_changed_files(self, staged_only: bool = False) -> list[FileChange]:
        """
        Obtém arquivos modificados.

        Args:
            staged_only: Apenas arquivos staged

        Returns:
            Lista de FileChange
        """
        if not self._repo:
            return []

        changes = []
        try:
            if staged_only:
                diff = self._repo.index.diff("HEAD")
            else:
                diff = self._repo.index.diff(None)

            for item in diff:
                change_type = "modified"
                if item.new_file:
                    change_type = "added"
                elif item.deleted_file:
                    change_type = "deleted"
                elif item.renamed:
                    change_type = "renamed"

                changes.append(
                    FileChange(
                        path=item.a_path or item.b_path,
                        change_type=change_type,
                    )
                )
        except Exception as e:
            logger.error(f"Erro ao obter arquivos modificados: {e}")

        return changes

    def get_blame(self, file_path: str) -> list[dict]:
        """
        Obtém blame de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Lista de dicionários com informações de blame
        """
        if not self._repo:
            return []

        blame_info = []
        try:
            blame = self._repo.blame("HEAD", file_path)
            for commit, lines in blame:
                for line in lines:
                    blame_info.append(
                        {
                            "commit": commit.hexsha[:7],
                            "author": commit.author.name,
                            "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                            "line": line,
                        }
                    )
        except Exception as e:
            logger.error(f"Erro ao obter blame: {e}")

        return blame_info

    def get_status(self) -> dict:
        """
        Obtém status do repositório.

        Returns:
            Dicionário com status
        """
        if not self._repo:
            return {"error": "Repositório Git não disponível"}

        try:
            return {
                "branch": (
                    self._repo.active_branch.name if not self._repo.head.is_detached else "detached"
                ),
                "is_dirty": self._repo.is_dirty(),
                "untracked_files": self._repo.untracked_files,
                "staged_files": [item.a_path for item in self._repo.index.diff("HEAD")],
                "modified_files": [item.a_path for item in self._repo.index.diff(None)],
            }
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"error": str(e)}

    def __repr__(self) -> str:
        return f"<GitTool(repo='{self.repo_path}', valid={self.is_git_repo()})>"
