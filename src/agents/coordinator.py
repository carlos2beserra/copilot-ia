# =============================================================================
# Copilot-IA - Coordenador Multiagente
# =============================================================================
"""
Coordenador responsável por orquestrar múltiplos copilotos para tarefas complexas.

O coordenador analisa a solicitação do usuário, determina quais copilotos são
necessários e coordena a execução entre eles.
"""

from enum import Enum

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from pydantic import BaseModel, Field

from src.agents.base import BaseCopilotAgent, ModelConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Enums e Modelos
# -----------------------------------------------------------------------------
class CopilotType(str, Enum):
    """Tipos de copilotos disponíveis."""

    CODE_REVIEWER = "code_reviewer"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEBUG = "debug"
    REFACTORING = "refactoring"
    ARCHITECTURE = "architecture"
    SECURITY = "security"


class TaskIntent(str, Enum):
    """Intenções de tarefa detectáveis."""

    REVIEW = "review"
    DOCUMENT = "document"
    TEST = "test"
    DEBUG = "debug"
    REFACTOR = "refactor"
    ANALYZE_ARCHITECTURE = "architecture"
    SECURITY_SCAN = "security"
    FULL_ANALYSIS = "full_analysis"


class CoordinatorRequest(BaseModel):
    """Solicitação ao coordenador."""

    message: str = Field(description="Mensagem/solicitação do usuário")
    files: list[str] = Field(default_factory=list, description="Arquivos envolvidos")
    context: dict | None = Field(default=None, description="Contexto adicional")
    preferred_copilots: list[CopilotType] | None = Field(
        default=None, description="Copilotos específicos a serem usados"
    )


class CoordinatorResponse(BaseModel):
    """Resposta consolidada do coordenador."""

    success: bool
    summary: str = Field(description="Resumo executivo")
    details: dict = Field(description="Detalhes por copiloto")
    recommendations: list[str] = Field(default_factory=list, description="Recomendações")
    copilots_used: list[str] = Field(description="Copilotos utilizados")


# -----------------------------------------------------------------------------
# Coordenador
# -----------------------------------------------------------------------------
class CopilotCoordinator:
    """
    Coordenador central que orquestra múltiplos copilotos.

    O coordenador analisa solicitações, determina a melhor combinação de
    copilotos e consolida os resultados em uma resposta unificada.

    Attributes:
        copilots: Dicionário de copilotos registrados
        team: Time Agno para coordenação multiagente

    Example:
        >>> coordinator = CopilotCoordinator()
        >>> coordinator.register_copilot(CodeReviewerCopilot())
        >>> coordinator.register_copilot(SecurityCopilot())
        >>>
        >>> response = coordinator.process(CoordinatorRequest(
        ...     message="Analise este código para bugs e segurança",
        ...     files=["src/main.py"]
        ... ))
    """

    # Mapeamento de intenções para copilotos
    INTENT_COPILOT_MAP = {
        TaskIntent.REVIEW: [CopilotType.CODE_REVIEWER],
        TaskIntent.DOCUMENT: [CopilotType.DOCUMENTATION],
        TaskIntent.TEST: [CopilotType.TESTING],
        TaskIntent.DEBUG: [CopilotType.DEBUG],
        TaskIntent.REFACTOR: [CopilotType.REFACTORING],
        TaskIntent.ANALYZE_ARCHITECTURE: [CopilotType.ARCHITECTURE],
        TaskIntent.SECURITY_SCAN: [CopilotType.SECURITY],
        TaskIntent.FULL_ANALYSIS: [
            CopilotType.CODE_REVIEWER,
            CopilotType.SECURITY,
            CopilotType.ARCHITECTURE,
        ],
    }

    # Palavras-chave para detecção de intenção
    INTENT_KEYWORDS = {
        TaskIntent.REVIEW: ["review", "revisar", "analisar código", "code review", "verificar"],
        TaskIntent.DOCUMENT: ["document", "documentar", "docstring", "readme", "docs"],
        TaskIntent.TEST: ["test", "testar", "teste", "unit test", "testes"],
        TaskIntent.DEBUG: ["debug", "bug", "erro", "error", "fix", "corrigir", "problema"],
        TaskIntent.REFACTOR: ["refactor", "refatorar", "melhorar", "clean", "limpar"],
        TaskIntent.ANALYZE_ARCHITECTURE: ["architecture", "arquitetura", "design", "estrutura"],
        TaskIntent.SECURITY_SCAN: ["security", "segurança", "vulnerab", "owasp", "injection"],
        TaskIntent.FULL_ANALYSIS: ["full", "completo", "completa", "tudo", "all"],
    }

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o coordenador.

        Args:
            model_config: Configurações do modelo para o agente coordenador
        """
        self.model_config = model_config or ModelConfig()
        self.copilots: dict[CopilotType, BaseCopilotAgent] = {}

        # Criar agente coordenador
        self.coordinator_agent = self._create_coordinator_agent()
        self.team: Team | None = None

        logger.info("CopilotCoordinator inicializado")

    def _create_coordinator_agent(self) -> Agent:
        """Cria o agente coordenador."""
        return Agent(
            name="Development Copilot Coordinator",
            description="Coordena múltiplos copilotos especializados para tarefas de desenvolvimento",
            model=OpenAIChat(
                id=self.model_config.name,
                temperature=self.model_config.temperature,
            ),
            instructions="""
            Você é o coordenador central dos copilotos de desenvolvimento.
            
            Seu papel é:
            1. Analisar a solicitação do usuário
            2. Identificar a intenção principal
            3. Determinar quais copilotos especializados são necessários
            4. Coordenar a execução e consolidar resultados
            
            Sempre forneça:
            - Resumo executivo claro
            - Detalhes organizados por área
            - Recomendações acionáveis
            """,
        )

    def register_copilot(self, copilot: BaseCopilotAgent, copilot_type: CopilotType) -> None:
        """
        Registra um copiloto no coordenador.

        Args:
            copilot: Instância do copiloto
            copilot_type: Tipo do copiloto
        """
        self.copilots[copilot_type] = copilot
        logger.info(f"Copiloto '{copilot.name}' registrado como {copilot_type.value}")

        # Atualizar time se necessário
        self._update_team()

    def _update_team(self) -> None:
        """Atualiza o time Agno com os copilotos registrados."""
        if len(self.copilots) > 0:
            agents = [copilot.agent for copilot in self.copilots.values()]
            self.team = Team(
                name="Development Copilots Team",
                agents=agents,
                mode="coordinate",
            )

    def detect_intent(self, message: str) -> list[TaskIntent]:
        """
        Detecta a intenção da solicitação do usuário.

        Args:
            message: Mensagem do usuário

        Returns:
            Lista de intenções detectadas
        """
        message_lower = message.lower()
        detected_intents = []

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    detected_intents.append(intent)
                    break

        # Se nenhuma intenção detectada, assume revisão de código
        if not detected_intents:
            detected_intents = [TaskIntent.REVIEW]

        logger.debug(f"Intenções detectadas: {detected_intents}")
        return detected_intents

    def select_copilots(self, intents: list[TaskIntent]) -> list[CopilotType]:
        """
        Seleciona os copilotos necessários baseado nas intenções.

        Args:
            intents: Lista de intenções detectadas

        Returns:
            Lista de tipos de copilotos a serem utilizados
        """
        copilot_types = set()

        for intent in intents:
            if intent in self.INTENT_COPILOT_MAP:
                copilot_types.update(self.INTENT_COPILOT_MAP[intent])

        # Filtrar apenas copilotos registrados
        available = [ct for ct in copilot_types if ct in self.copilots]

        logger.debug(f"Copilotos selecionados: {available}")
        return available

    def process(self, request: CoordinatorRequest) -> CoordinatorResponse:
        """
        Processa uma solicitação coordenando múltiplos copilotos.

        Args:
            request: Solicitação do usuário

        Returns:
            Resposta consolidada de todos os copilotos
        """
        logger.info(f"Processando solicitação: {request.message[:100]}...")

        # Detectar intenção e selecionar copilotos
        if request.preferred_copilots:
            copilot_types = request.preferred_copilots
        else:
            intents = self.detect_intent(request.message)
            copilot_types = self.select_copilots(intents)

        if not copilot_types:
            return CoordinatorResponse(
                success=False,
                summary="Nenhum copiloto disponível para esta solicitação",
                details={},
                copilots_used=[],
            )

        # Executar cada copiloto
        results = {}
        for copilot_type in copilot_types:
            if copilot_type in self.copilots:
                copilot = self.copilots[copilot_type]

                try:
                    # Preparar contexto para o copiloto
                    context = {
                        "message": request.message,
                        "files": request.files,
                        **(request.context or {}),
                    }

                    response = copilot.process(context)
                    results[copilot_type.value] = {
                        "success": response.success,
                        "content": response.content,
                        "metadata": response.metadata,
                    }

                except Exception as e:
                    logger.error(f"Erro ao executar {copilot_type.value}: {e}")
                    results[copilot_type.value] = {
                        "success": False,
                        "content": f"Erro: {str(e)}",
                        "metadata": {},
                    }

        # Consolidar resultados
        return self._consolidate_results(results, copilot_types)

    async def aprocess(self, request: CoordinatorRequest) -> CoordinatorResponse:
        """
        Processa uma solicitação de forma assíncrona.

        Args:
            request: Solicitação do usuário

        Returns:
            Resposta consolidada
        """
        import asyncio

        logger.info(f"Processando solicitação async: {request.message[:100]}...")

        if request.preferred_copilots:
            copilot_types = request.preferred_copilots
        else:
            intents = self.detect_intent(request.message)
            copilot_types = self.select_copilots(intents)

        if not copilot_types:
            return CoordinatorResponse(
                success=False,
                summary="Nenhum copiloto disponível",
                details={},
                copilots_used=[],
            )

        # Executar copilotos em paralelo
        async def run_copilot(copilot_type: CopilotType):
            copilot = self.copilots.get(copilot_type)
            if not copilot:
                return copilot_type.value, None

            try:
                context = {
                    "message": request.message,
                    "files": request.files,
                    **(request.context or {}),
                }
                response = await copilot.arun(str(context))
                return copilot_type.value, {
                    "success": response.success,
                    "content": response.content,
                }
            except Exception as e:
                return copilot_type.value, {"success": False, "content": str(e)}

        tasks = [run_copilot(ct) for ct in copilot_types]
        results_list = await asyncio.gather(*tasks)

        results = {name: result for name, result in results_list if result}

        return self._consolidate_results(results, copilot_types)

    def _consolidate_results(
        self, results: dict, copilot_types: list[CopilotType]
    ) -> CoordinatorResponse:
        """
        Consolida os resultados de múltiplos copilotos.

        Args:
            results: Resultados de cada copiloto
            copilot_types: Tipos de copilotos utilizados

        Returns:
            Resposta consolidada
        """
        # Verificar sucesso geral
        all_success = all(r.get("success", False) for r in results.values())

        # Gerar resumo
        summary_parts = []
        recommendations = []

        for copilot_name, result in results.items():
            if result.get("success"):
                summary_parts.append(f"✅ {copilot_name}: Análise concluída")
            else:
                summary_parts.append(f"❌ {copilot_name}: Falha na análise")

        summary = "## Resumo da Análise\n\n" + "\n".join(summary_parts)

        # Extrair recomendações (simplificado)
        for result in results.values():
            content = result.get("content", "")
            if "recomend" in content.lower() or "sugest" in content.lower():
                recommendations.append("Verifique as recomendações detalhadas no relatório")
                break

        return CoordinatorResponse(
            success=all_success,
            summary=summary,
            details=results,
            recommendations=recommendations,
            copilots_used=[ct.value for ct in copilot_types],
        )

    def get_available_copilots(self) -> list[str]:
        """Retorna lista de copilotos disponíveis."""
        return [ct.value for ct in self.copilots.keys()]

    def __repr__(self) -> str:
        copilots_str = ", ".join(self.get_available_copilots())
        return f"<CopilotCoordinator(copilots=[{copilots_str}])>"
