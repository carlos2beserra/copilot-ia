# =============================================================================
# Copilot-IA - Debug Copilot
# =============================================================================
"""
Copiloto especializado em depuração de código.

Este copiloto auxilia na identificação e resolução de bugs:
- Análise de mensagens de erro
- Interpretação de stack traces
- Identificação de causa raiz
- Sugestão de correções
"""

from typing import Any

from pydantic import BaseModel, Field

from src.agents.base import AgentResponse, BaseCopilotAgent, ModelConfig
from src.tools.code_analysis import CodeAnalysisTool
from src.tools.file_operations import FileOperationsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class ErrorInfo(BaseModel):
    """Informações sobre um erro."""

    message: str = Field(description="Mensagem de erro")
    stack_trace: str | None = Field(default=None, description="Stack trace")
    file: str | None = Field(default=None, description="Arquivo onde ocorreu")
    line: int | None = Field(default=None, description="Linha do erro")
    context: str | None = Field(default=None, description="Contexto adicional")


class DebugResult(BaseModel):
    """Resultado da análise de debug."""

    root_cause: str = Field(description="Causa raiz identificada")
    explanation: str = Field(description="Explicação do problema")
    solution: str = Field(description="Solução proposta")
    prevention: str | None = Field(default=None, description="Como prevenir")
    code_fix: str | None = Field(default=None, description="Código corrigido")


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class DebugCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em depuração.

    Ajuda a identificar e resolver bugs através da análise de
    erros, stack traces e comportamento inesperado.

    Example:
        >>> debug_copilot = DebugCopilot()
        >>>
        >>> # Analisar erro
        >>> result = debug_copilot.analyze_error(error_message, stack_trace)
        >>>
        >>> # Depurar comportamento
        >>> result = debug_copilot.debug_behavior(expected, actual, code)
    """

    INSTRUCTIONS = """
    Você é um especialista em depuração de software.
    
    ## Sua Missão
    
    Ajudar desenvolvedores a identificar e resolver bugs de forma eficiente.
    
    ## Processo de Debug
    
    1. **Entender o Problema**
       - Analisar mensagem de erro
       - Interpretar stack trace
       - Entender comportamento esperado vs atual
    
    2. **Identificar Causa Raiz**
       - Não tratar apenas sintomas
       - Encontrar a origem real do problema
       - Considerar contexto e dependências
    
    3. **Propor Solução**
       - Correção específica e direcionada
       - Código corrigido quando possível
       - Explicar por que funciona
    
    4. **Prevenir Recorrência**
       - Sugerir testes para o caso
       - Recomendar boas práticas
       - Identificar padrões problemáticos
    
    ## Tipos de Erros Comuns
    
    - **Runtime Errors**: NullPointer, TypeError, IndexError
    - **Logic Errors**: Comportamento incorreto sem crash
    - **Race Conditions**: Problemas de concorrência
    - **Memory Issues**: Leaks, buffer overflow
    - **Integration Errors**: Problemas entre componentes
    
    ## Formato da Resposta
    
    1. **Causa Raiz**: Identificação clara do problema
    2. **Explicação**: Por que o erro ocorre
    3. **Solução**: Código corrigido com explicação
    4. **Prevenção**: Como evitar no futuro
    """

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o Debug Copilot.

        Args:
            model_config: Configurações do modelo
        """
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.2,  # Baixa para análises precisas
                max_tokens=4096,
            )

        tools = [
            CodeAnalysisTool(),
            FileOperationsTool(),
        ]

        super().__init__(
            name="Debug Assistant",
            description="Auxilia na identificação e resolução de bugs",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e realiza debugging.

        Args:
            input_data: Informações de erro ou código

        Returns:
            AgentResponse com análise de debug
        """
        if isinstance(input_data, dict):
            error_message = input_data.get("error", input_data.get("message", ""))
            stack_trace = input_data.get("stack_trace", "")
            code = input_data.get("code", "")

            return self.analyze_error(
                error_message=error_message, stack_trace=stack_trace, code=code
            )

        return self.run(f"Analise e ajude a resolver: {input_data}")

    def analyze_error(
        self,
        error_message: str,
        stack_trace: str | None = None,
        code: str | None = None,
        language: str = "python",
    ) -> AgentResponse:
        """
        Analisa um erro e sugere solução.

        Args:
            error_message: Mensagem de erro
            stack_trace: Stack trace completo
            code: Código relevante
            language: Linguagem de programação

        Returns:
            AgentResponse com análise e solução
        """
        parts = [
            "Analise o seguinte erro e ajude a resolvê-lo:",
            "",
            "**Mensagem de Erro:**",
            "```",
            error_message,
            "```",
        ]

        if stack_trace:
            parts.extend(
                [
                    "",
                    "**Stack Trace:**",
                    "```",
                    stack_trace,
                    "```",
                ]
            )

        if code:
            parts.extend(
                [
                    "",
                    f"**Código Relevante ({language}):**",
                    f"```{language}",
                    code,
                    "```",
                ]
            )

        parts.extend(
            [
                "",
                "Forneça:",
                "1. **Causa Raiz**: O que está causando este erro?",
                "2. **Explicação**: Por que isso acontece?",
                "3. **Solução**: Como corrigir (com código se possível)?",
                "4. **Prevenção**: Como evitar este erro no futuro?",
            ]
        )

        prompt = "\n".join(parts)
        return self.run(prompt)

    def debug_behavior(
        self, expected: str, actual: str, code: str, language: str = "python"
    ) -> AgentResponse:
        """
        Depura um comportamento inesperado.

        Args:
            expected: Comportamento esperado
            actual: Comportamento atual
            code: Código que apresenta o problema
            language: Linguagem de programação

        Returns:
            AgentResponse com análise
        """
        prompt = f"""
        O código não está se comportando como esperado.
        
        **Comportamento Esperado:**
        {expected}
        
        **Comportamento Atual:**
        {actual}
        
        **Código:**
        ```{language}
        {code}
        ```
        
        Por favor:
        1. Identifique por que o comportamento difere do esperado
        2. Explique a lógica que está causando o problema
        3. Forneça o código corrigido
        4. Sugira como testar a correção
        """

        return self.run(prompt)

    def explain_error(self, error_message: str) -> AgentResponse:
        """
        Explica uma mensagem de erro.

        Args:
            error_message: Mensagem de erro a ser explicada

        Returns:
            AgentResponse com explicação
        """
        prompt = f"""
        Explique a seguinte mensagem de erro para um desenvolvedor:
        
        ```
        {error_message}
        ```
        
        Forneça:
        1. O que este erro significa
        2. Causas comuns
        3. Como investigar
        4. Exemplos de correção
        """

        return self.run(prompt)

    def explain_code(
        self, code: str, language: str = "python", level: str = "intermediate"
    ) -> AgentResponse:
        """
        Explica o que um código faz.

        Args:
            code: Código a ser explicado
            language: Linguagem de programação
            level: Nível de detalhe (beginner, intermediate, advanced)

        Returns:
            AgentResponse com explicação
        """
        prompt = f"""
        Explique o que o seguinte código faz (nível: {level}):
        
        ```{language}
        {code}
        ```
        
        Inclua:
        1. Propósito geral do código
        2. Explicação passo a passo
        3. Entradas e saídas
        4. Possíveis problemas ou melhorias
        """

        return self.run(prompt)

    def trace_execution(self, code: str, inputs: dict, language: str = "python") -> AgentResponse:
        """
        Simula a execução do código com os inputs dados.

        Args:
            code: Código a ser rastreado
            inputs: Valores de entrada
            language: Linguagem de programação

        Returns:
            AgentResponse com trace de execução
        """
        inputs_str = "\n".join(f"- {k} = {v}" for k, v in inputs.items())

        prompt = f"""
        Simule a execução do seguinte código com os inputs fornecidos:
        
        **Código:**
        ```{language}
        {code}
        ```
        
        **Inputs:**
        {inputs_str}
        
        Forneça um trace detalhado:
        1. Valor de cada variável em cada passo
        2. Resultado de cada expressão
        3. Fluxo de controle (condicionais, loops)
        4. Resultado final
        
        Se encontrar um erro durante a simulação, explique onde e por quê.
        """

        return self.run(prompt)

    def analyze_stack_trace(self, stack_trace: str, language: str = "python") -> AgentResponse:
        """
        Analisa um stack trace em detalhes.

        Args:
            stack_trace: Stack trace completo
            language: Linguagem de programação

        Returns:
            AgentResponse com análise detalhada
        """
        prompt = f"""
        Analise o seguinte stack trace ({language}):
        
        ```
        {stack_trace}
        ```
        
        Forneça:
        1. **Erro Principal**: Qual exceção/erro ocorreu?
        2. **Localização**: Arquivo e linha exata
        3. **Call Stack**: Sequência de chamadas que levaram ao erro
        4. **Contexto**: O que provavelmente estava acontecendo
        5. **Próximos Passos**: O que investigar primeiro
        """

        return self.run(prompt)

    def suggest_debug_steps(
        self, problem_description: str, code: str | None = None
    ) -> AgentResponse:
        """
        Sugere passos de debug para um problema.

        Args:
            problem_description: Descrição do problema
            code: Código relacionado (opcional)

        Returns:
            AgentResponse com passos de debug
        """
        code_section = ""
        if code:
            code_section = f"""
            
            **Código Relacionado:**
            ```
            {code}
            ```
            """

        prompt = f"""
        Sugira passos de debug para o seguinte problema:
        
        **Problema:**
        {problem_description}
        {code_section}
        
        Forneça um plano de debug:
        1. **Hipóteses**: Possíveis causas
        2. **Verificações**: O que checar primeiro
        3. **Ferramentas**: Ferramentas/comandos úteis
        4. **Pontos de Debug**: Onde colocar breakpoints/logs
        5. **Testes**: Como isolar o problema
        """

        return self.run(prompt)

    def fix_code(
        self, broken_code: str, error_or_issue: str, language: str = "python"
    ) -> AgentResponse:
        """
        Corrige código com problemas.

        Args:
            broken_code: Código com problema
            error_or_issue: Descrição do erro ou problema
            language: Linguagem de programação

        Returns:
            AgentResponse com código corrigido
        """
        prompt = f"""
        Corrija o seguinte código:
        
        **Código com Problema:**
        ```{language}
        {broken_code}
        ```
        
        **Erro/Problema:**
        {error_or_issue}
        
        Forneça:
        1. **Código Corrigido** (completo e funcional)
        2. **Mudanças Feitas** (lista das alterações)
        3. **Explicação** (por que a correção funciona)
        """

        return self.run(prompt)
