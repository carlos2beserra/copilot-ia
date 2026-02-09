# =============================================================================
# Copilot-IA - Architecture Copilot
# =============================================================================
"""
Copiloto especializado em arquitetura de software.

Este copiloto orienta decisões arquiteturais:
- Análise de estrutura de projetos
- Recomendação de design patterns
- Avaliação de escalabilidade
- Sugestões de organização de código
"""

from enum import Enum
from typing import Any

from src.agents.base import AgentResponse, BaseCopilotAgent, ModelConfig
from src.tools.code_analysis import CodeAnalysisTool
from src.tools.file_operations import FileOperationsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class ArchitecturePattern(str, Enum):
    """Padrões arquiteturais."""

    MVC = "mvc"
    MVVM = "mvvm"
    CLEAN = "clean_architecture"
    HEXAGONAL = "hexagonal"
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    EVENT_DRIVEN = "event_driven"
    CQRS = "cqrs"
    SERVERLESS = "serverless"


class DesignPattern(str, Enum):
    """Design patterns."""

    # Creational
    SINGLETON = "singleton"
    FACTORY = "factory"
    ABSTRACT_FACTORY = "abstract_factory"
    BUILDER = "builder"
    PROTOTYPE = "prototype"

    # Structural
    ADAPTER = "adapter"
    BRIDGE = "bridge"
    COMPOSITE = "composite"
    DECORATOR = "decorator"
    FACADE = "facade"
    PROXY = "proxy"

    # Behavioral
    STRATEGY = "strategy"
    OBSERVER = "observer"
    COMMAND = "command"
    STATE = "state"
    TEMPLATE_METHOD = "template_method"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    MEDIATOR = "mediator"


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class ArchitectureCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em arquitetura de software.

    Orienta decisões arquiteturais, sugere design patterns e
    avalia a estrutura de projetos.

    Example:
        >>> arch = ArchitectureCopilot()
        >>>
        >>> # Analisar estrutura
        >>> result = arch.analyze_structure(file_structure)
        >>>
        >>> # Sugerir arquitetura
        >>> result = arch.suggest_architecture(requirements)
    """

    INSTRUCTIONS = """
    Você é um arquiteto de software experiente.
    
    ## Sua Missão
    
    Orientar desenvolvedores em decisões arquiteturais que resultem em
    sistemas escaláveis, manuteníveis e bem estruturados.
    
    ## Áreas de Expertise
    
    1. **Arquitetura de Software**
       - Clean Architecture
       - Hexagonal Architecture
       - Microservices vs Monolith
       - Event-Driven Architecture
       - CQRS e Event Sourcing
    
    2. **Design Patterns**
       - Creational: Factory, Singleton, Builder
       - Structural: Adapter, Facade, Decorator
       - Behavioral: Strategy, Observer, Command
    
    3. **Princípios de Design**
       - SOLID
       - DRY (Don't Repeat Yourself)
       - KISS (Keep It Simple)
       - YAGNI (You Ain't Gonna Need It)
       - Separation of Concerns
    
    4. **Qualidade**
       - Coesão e Acoplamento
       - Testabilidade
       - Escalabilidade
       - Manutenibilidade
    
    ## Abordagem
    
    1. Entender o contexto e requisitos
    2. Identificar trade-offs
    3. Sugerir opções com prós e contras
    4. Recomendar a melhor abordagem
    5. Fornecer exemplos práticos
    
    ## Formato
    
    Use diagramas (ASCII ou Mermaid) quando útil.
    Sempre explique os trade-offs das decisões.
    """

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o Architecture Copilot.

        Args:
            model_config: Configurações do modelo
        """
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.4,
                max_tokens=4096,
            )

        tools = [
            CodeAnalysisTool(),
            FileOperationsTool(),
        ]

        super().__init__(
            name="Architecture Advisor",
            description="Orienta decisões arquiteturais e design patterns",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e fornece consultoria arquitetural.

        Args:
            input_data: Informações sobre o projeto

        Returns:
            AgentResponse com análise/recomendações
        """
        if isinstance(input_data, dict):
            structure = input_data.get("structure", "")
            requirements = input_data.get("requirements", "")
            message = input_data.get("message", "")

            if message:
                return self.run(message)
            elif structure:
                return self.analyze_structure(structure)
            elif requirements:
                return self.suggest_architecture(requirements)

        return self.run(str(input_data))

    def analyze_structure(
        self, file_structure: str, code_samples: dict[str, str] | None = None
    ) -> AgentResponse:
        """
        Analisa a estrutura de um projeto.

        Args:
            file_structure: Estrutura de diretórios/arquivos
            code_samples: Amostras de código dos principais arquivos

        Returns:
            AgentResponse com análise da arquitetura
        """
        code_str = ""
        if code_samples:
            code_str = "\n\n**Amostras de Código:**\n"
            for path, code in code_samples.items():
                code_str += f"\n`{path}`:\n```\n{code[:500]}...\n```\n"

        prompt = f"""
        Analise a arquitetura do projeto com base na estrutura:
        
        ```
        {file_structure}
        ```
        {code_str}
        
        Avalie:
        1. **Organização Geral**: A estrutura faz sentido?
        2. **Separação de Responsabilidades**: O código está bem organizado?
        3. **Padrões Identificados**: Quais patterns estão sendo usados?
        4. **Pontos Fortes**: O que está bem feito?
        5. **Pontos de Melhoria**: O que pode ser melhorado?
        6. **Recomendações**: Sugestões específicas de mudanças
        """

        return self.run(prompt)

    def suggest_architecture(
        self,
        requirements: str,
        constraints: str | None = None,
        tech_stack: list[str] | None = None,
    ) -> AgentResponse:
        """
        Sugere uma arquitetura para um novo projeto.

        Args:
            requirements: Requisitos do projeto
            constraints: Restrições (tempo, equipe, orçamento)
            tech_stack: Stack tecnológica preferida

        Returns:
            AgentResponse com proposta de arquitetura
        """
        constraints_str = f"\n**Restrições:** {constraints}" if constraints else ""
        tech_str = f"\n**Tech Stack:** {', '.join(tech_stack)}" if tech_stack else ""

        prompt = f"""
        Sugira uma arquitetura para um projeto com os seguintes requisitos:
        
        **Requisitos:**
        {requirements}
        {constraints_str}
        {tech_str}
        
        Forneça:
        
        ## 1. Arquitetura Recomendada
        - Padrão arquitetural escolhido e por quê
        - Diagrama da arquitetura (Mermaid)
        
        ## 2. Componentes Principais
        - Lista de componentes/serviços
        - Responsabilidades de cada um
        
        ## 3. Estrutura de Diretórios
        ```
        projeto/
        ├── ...
        ```
        
        ## 4. Design Patterns Recomendados
        - Quais patterns usar e onde
        
        ## 5. Trade-offs
        - Prós e contras da arquitetura escolhida
        
        ## 6. Alternativas Consideradas
        - Outras opções e por que não foram escolhidas
        """

        return self.run(prompt)

    def evaluate_decision(
        self, decision: str, context: str, alternatives: list[str] | None = None
    ) -> AgentResponse:
        """
        Avalia uma decisão arquitetural.

        Args:
            decision: Decisão a ser avaliada
            context: Contexto da decisão
            alternatives: Alternativas consideradas

        Returns:
            AgentResponse com avaliação
        """
        alts_str = ""
        if alternatives:
            alts_str = "\n**Alternativas Consideradas:**\n" + "\n".join(
                f"- {a}" for a in alternatives
            )

        prompt = f"""
        Avalie a seguinte decisão arquitetural:
        
        **Decisão:** {decision}
        
        **Contexto:** {context}
        {alts_str}
        
        Forneça:
        
        ## Análise da Decisão
        
        ### Prós
        - ...
        
        ### Contras
        - ...
        
        ### Riscos
        - ...
        
        ### Impacto
        - Curto prazo: ...
        - Longo prazo: ...
        
        ### Recomendação
        A decisão é boa? Deve ser mantida ou reconsiderada?
        """

        return self.run(prompt)

    def suggest_pattern(
        self, problem: str, code: str | None = None, language: str = "python"
    ) -> AgentResponse:
        """
        Sugere design patterns para um problema.

        Args:
            problem: Descrição do problema
            code: Código atual (opcional)
            language: Linguagem de programação

        Returns:
            AgentResponse com patterns sugeridos
        """
        code_str = ""
        if code:
            code_str = f"""
            
            **Código Atual:**
            ```{language}
            {code}
            ```
            """

        prompt = f"""
        Sugira design patterns para resolver o seguinte problema:
        
        **Problema:**
        {problem}
        {code_str}
        
        Para cada pattern sugerido:
        
        1. **Nome do Pattern**: Ex: Strategy
        2. **Por que é apropriado**: Como resolve o problema
        3. **Implementação**: Exemplo de código
        4. **Diagrama**: Estrutura em Mermaid
        5. **Trade-offs**: Prós e contras
        """

        return self.run(prompt)

    def review_dependencies(
        self, dependencies: dict[str, str], project_type: str = "web"
    ) -> AgentResponse:
        """
        Analisa as dependências de um projeto.

        Args:
            dependencies: Dicionário de dependências e versões
            project_type: Tipo de projeto

        Returns:
            AgentResponse com análise das dependências
        """
        deps_str = "\n".join(f"- {name}: {version}" for name, version in dependencies.items())

        prompt = f"""
        Analise as dependências deste projeto {project_type}:
        
        **Dependências:**
        {deps_str}
        
        Avalie:
        1. **Redundâncias**: Dependências que fazem coisas similares
        2. **Riscos de Segurança**: Dependências com vulnerabilidades conhecidas
        3. **Manutenção**: Dependências abandonadas ou pouco mantidas
        4. **Peso**: Dependências muito pesadas para o que fazem
        5. **Alternativas**: Sugestões de substituição
        6. **Faltando**: Dependências que poderiam ajudar
        """

        return self.run(prompt)

    def design_api(self, requirements: str, style: str = "REST") -> AgentResponse:
        """
        Projeta uma API baseada em requisitos.

        Args:
            requirements: Requisitos da API
            style: Estilo da API (REST, GraphQL, gRPC)

        Returns:
            AgentResponse com design da API
        """
        prompt = f"""
        Projete uma API {style} baseada nos seguintes requisitos:
        
        **Requisitos:**
        {requirements}
        
        Forneça:
        
        ## Design da API
        
        ### Recursos/Endpoints
        | Método | Endpoint | Descrição |
        |--------|----------|-----------|
        
        ### Modelos de Dados
        ```json
        // Schemas
        ```
        
        ### Autenticação/Autorização
        - Método de auth recomendado
        
        ### Versionamento
        - Estratégia de versionamento
        
        ### Boas Práticas
        - Paginação
        - Filtros
        - Tratamento de erros
        
        ### Exemplo de Especificação
        ```yaml
        # OpenAPI spec (parcial)
        ```
        """

        return self.run(prompt)

    def plan_migration(
        self, current_state: str, target_state: str, constraints: str | None = None
    ) -> AgentResponse:
        """
        Planeja uma migração arquitetural.

        Args:
            current_state: Estado atual da arquitetura
            target_state: Estado desejado
            constraints: Restrições (downtime, equipe, etc.)

        Returns:
            AgentResponse com plano de migração
        """
        constraints_str = f"\n**Restrições:** {constraints}" if constraints else ""

        prompt = f"""
        Planeje uma migração arquitetural:
        
        **Estado Atual:**
        {current_state}
        
        **Estado Desejado:**
        {target_state}
        {constraints_str}
        
        Forneça:
        
        ## Plano de Migração
        
        ### Análise de Gap
        - O que precisa mudar
        
        ### Fases da Migração
        1. Fase 1: ...
        2. Fase 2: ...
        
        ### Riscos e Mitigações
        | Risco | Probabilidade | Impacto | Mitigação |
        
        ### Estratégia de Rollback
        - Como reverter se necessário
        
        ### Testes Necessários
        - O que validar em cada fase
        
        ### Timeline Estimado
        - Estimativa de tempo para cada fase
        """

        return self.run(prompt)
