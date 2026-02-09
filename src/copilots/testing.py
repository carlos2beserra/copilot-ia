# =============================================================================
# Copilot-IA - Testing Copilot
# =============================================================================
"""
Copiloto especializado em geração de testes automatizados.

Este copiloto cria testes incluindo:
- Testes unitários
- Testes de integração
- Testes E2E
- Mocks e fixtures
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.agents.base import AgentResponse, BaseCopilotAgent, ModelConfig
from src.tools.code_analysis import CodeAnalysisTool
from src.tools.file_operations import FileOperationsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Dados
# -----------------------------------------------------------------------------
class TestType(str, Enum):
    """Tipos de teste."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"


class TestFramework(str, Enum):
    """Frameworks de teste suportados."""

    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    VITEST = "vitest"
    MOCHA = "mocha"
    JUNIT = "junit"


class TestCase(BaseModel):
    """Caso de teste."""

    name: str
    description: str
    test_type: TestType
    code: str
    expected_result: str | None = None


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class TestingCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em criação de testes.

    Gera testes automatizados abrangentes incluindo casos normais,
    edge cases, e tratamento de erros.

    Example:
        >>> test_copilot = TestingCopilot()
        >>>
        >>> # Gerar testes unitários
        >>> result = test_copilot.generate_unit_tests(code, framework="pytest")
        >>>
        >>> # Sugerir casos de teste
        >>> result = test_copilot.suggest_test_cases(code)
    """

    INSTRUCTIONS = """
    Você é um especialista em testes de software.
    
    ## Sua Missão
    
    Criar testes abrangentes e eficazes que garantam a qualidade do código.
    
    ## Tipos de Teste
    
    1. **Testes Unitários**
       - Testar funções/métodos isoladamente
       - Usar mocks para dependências
       - Cobrir happy path e edge cases
       - Testar tratamento de erros
    
    2. **Testes de Integração**
       - Testar integração entre componentes
       - Verificar fluxos de dados
       - Testar com banco de dados real ou em memória
    
    3. **Testes E2E**
       - Simular comportamento do usuário
       - Testar fluxos completos
       - Verificar UI e API juntos
    
    ## Boas Práticas
    
    - **AAA Pattern**: Arrange, Act, Assert
    - **Nomes descritivos**: test_should_do_X_when_Y
    - **Um assert por teste** (quando possível)
    - **Testes independentes**: não depender de ordem
    - **Fixtures reutilizáveis**: evitar duplicação
    
    ## Cobertura
    
    Garanta cobertura de:
    - Casos normais (happy path)
    - Casos de borda (edge cases)
    - Valores limites (boundary values)
    - Entradas inválidas
    - Exceções esperadas
    """

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        default_framework: TestFramework = TestFramework.PYTEST,
    ):
        """
        Inicializa o Testing Copilot.

        Args:
            model_config: Configurações do modelo
            default_framework: Framework de teste padrão
        """
        if model_config is None:
            model_config = ModelConfig(
                provider="openai",
                name="gpt-4o",
                temperature=0.3,
                max_tokens=4096,
            )

        self.default_framework = default_framework

        tools = [
            CodeAnalysisTool(),
            FileOperationsTool(),
        ]

        super().__init__(
            name="Test Generator",
            description="Cria testes unitários, de integração e E2E",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e gera testes.

        Args:
            input_data: Código ou dicionário com informações

        Returns:
            AgentResponse com os testes gerados
        """
        if isinstance(input_data, dict):
            code = input_data.get("code", "")
            test_type = input_data.get("test_type", "unit")
            framework = input_data.get("framework", self.default_framework.value)
            message = input_data.get("message", "")

            if message:
                return self.run(f"{message}\n\nCódigo:\n```\n{code}\n```")

            return self.generate_tests(code, test_type=test_type, framework=framework)

        return self.generate_tests(str(input_data))

    def generate_tests(
        self,
        code: str,
        language: str = "python",
        test_type: str = "unit",
        framework: str | None = None,
    ) -> AgentResponse:
        """
        Gera testes para o código fornecido.

        Args:
            code: Código a ser testado
            language: Linguagem de programação
            test_type: Tipo de teste (unit, integration, e2e)
            framework: Framework de teste

        Returns:
            AgentResponse com os testes gerados
        """
        framework = framework or self.default_framework.value

        prompt = f"""
        Gere testes **{test_type}** abrangentes para o seguinte código usando **{framework}**:
        
        ```{language}
        {code}
        ```
        
        Os testes devem cobrir:
        1. **Happy Path**: Casos de uso normais
        2. **Edge Cases**: Casos de borda
        3. **Error Handling**: Tratamento de erros
        4. **Boundary Values**: Valores limite
        
        Use o padrão AAA (Arrange, Act, Assert).
        Inclua mocks quando necessário.
        Nomeie os testes de forma descritiva.
        
        Retorne o código de teste completo e executável.
        """

        return self.run(prompt)

    def generate_unit_tests(
        self,
        code: str,
        language: str = "python",
        framework: str | None = None,
        coverage_target: int = 80,
    ) -> AgentResponse:
        """
        Gera testes unitários específicos.

        Args:
            code: Código a ser testado
            language: Linguagem de programação
            framework: Framework de teste
            coverage_target: Meta de cobertura (%)

        Returns:
            AgentResponse com testes unitários
        """
        framework = framework or self.default_framework.value

        prompt = f"""
        Gere testes UNITÁRIOS para atingir {coverage_target}% de cobertura:
        
        ```{language}
        {code}
        ```
        
        Framework: {framework}
        
        Requisitos:
        - Testar cada função/método individualmente
        - Usar mocks para todas as dependências externas
        - Incluir testes parametrizados quando aplicável
        - Cobrir todos os branches condicionais
        
        Estrutura do arquivo de teste:
        1. Imports
        2. Fixtures
        3. Testes organizados por classe/função testada
        """

        return self.run(prompt)

    def generate_integration_tests(
        self, components: list[str], code: str, language: str = "python"
    ) -> AgentResponse:
        """
        Gera testes de integração.

        Args:
            components: Lista de componentes a integrar
            code: Código dos componentes
            language: Linguagem de programação

        Returns:
            AgentResponse com testes de integração
        """
        components_str = ", ".join(components)

        prompt = f"""
        Gere testes de INTEGRAÇÃO entre os seguintes componentes: {components_str}
        
        ```{language}
        {code}
        ```
        
        Os testes devem verificar:
        - Comunicação correta entre componentes
        - Fluxo de dados end-to-end
        - Tratamento de erros entre componentes
        - Estados compartilhados
        
        Use fixtures realistas e dados de teste significativos.
        """

        return self.run(prompt)

    def suggest_test_cases(self, code: str, language: str = "python") -> AgentResponse:
        """
        Sugere casos de teste para o código.

        Args:
            code: Código a ser analisado
            language: Linguagem de programação

        Returns:
            AgentResponse com sugestões de casos de teste
        """
        prompt = f"""
        Analise o código abaixo e sugira TODOS os casos de teste necessários:
        
        ```{language}
        {code}
        ```
        
        Organize as sugestões em:
        
        ## Testes Unitários
        - [ ] Caso 1: descrição
        - [ ] Caso 2: descrição
        
        ## Testes de Integração
        - [ ] Caso 1: descrição
        
        ## Testes E2E (se aplicável)
        - [ ] Caso 1: descrição
        
        ## Edge Cases
        - [ ] Caso 1: descrição
        
        Para cada caso, explique brevemente o que deve ser testado e por quê.
        """

        return self.run(prompt)

    def generate_mocks(
        self, code: str, dependencies: list[str], language: str = "python"
    ) -> AgentResponse:
        """
        Gera mocks para dependências.

        Args:
            code: Código que usa as dependências
            dependencies: Lista de dependências a mockar
            language: Linguagem de programação

        Returns:
            AgentResponse com mocks gerados
        """
        deps_str = ", ".join(dependencies)

        prompt = f"""
        Gere mocks/stubs para as seguintes dependências: {deps_str}
        
        Código que usa as dependências:
        ```{language}
        {code}
        ```
        
        Os mocks devem:
        - Simular comportamento realista
        - Ser configuráveis para diferentes cenários
        - Incluir verificação de chamadas
        - Ser reutilizáveis como fixtures
        """

        return self.run(prompt)

    def generate_fixtures(
        self, code: str, language: str = "python", framework: str | None = None
    ) -> AgentResponse:
        """
        Gera fixtures de teste.

        Args:
            code: Código a ser testado
            language: Linguagem de programação
            framework: Framework de teste

        Returns:
            AgentResponse com fixtures
        """
        framework = framework or self.default_framework.value

        prompt = f"""
        Gere fixtures reutilizáveis para testar o seguinte código:
        
        ```{language}
        {code}
        ```
        
        Framework: {framework}
        
        Inclua:
        - Fixtures de dados de teste
        - Fixtures de objetos mock
        - Fixtures de setup/teardown
        - Fixtures parametrizadas
        
        Organize em um arquivo conftest.py (ou equivalente).
        """

        return self.run(prompt)

    def analyze_test_coverage(self, test_code: str, source_code: str) -> AgentResponse:
        """
        Analisa a cobertura dos testes existentes.

        Args:
            test_code: Código dos testes
            source_code: Código fonte sendo testado

        Returns:
            AgentResponse com análise de cobertura
        """
        prompt = f"""
        Analise a cobertura dos seguintes testes:
        
        **Código de Teste:**
        ```
        {test_code}
        ```
        
        **Código Fonte:**
        ```
        {source_code}
        ```
        
        Forneça:
        1. Estimativa de cobertura atual
        2. Funções/métodos não testados
        3. Branches não cobertos
        4. Edge cases não testados
        5. Sugestões de novos testes
        """

        return self.run(prompt)

    def generate_test_file(self, file_path: str) -> AgentResponse:
        """
        Gera arquivo de teste completo para um arquivo de código.

        Args:
            file_path: Caminho do arquivo a ser testado

        Returns:
            AgentResponse com arquivo de teste
        """
        path = Path(file_path)

        if not path.exists():
            return AgentResponse(
                success=False,
                content=f"Arquivo não encontrado: {file_path}",
                metadata={"error": "file_not_found"},
            )

        code = path.read_text(encoding="utf-8")
        language = self._detect_language(path.suffix)
        framework = self._get_framework_for_language(language)

        prompt = f"""
        Gere um arquivo de teste COMPLETO para:
        
        **Arquivo:** {path.name}
        **Linguagem:** {language}
        **Framework:** {framework}
        
        ```{language}
        {code}
        ```
        
        O arquivo de teste deve:
        - Ser salvo como test_{path.stem}.py (ou equivalente)
        - Incluir todos os imports necessários
        - Ter fixtures no início
        - Testar todas as funções/classes públicas
        - Seguir convenções do {framework}
        """

        return self.run(prompt)

    def _detect_language(self, extension: str) -> str:
        """Detecta a linguagem pela extensão."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
        }
        return language_map.get(extension.lower(), "python")

    def _get_framework_for_language(self, language: str) -> str:
        """Retorna o framework de teste padrão para a linguagem."""
        framework_map = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "go": "testing",
        }
        return framework_map.get(language, "pytest")
