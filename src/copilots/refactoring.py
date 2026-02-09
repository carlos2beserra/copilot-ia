# =============================================================================
# Copilot-IA - Refactoring Copilot
# =============================================================================
"""
Copiloto especializado em refatoração de código.

Este copiloto sugere e aplica refatorações:
- Identificação de code smells
- Aplicação de design patterns
- Simplificação de código
- Melhoria de legibilidade
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
class CodeSmell(str, Enum):
    """Tipos de code smells."""

    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    SWITCH_STATEMENTS = "switch_statements"
    PARALLEL_INHERITANCE = "parallel_inheritance"
    LAZY_CLASS = "lazy_class"
    SPECULATIVE_GENERALITY = "speculative_generality"
    TEMPORARY_FIELD = "temporary_field"
    MESSAGE_CHAINS = "message_chains"
    MIDDLE_MAN = "middle_man"
    INAPPROPRIATE_INTIMACY = "inappropriate_intimacy"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    COMMENTS = "excessive_comments"


class RefactoringType(str, Enum):
    """Tipos de refatoração."""

    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INLINE_METHOD = "inline_method"
    RENAME = "rename"
    MOVE_METHOD = "move_method"
    REPLACE_CONDITIONAL = "replace_conditional_with_polymorphism"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    PRESERVE_WHOLE_OBJECT = "preserve_whole_object"
    REPLACE_MAGIC_NUMBER = "replace_magic_number_with_constant"
    ENCAPSULATE_FIELD = "encapsulate_field"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"
    CONSOLIDATE_CONDITIONAL = "consolidate_conditional"
    REMOVE_DEAD_CODE = "remove_dead_code"


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class RefactoringCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em refatoração de código.

    Identifica code smells e sugere refatorações para melhorar
    a qualidade e manutenibilidade do código.

    Example:
        >>> refactor = RefactoringCopilot()
        >>>
        >>> # Identificar code smells
        >>> result = refactor.identify_smells(code)
        >>>
        >>> # Sugerir refatorações
        >>> result = refactor.suggest_refactoring(code, focus=["readability"])
    """

    INSTRUCTIONS = """
    Você é um especialista em refatoração de código.
    
    ## Sua Missão
    
    Melhorar a qualidade do código através de refatorações que:
    - Mantêm o comportamento existente (sem breaking changes)
    - Aumentam legibilidade e manutenibilidade
    - Reduzem complexidade
    - Seguem princípios de design
    
    ## Code Smells a Identificar
    
    1. **Bloaters**
       - Long Method: Métodos muito longos
       - Large Class: Classes com muitas responsabilidades
       - Primitive Obsession: Uso excessivo de primitivos
       - Long Parameter List: Muitos parâmetros
    
    2. **Object-Orientation Abusers**
       - Switch Statements: Switch/case extensos
       - Temporary Field: Campos usados ocasionalmente
       - Refused Bequest: Subclasse não usa herança
    
    3. **Change Preventers**
       - Divergent Change: Uma classe muda por várias razões
       - Shotgun Surgery: Uma mudança afeta várias classes
    
    4. **Dispensables**
       - Comments: Comentários explicando código ruim
       - Duplicate Code: Código repetido
       - Lazy Class: Classe que faz pouco
       - Dead Code: Código não utilizado
    
    5. **Couplers**
       - Feature Envy: Método usa mais dados de outra classe
       - Inappropriate Intimacy: Classes muito acopladas
       - Message Chains: obj.getA().getB().getC()
    
    ## Técnicas de Refatoração
    
    - Extract Method/Class
    - Inline Method/Variable
    - Rename (Method, Variable, Class)
    - Move Method/Field
    - Replace Conditional with Polymorphism
    - Introduce Parameter Object
    
    ## Formato da Resposta
    
    1. **Code Smells Encontrados**: Lista com localização
    2. **Refatorações Sugeridas**: Para cada smell
    3. **Código Refatorado**: Antes e depois
    4. **Benefícios**: Por que é melhor
    """

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o Refactoring Copilot.

        Args:
            model_config: Configurações do modelo
        """
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.3,
                max_tokens=4096,
            )

        tools = [
            CodeAnalysisTool(),
            FileOperationsTool(),
        ]

        super().__init__(
            name="Refactoring Expert",
            description="Sugere e aplica refatorações de código",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e sugere refatorações.

        Args:
            input_data: Código ou dicionário com informações

        Returns:
            AgentResponse com sugestões de refatoração
        """
        if isinstance(input_data, dict):
            code = input_data.get("code", "")
            focus = input_data.get("focus", [])
            message = input_data.get("message", "")

            if message:
                return self.run(f"{message}\n\nCódigo:\n```\n{code}\n```")

            return self.suggest_refactoring(code, focus=focus)

        return self.suggest_refactoring(str(input_data))

    def identify_smells(self, code: str, language: str = "python") -> AgentResponse:
        """
        Identifica code smells no código.

        Args:
            code: Código a ser analisado
            language: Linguagem de programação

        Returns:
            AgentResponse com code smells encontrados
        """
        prompt = f"""
        Analise o código abaixo e identifique TODOS os code smells:
        
        ```{language}
        {code}
        ```
        
        Para cada code smell encontrado:
        
        | Code Smell | Localização | Severidade | Descrição |
        |------------|-------------|------------|-----------|
        | Nome | Linha/Função | Alta/Média/Baixa | Breve descrição |
        
        Após a tabela, explique cada smell e seu impacto na manutenibilidade.
        """

        return self.run(prompt)

    def suggest_refactoring(
        self, code: str, language: str = "python", focus: list[str] | None = None
    ) -> AgentResponse:
        """
        Sugere refatorações para o código.

        Args:
            code: Código a ser refatorado
            language: Linguagem de programação
            focus: Áreas de foco (readability, performance, etc.)

        Returns:
            AgentResponse com sugestões de refatoração
        """
        focus_str = ""
        if focus:
            focus_str = f"\n\nFoque especialmente em: {', '.join(focus)}"

        prompt = f"""
        Sugira refatorações para melhorar o seguinte código:
        
        ```{language}
        {code}
        ```
        {focus_str}
        
        Para cada sugestão:
        1. **Problema Identificado**: Qual code smell ou issue
        2. **Técnica de Refatoração**: Qual técnica aplicar
        3. **Código Antes e Depois**: Mostrar a mudança
        4. **Benefícios**: Por que é uma melhoria
        """

        return self.run(prompt)

    def apply_refactoring(
        self, code: str, refactoring_type: RefactoringType, target: str, language: str = "python"
    ) -> AgentResponse:
        """
        Aplica uma refatoração específica.

        Args:
            code: Código original
            refactoring_type: Tipo de refatoração
            target: Alvo da refatoração (função, variável, etc.)
            language: Linguagem de programação

        Returns:
            AgentResponse com código refatorado
        """
        prompt = f"""
        Aplique a refatoração **{refactoring_type.value}** no seguinte código:
        
        **Alvo da refatoração:** {target}
        
        ```{language}
        {code}
        ```
        
        Forneça:
        1. O código completamente refatorado
        2. Lista de todas as mudanças feitas
        3. Justificativa para cada mudança
        """

        return self.run(prompt)

    def apply_pattern(self, code: str, pattern: str, language: str = "python") -> AgentResponse:
        """
        Aplica um design pattern ao código.

        Args:
            code: Código original
            pattern: Design pattern a aplicar
            language: Linguagem de programação

        Returns:
            AgentResponse com código com pattern aplicado
        """
        prompt = f"""
        Refatore o código abaixo aplicando o design pattern **{pattern}**:
        
        ```{language}
        {code}
        ```
        
        Forneça:
        1. **Código Refatorado**: Implementação completa do pattern
        2. **Diagrama UML** (em ASCII ou Mermaid): Estrutura do pattern
        3. **Explicação**: Como o pattern resolve o problema
        4. **Benefícios**: Vantagens da mudança
        5. **Trade-offs**: Desvantagens ou custos
        """

        return self.run(prompt)

    def simplify_code(self, code: str, language: str = "python") -> AgentResponse:
        """
        Simplifica código complexo.

        Args:
            code: Código a ser simplificado
            language: Linguagem de programação

        Returns:
            AgentResponse com código simplificado
        """
        prompt = f"""
        Simplifique o seguinte código mantendo a funcionalidade:
        
        ```{language}
        {code}
        ```
        
        Foque em:
        - Reduzir complexidade ciclomática
        - Eliminar código desnecessário
        - Melhorar legibilidade
        - Usar recursos idiomáticos da linguagem
        
        Forneça o código simplificado e explique cada simplificação.
        """

        return self.run(prompt)

    def extract_method(
        self, code: str, lines_to_extract: str, method_name: str, language: str = "python"
    ) -> AgentResponse:
        """
        Extrai um trecho de código para um novo método.

        Args:
            code: Código original
            lines_to_extract: Descrição das linhas a extrair
            method_name: Nome sugerido para o novo método
            language: Linguagem de programação

        Returns:
            AgentResponse com código refatorado
        """
        prompt = f"""
        Extraia as linhas indicadas para um novo método:
        
        **Código Original:**
        ```{language}
        {code}
        ```
        
        **Linhas a Extrair:** {lines_to_extract}
        **Nome do Novo Método:** {method_name}
        
        Forneça:
        1. O novo método extraído (com docstring)
        2. O código original modificado para usar o novo método
        3. Parâmetros necessários para o novo método
        """

        return self.run(prompt)

    def remove_duplication(self, code: str, language: str = "python") -> AgentResponse:
        """
        Remove código duplicado.

        Args:
            code: Código com duplicações
            language: Linguagem de programação

        Returns:
            AgentResponse com código sem duplicações
        """
        prompt = f"""
        Identifique e remova duplicações no seguinte código:
        
        ```{language}
        {code}
        ```
        
        Para cada duplicação:
        1. Identificar o código duplicado
        2. Criar abstração apropriada (função, classe, constante)
        3. Refatorar usos para a nova abstração
        
        Forneça o código completamente refatorado sem duplicações.
        """

        return self.run(prompt)

    def improve_naming(self, code: str, language: str = "python") -> AgentResponse:
        """
        Melhora nomenclatura de variáveis, funções e classes.

        Args:
            code: Código com nomenclatura a melhorar
            language: Linguagem de programação

        Returns:
            AgentResponse com nomenclatura melhorada
        """
        prompt = f"""
        Melhore a nomenclatura no seguinte código:
        
        ```{language}
        {code}
        ```
        
        Identifique e renomeie:
        - Variáveis com nomes pouco descritivos
        - Funções que não indicam claramente o que fazem
        - Classes com nomes confusos
        - Abreviações não claras
        
        Forneça uma tabela de renomeações e o código atualizado.
        
        | Original | Novo | Justificativa |
        |----------|------|---------------|
        """

        return self.run(prompt)

    def modernize_code(
        self, code: str, language: str = "python", target_version: str | None = None
    ) -> AgentResponse:
        """
        Moderniza código para usar recursos mais recentes da linguagem.

        Args:
            code: Código a ser modernizado
            language: Linguagem de programação
            target_version: Versão alvo (ex: "3.12" para Python)

        Returns:
            AgentResponse com código modernizado
        """
        version_str = f" (versão {target_version})" if target_version else ""

        prompt = f"""
        Modernize o seguinte código {language}{version_str}:
        
        ```{language}
        {code}
        ```
        
        Use recursos modernos como:
        - List comprehensions / Generator expressions
        - f-strings (Python) / Template literals (JS)
        - Destructuring / Pattern matching
        - Type hints / TypeScript types
        - Async/await quando apropriado
        
        Forneça o código modernizado e explique cada modernização.
        """

        return self.run(prompt)
