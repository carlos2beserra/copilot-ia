# =============================================================================
# Copilot-IA - Agente Base
# =============================================================================
"""
Classe base abstrata para todos os copilotos de desenvolvimento.

Este módulo define a interface comum que todos os agentes especializados
devem implementar, utilizando o framework Agno.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Configurações
# -----------------------------------------------------------------------------
class ModelConfig(BaseSettings):
    """Configurações do modelo LLM."""

    provider: str = Field(default="openai", description="Provider do modelo")
    name: str = Field(default="gpt-4o", description="Nome do modelo")
    temperature: float = Field(default=0.3, description="Temperatura de geração")
    max_tokens: int = Field(default=4096, description="Máximo de tokens")

    class Config:
        env_prefix = "DEFAULT_"


class AgentResponse(BaseModel):
    """Resposta padronizada dos agentes."""

    success: bool = Field(description="Se a operação foi bem sucedida")
    content: str = Field(description="Conteúdo da resposta")
    metadata: dict = Field(default_factory=dict, description="Metadados adicionais")
    tokens_used: int | None = Field(default=None, description="Tokens utilizados")
    model: str | None = Field(default=None, description="Modelo utilizado")


# -----------------------------------------------------------------------------
# Agente Base
# -----------------------------------------------------------------------------
class BaseCopilotAgent(ABC):
    """
    Classe base abstrata para todos os copilotos.

    Esta classe define a interface comum e funcionalidades compartilhadas
    entre todos os agentes especializados do sistema.

    Attributes:
        name: Nome do copiloto
        description: Descrição do propósito do copiloto
        agent: Instância do agente Agno
        config: Configurações do agente

    Example:
        >>> class MyCopilot(BaseCopilotAgent):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="My Copilot",
        ...             description="Meu copiloto personalizado"
        ...         )
        ...
        ...     def process(self, input_data):
        ...         return self.run(f"Processe: {input_data}")
    """

    def __init__(
        self,
        name: str,
        description: str,
        instructions: str | None = None,
        model_config: ModelConfig | None = None,
        tools: list | None = None,
    ):
        """
        Inicializa o agente base.

        Args:
            name: Nome identificador do copiloto
            description: Descrição do propósito e capacidades
            instructions: Instruções do sistema para o agente
            model_config: Configurações do modelo LLM
            tools: Lista de ferramentas disponíveis para o agente
        """
        self.name = name
        self.description = description
        self.instructions = instructions or self._default_instructions()
        self.model_config = model_config or ModelConfig()
        self.tools = tools or []

        # Carregar configurações do arquivo YAML
        self._load_config()

        # Inicializar o agente Agno
        self.agent = self._create_agent()

        logger.info(
            f"Copiloto '{self.name}' inicializado com {self.model_config.provider}/{self.model_config.name}"
        )

    def _load_config(self) -> None:
        """Carrega configurações do arquivo YAML."""
        config_path = Path(__file__).parent.parent.parent / "config" / "agents_config.yaml"

        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self.yaml_config = yaml.safe_load(f)
        else:
            self.yaml_config = {}
            logger.warning(f"Arquivo de configuração não encontrado: {config_path}")

    def _get_model(self) -> Any:
        """
        Retorna a instância do modelo LLM baseado na configuração.

        Returns:
            Instância do modelo (OpenAIChat, Claude, Groq, etc.)
        """
        provider = self.model_config.provider.lower()

        if provider == "openai":
            return OpenAIChat(
                id=self.model_config.name,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
            )
        elif provider == "anthropic":
            return Claude(
                id=self.model_config.name,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
            )
        elif provider == "groq":
            return Groq(
                id=self.model_config.name,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
            )
        else:
            raise ValueError(f"Provider não suportado: {provider}")

    def _create_agent(self) -> Agent:
        """
        Cria e configura a instância do agente Agno.

        Returns:
            Instância configurada do Agent
        """
        # Parâmetros base do Agent
        agent_kwargs = {
            "name": self.name,
            "description": self.description,
            "model": self._get_model(),
            "instructions": self.instructions,
        }

        # Adicionar tools se disponíveis
        if self.tools:
            agent_kwargs["tools"] = self.tools

        return Agent(**agent_kwargs)

    def _default_instructions(self) -> str:
        """
        Retorna as instruções padrão do agente.

        Subclasses devem sobrescrever este método para fornecer
        instruções específicas.

        Returns:
            String com instruções do sistema
        """
        return f"""
        Você é {self.name}, um assistente de desenvolvimento especializado.
        
        {self.description}
        
        Sempre forneça respostas claras, detalhadas e acionáveis.
        Use Markdown para formatar suas respostas.
        """

    def run(self, prompt: str, **kwargs) -> AgentResponse:
        """
        Executa o agente com o prompt fornecido.

        Args:
            prompt: Prompt de entrada para o agente
            **kwargs: Argumentos adicionais

        Returns:
            AgentResponse com o resultado da execução
        """
        try:
            logger.debug(f"[{self.name}] Executando com prompt: {prompt[:100]}...")

            response = self.agent.run(prompt, **kwargs)

            # Extrair conteúdo da resposta
            content = response.content if hasattr(response, "content") else str(response)

            return AgentResponse(
                success=True,
                content=content,
                metadata={
                    "agent": self.name,
                    "model": self.model_config.name,
                },
                model=self.model_config.name,
            )

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução: {e}")
            return AgentResponse(
                success=False,
                content=f"Erro ao processar: {str(e)}",
                metadata={"error": str(e)},
            )

    async def arun(self, prompt: str, **kwargs) -> AgentResponse:
        """
        Executa o agente de forma assíncrona.

        Args:
            prompt: Prompt de entrada para o agente
            **kwargs: Argumentos adicionais

        Returns:
            AgentResponse com o resultado da execução
        """
        try:
            logger.debug(f"[{self.name}] Executando async com prompt: {prompt[:100]}...")

            response = await self.agent.arun(prompt, **kwargs)
            content = response.content if hasattr(response, "content") else str(response)

            return AgentResponse(
                success=True,
                content=content,
                metadata={"agent": self.name},
                model=self.model_config.name,
            )

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução async: {e}")
            return AgentResponse(
                success=False,
                content=f"Erro ao processar: {str(e)}",
                metadata={"error": str(e)},
            )

    def stream(self, prompt: str, **kwargs):
        """
        Executa o agente em modo streaming.

        Args:
            prompt: Prompt de entrada
            **kwargs: Argumentos adicionais

        Yields:
            Chunks da resposta
        """
        logger.debug(f"[{self.name}] Streaming com prompt: {prompt[:100]}...")

        for chunk in self.agent.run(prompt, stream=True, **kwargs):
            yield chunk

    @abstractmethod
    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada específica do copiloto.

        Este método deve ser implementado por cada copiloto especializado
        para definir sua lógica de processamento principal.

        Args:
            input_data: Dados de entrada específicos do copiloto

        Returns:
            AgentResponse com o resultado do processamento
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', model='{self.model_config.name}')>"
