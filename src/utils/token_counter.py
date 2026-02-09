# =============================================================================
# Copilot-IA - Contador de Tokens
# =============================================================================
"""
Utilitário para contagem de tokens para diferentes modelos.
"""


import tiktoken

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TokenCounter:
    """
    Contador de tokens para modelos LLM.

    Suporta contagem de tokens para diferentes modelos
    usando tiktoken.

    Example:
        >>> counter = TokenCounter()
        >>> tokens = counter.count("Hello, world!", model="gpt-4o")
        >>> print(f"Tokens: {tokens}")
    """

    # Mapeamento de modelos para encodings
    MODEL_ENCODINGS = {
        # OpenAI
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        # Anthropic (aproximação)
        "claude-3-5-sonnet": "cl100k_base",
        "claude-3-opus": "cl100k_base",
        "claude-3-sonnet": "cl100k_base",
        "claude-3-haiku": "cl100k_base",
        # Default
        "default": "cl100k_base",
    }

    # Preços por 1M tokens (input/output) em USD
    MODEL_PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, default_model: str = "gpt-4o"):
        """
        Inicializa o contador.

        Args:
            default_model: Modelo padrão para contagem
        """
        self.default_model = default_model
        self._encoders: dict[str, tiktoken.Encoding] = {}

    def _get_encoder(self, model: str) -> tiktoken.Encoding:
        """Obtém o encoder para um modelo."""
        encoding_name = self.MODEL_ENCODINGS.get(model, self.MODEL_ENCODINGS["default"])

        if encoding_name not in self._encoders:
            try:
                self._encoders[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Erro ao obter encoding {encoding_name}: {e}")
                self._encoders[encoding_name] = tiktoken.get_encoding("cl100k_base")

        return self._encoders[encoding_name]

    def count(self, text: str, model: str | None = None) -> int:
        """
        Conta tokens em um texto.

        Args:
            text: Texto para contar tokens
            model: Modelo para usar encoding apropriado

        Returns:
            Número de tokens
        """
        model = model or self.default_model
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))

    def count_messages(self, messages: list[dict], model: str | None = None) -> int:
        """
        Conta tokens em uma lista de mensagens (chat format).

        Args:
            messages: Lista de mensagens {"role": str, "content": str}
            model: Modelo para encoding

        Returns:
            Total de tokens
        """
        model = model or self.default_model

        total = 0

        # Overhead por mensagem (aproximado)
        tokens_per_message = 4

        for message in messages:
            total += tokens_per_message
            total += self.count(message.get("role", ""), model)
            total += self.count(message.get("content", ""), model)

        # Overhead de formatação
        total += 3

        return total

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, model: str | None = None
    ) -> dict:
        """
        Estima o custo em USD.

        Args:
            input_tokens: Tokens de entrada
            output_tokens: Tokens de saída
            model: Modelo usado

        Returns:
            Dicionário com custos
        """
        model = model or self.default_model

        # Encontrar preço do modelo
        pricing = self.MODEL_PRICING.get(model)

        if not pricing:
            # Tentar encontrar modelo similar
            for key in self.MODEL_PRICING:
                if key in model:
                    pricing = self.MODEL_PRICING[key]
                    break

        if not pricing:
            return {
                "input_cost": 0,
                "output_cost": 0,
                "total_cost": 0,
                "model": model,
                "warning": "Preço não disponível para este modelo",
            }

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "model": model,
            "currency": "USD",
        }

    def truncate_to_limit(self, text: str, max_tokens: int, model: str | None = None) -> str:
        """
        Trunca texto para não exceder limite de tokens.

        Args:
            text: Texto para truncar
            max_tokens: Limite de tokens
            model: Modelo para encoding

        Returns:
            Texto truncado
        """
        model = model or self.default_model
        encoder = self._get_encoder(model)

        tokens = encoder.encode(text)

        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        return encoder.decode(truncated_tokens)

    def split_into_chunks(
        self, text: str, chunk_size: int, overlap: int = 0, model: str | None = None
    ) -> list[str]:
        """
        Divide texto em chunks por tokens.

        Args:
            text: Texto para dividir
            chunk_size: Tamanho de cada chunk em tokens
            overlap: Sobreposição entre chunks
            model: Modelo para encoding

        Returns:
            Lista de chunks
        """
        model = model or self.default_model
        encoder = self._get_encoder(model)

        tokens = encoder.encode(text)
        chunks = []

        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(encoder.decode(chunk_tokens))
            start = end - overlap if overlap > 0 else end

        return chunks

    def get_model_info(self, model: str) -> dict:
        """
        Retorna informações sobre um modelo.

        Args:
            model: Nome do modelo

        Returns:
            Dicionário com informações
        """
        pricing = self.MODEL_PRICING.get(model, {})
        encoding = self.MODEL_ENCODINGS.get(model, "cl100k_base")

        return {
            "model": model,
            "encoding": encoding,
            "input_price_per_1m": pricing.get("input", "N/A"),
            "output_price_per_1m": pricing.get("output", "N/A"),
        }
