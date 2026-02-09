# =============================================================================
# Copilot-IA - Sistema de Cache
# =============================================================================
"""
Sistema de cache para respostas e embeddings.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheEntry(BaseModel):
    """Entrada de cache."""

    key: str
    value: Any
    created_at: float
    expires_at: float | None = None
    hit_count: int = 0


class Cache:
    """
    Sistema de cache em disco.

    Armazena respostas de LLM e outros dados para evitar
    requisições redundantes.

    Example:
        >>> cache = Cache(cache_dir="data/cache")
        >>>
        >>> # Armazenar
        >>> cache.set("key", {"response": "value"}, ttl=3600)
        >>>
        >>> # Recuperar
        >>> value = cache.get("key")
    """

    def __init__(
        self, cache_dir: str = "data/cache", default_ttl: int = 3600, enabled: bool = True
    ):
        """
        Inicializa o cache.

        Args:
            cache_dir: Diretório para armazenar cache
            default_ttl: TTL padrão em segundos
            enabled: Se o cache está habilitado
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.enabled = enabled

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Cache inicializado em: {self.cache_dir}")

    def _get_key_hash(self, key: str) -> str:
        """Gera hash da chave."""
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def _get_cache_path(self, key: str) -> Path:
        """Obtém caminho do arquivo de cache."""
        key_hash = self._get_key_hash(key)
        # Usar subdiretórios para evitar muitos arquivos em um diretório
        subdir = key_hash[:2]
        return self.cache_dir / subdir / f"{key_hash}.json"

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        Armazena valor no cache.

        Args:
            key: Chave única
            value: Valor para armazenar (deve ser JSON serializable)
            ttl: Tempo de vida em segundos

        Returns:
            True se armazenado com sucesso
        """
        if not self.enabled:
            return False

        ttl = ttl or self.default_ttl
        now = time.time()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl if ttl > 0 else None,
        )

        cache_path = self._get_cache_path(key)

        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(entry.model_dump_json(indent=2), encoding="utf-8")
            logger.debug(f"Cache set: {key[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False

    def get(self, key: str) -> Any | None:
        """
        Recupera valor do cache.

        Args:
            key: Chave para buscar

        Returns:
            Valor ou None se não encontrado/expirado
        """
        if not self.enabled:
            return None

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            entry = CacheEntry(**data)

            # Verificar expiração
            if entry.expires_at and time.time() > entry.expires_at:
                self.delete(key)
                return None

            # Atualizar hit count
            entry.hit_count += 1
            cache_path.write_text(entry.model_dump_json(indent=2), encoding="utf-8")

            logger.debug(f"Cache hit: {key[:50]}...")
            return entry.value

        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Remove entrada do cache.

        Args:
            key: Chave para remover

        Returns:
            True se removido
        """
        cache_path = self._get_cache_path(key)

        try:
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cache deleted: {key[:50]}...")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        if not self.enabled:
            return False

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return False

        # Verificar expiração
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            entry = CacheEntry(**data)

            if entry.expires_at and time.time() > entry.expires_at:
                self.delete(key)
                return False

            return True
        except Exception:
            return False

    def clear(self) -> int:
        """
        Limpa todo o cache.

        Returns:
            Número de entradas removidas
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass

        logger.info(f"Cache limpo: {count} entradas removidas")
        return count

    def clear_expired(self) -> int:
        """
        Remove entradas expiradas.

        Returns:
            Número de entradas removidas
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        now = time.time()

        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                entry = CacheEntry(**data)

                if entry.expires_at and now > entry.expires_at:
                    cache_file.unlink()
                    count += 1
            except Exception:
                pass

        logger.info(f"Cache cleanup: {count} entradas expiradas removidas")
        return count

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache.

        Returns:
            Dicionário com estatísticas
        """
        if not self.cache_dir.exists():
            return {
                "total_entries": 0,
                "total_size_bytes": 0,
                "expired_entries": 0,
            }

        total = 0
        expired = 0
        total_size = 0
        now = time.time()

        for cache_file in self.cache_dir.rglob("*.json"):
            total += 1
            total_size += cache_file.stat().st_size

            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                entry = CacheEntry(**data)

                if entry.expires_at and now > entry.expires_at:
                    expired += 1
            except Exception:
                pass

        return {
            "total_entries": total,
            "expired_entries": expired,
            "valid_entries": total - expired,
            "total_size_bytes": total_size,
            "total_size_human": self._human_readable_size(total_size),
            "cache_dir": str(self.cache_dir),
        }

    def _human_readable_size(self, size_bytes: int) -> str:
        """Converte bytes para formato legível."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    # Context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def cache_response(cache: Cache, key_prefix: str = "", ttl: int | None = None):
    """
    Decorator para cachear respostas de funções.

    Args:
        cache: Instância de Cache
        key_prefix: Prefixo para a chave
        ttl: TTL em segundos

    Example:
        >>> @cache_response(cache, key_prefix="review", ttl=3600)
        ... def review_code(code: str) -> str:
        ...     return expensive_llm_call(code)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)

            # Tentar obter do cache
            cached = cache.get(key)
            if cached is not None:
                return cached

            # Executar função
            result = func(*args, **kwargs)

            # Salvar no cache
            cache.set(key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
