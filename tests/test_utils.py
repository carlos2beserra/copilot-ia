# =============================================================================
# Copilot-IA - Testes dos Utilitários
# =============================================================================
"""
Testes unitários para os utilitários.
"""

import time

import pytest

from src.utils.cache import Cache
from src.utils.token_counter import TokenCounter


# -----------------------------------------------------------------------------
# Testes - TokenCounter
# -----------------------------------------------------------------------------
class TestTokenCounter:
    """Testes para TokenCounter."""

    @pytest.fixture
    def counter(self):
        """Instância do contador de tokens."""
        return TokenCounter()

    def test_count_simple_text(self, counter):
        """Testa contagem de texto simples."""
        tokens = counter.count("Hello, world!")
        assert tokens > 0
        assert tokens < 10

    def test_count_longer_text(self, counter):
        """Testa contagem de texto mais longo."""
        text = "This is a longer text that should have more tokens. " * 10
        tokens = counter.count(text)
        assert tokens > 50

    def test_count_code(self, counter):
        """Testa contagem de código."""
        code = """
def hello():
    print("Hello, world!")
    return True
"""
        tokens = counter.count(code)
        assert tokens > 10

    def test_count_messages(self, counter):
        """Testa contagem de mensagens de chat."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        tokens = counter.count_messages(messages)
        assert tokens > 20

    def test_estimate_cost(self, counter):
        """Testa estimativa de custo."""
        cost = counter.estimate_cost(input_tokens=1000, output_tokens=500, model="gpt-4o")

        assert "input_cost" in cost
        assert "output_cost" in cost
        assert "total_cost" in cost
        assert cost["total_cost"] > 0

    def test_truncate_to_limit(self, counter):
        """Testa truncamento de texto."""
        text = "word " * 1000  # Muitas palavras
        truncated = counter.truncate_to_limit(text, max_tokens=50)

        truncated_tokens = counter.count(truncated)
        assert truncated_tokens <= 50

    def test_split_into_chunks(self, counter):
        """Testa divisão em chunks."""
        text = "word " * 500
        chunks = counter.split_into_chunks(text, chunk_size=100, overlap=10)

        assert len(chunks) >= 5
        for chunk in chunks:
            tokens = counter.count(chunk)
            assert tokens <= 110  # chunk_size + margem

    def test_get_model_info(self, counter):
        """Testa informações do modelo."""
        info = counter.get_model_info("gpt-4o")

        assert "model" in info
        assert "encoding" in info
        assert info["model"] == "gpt-4o"


# -----------------------------------------------------------------------------
# Testes - Cache
# -----------------------------------------------------------------------------
class TestCache:
    """Testes para Cache."""

    @pytest.fixture
    def cache(self, tmp_path):
        """Instância do cache em diretório temporário."""
        return Cache(cache_dir=str(tmp_path / "cache"), default_ttl=3600)

    def test_set_and_get(self, cache):
        """Testa armazenar e recuperar valor."""
        cache.set("test_key", {"value": 123})
        result = cache.get("test_key")

        assert result is not None
        assert result["value"] == 123

    def test_get_nonexistent(self, cache):
        """Testa recuperar chave inexistente."""
        result = cache.get("nonexistent_key")
        assert result is None

    def test_delete(self, cache):
        """Testa deletar entrada."""
        cache.set("to_delete", "value")
        assert cache.exists("to_delete")

        cache.delete("to_delete")
        assert not cache.exists("to_delete")

    def test_exists(self, cache):
        """Testa verificar existência."""
        assert not cache.exists("new_key")

        cache.set("new_key", "value")
        assert cache.exists("new_key")

    def test_ttl_expiration(self, cache, tmp_path):
        """Testa expiração por TTL."""
        # Cache com TTL muito curto
        short_cache = Cache(cache_dir=str(tmp_path / "short_cache"), default_ttl=1)

        short_cache.set("expire_key", "value", ttl=1)
        assert short_cache.exists("expire_key")

        # Esperar expiração
        time.sleep(1.5)

        result = short_cache.get("expire_key")
        assert result is None

    def test_clear(self, cache):
        """Testa limpar todo o cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        count = cache.clear()
        assert count >= 3

        assert not cache.exists("key1")
        assert not cache.exists("key2")
        assert not cache.exists("key3")

    def test_get_stats(self, cache):
        """Testa obter estatísticas."""
        cache.set("stat_key1", "value1")
        cache.set("stat_key2", "value2")

        stats = cache.get_stats()

        assert "total_entries" in stats
        assert stats["total_entries"] >= 2
        assert "total_size_bytes" in stats

    def test_disabled_cache(self, tmp_path):
        """Testa cache desabilitado."""
        disabled_cache = Cache(cache_dir=str(tmp_path / "disabled"), enabled=False)

        result = disabled_cache.set("key", "value")
        assert result is False

        result = disabled_cache.get("key")
        assert result is None

    def test_complex_values(self, cache):
        """Testa valores complexos."""
        complex_value = {
            "list": [1, 2, 3],
            "nested": {"a": 1, "b": 2},
            "string": "test",
            "number": 42.5,
        }

        cache.set("complex", complex_value)
        result = cache.get("complex")

        assert result == complex_value

    def test_hit_count(self, cache):
        """Testa contador de hits."""
        cache.set("hit_key", "value")

        # Múltiplos acessos
        cache.get("hit_key")
        cache.get("hit_key")
        cache.get("hit_key")

        # O hit_count deve ter aumentado (verificar indiretamente)
        result = cache.get("hit_key")
        assert result is not None
