# =============================================================================
# Copilot-IA - Security Copilot
# =============================================================================
"""
Copiloto especializado em segurança de aplicações.

Este copiloto analisa vulnerabilidades:
- OWASP Top 10
- Análise de código seguro
- Revisão de autenticação/autorização
- Detecção de dados sensíveis expostos
"""

from enum import Enum
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
class VulnerabilitySeverity(str, Enum):
    """Severidade de vulnerabilidades."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(str, Enum):
    """Categorias OWASP Top 10 2021."""

    BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    CRYPTOGRAPHIC_FAILURES = "A02:2021-Cryptographic Failures"
    INJECTION = "A03:2021-Injection"
    INSECURE_DESIGN = "A04:2021-Insecure Design"
    SECURITY_MISCONFIGURATION = "A05:2021-Security Misconfiguration"
    VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    AUTH_FAILURES = "A07:2021-Identification and Authentication Failures"
    DATA_INTEGRITY_FAILURES = "A08:2021-Software and Data Integrity Failures"
    LOGGING_FAILURES = "A09:2021-Security Logging and Monitoring Failures"
    SSRF = "A10:2021-Server-Side Request Forgery"


class Vulnerability(BaseModel):
    """Vulnerabilidade identificada."""

    category: VulnerabilityCategory
    severity: VulnerabilitySeverity
    location: str = Field(description="Arquivo e linha")
    description: str
    impact: str
    recommendation: str
    cwe_id: str | None = None


# -----------------------------------------------------------------------------
# Copiloto
# -----------------------------------------------------------------------------
class SecurityCopilot(BaseCopilotAgent):
    """
    Copiloto especializado em segurança de aplicações.

    Analisa código em busca de vulnerabilidades e fornece
    recomendações de segurança.

    Example:
        >>> security = SecurityCopilot()
        >>>
        >>> # Scan de vulnerabilidades
        >>> result = security.vulnerability_scan(code)
        >>>
        >>> # Análise de autenticação
        >>> result = security.review_authentication(auth_code)
    """

    INSTRUCTIONS = """
    Você é um especialista em segurança de aplicações (AppSec).
    
    ## Sua Missão
    
    Identificar vulnerabilidades de segurança e fornecer recomendações
    práticas para mitigá-las.
    
    ## OWASP Top 10 2021
    
    1. **A01:2021 - Broken Access Control**
       - Falta de verificação de autorização
       - IDOR (Insecure Direct Object Reference)
       - Elevação de privilégio
    
    2. **A02:2021 - Cryptographic Failures**
       - Dados sensíveis não criptografados
       - Algoritmos fracos
       - Chaves hardcoded
    
    3. **A03:2021 - Injection**
       - SQL Injection
       - Command Injection
       - XSS (Cross-Site Scripting)
       - LDAP Injection
    
    4. **A04:2021 - Insecure Design**
       - Falta de threat modeling
       - Design patterns inseguros
    
    5. **A05:2021 - Security Misconfiguration**
       - Configurações padrão inseguras
       - Recursos desnecessários habilitados
       - Mensagens de erro detalhadas
    
    6. **A06:2021 - Vulnerable Components**
       - Dependências desatualizadas
       - Bibliotecas com CVEs conhecidos
    
    7. **A07:2021 - Auth Failures**
       - Senhas fracas permitidas
       - Sessões não expiram
       - Credenciais expostas
    
    8. **A08:2021 - Data Integrity Failures**
       - Deserialização insegura
       - Atualizações não verificadas
    
    9. **A09:2021 - Logging Failures**
       - Falta de logs de segurança
       - Informações sensíveis em logs
    
    10. **A10:2021 - SSRF**
        - Requisições server-side sem validação
    
    ## Formato da Resposta
    
    Para cada vulnerabilidade:
    - Severidade (Critical/High/Medium/Low)
    - Categoria OWASP
    - Localização no código
    - Descrição do risco
    - Impacto potencial
    - Recomendação de correção
    - Código corrigido (quando aplicável)
    """

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Inicializa o Security Copilot.

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
            name="Security Analyst",
            description="Analisa vulnerabilidades e melhores práticas de segurança",
            instructions=self.INSTRUCTIONS,
            model_config=model_config,
            tools=tools,
        )

    def _default_instructions(self) -> str:
        return self.INSTRUCTIONS

    def process(self, input_data: Any) -> AgentResponse:
        """
        Processa a entrada e realiza análise de segurança.

        Args:
            input_data: Código ou informações do projeto

        Returns:
            AgentResponse com análise de segurança
        """
        if isinstance(input_data, dict):
            code = input_data.get("code", "")
            message = input_data.get("message", "")

            if message:
                return self.run(f"{message}\n\nCódigo:\n```\n{code}\n```")

            return self.vulnerability_scan(code)

        return self.vulnerability_scan(str(input_data))

    def vulnerability_scan(
        self,
        code: str,
        language: str = "python",
        focus: list[VulnerabilityCategory] | None = None,
    ) -> AgentResponse:
        """
        Realiza scan de vulnerabilidades no código.

        Args:
            code: Código a ser analisado
            language: Linguagem de programação
            focus: Categorias específicas para focar

        Returns:
            AgentResponse com vulnerabilidades encontradas
        """
        focus_str = ""
        if focus:
            focus_str = f"\n\nFoque especialmente em: {', '.join(f.value for f in focus)}"

        prompt = f"""
        Realize uma análise de segurança completa do seguinte código:
        
        ```{language}
        {code}
        ```
        {focus_str}
        
        Para cada vulnerabilidade encontrada, forneça:
        
        ## Vulnerabilidades Encontradas
        
        ### [SEVERIDADE] Categoria OWASP
        - **Localização**: Arquivo:linha
        - **Descrição**: O que é o problema
        - **Impacto**: O que um atacante poderia fazer
        - **CWE**: ID do CWE relacionado
        - **Recomendação**: Como corrigir
        - **Código Corrigido**:
        ```{language}
        // código corrigido
        ```
        
        ## Resumo
        - Total de vulnerabilidades: X
        - Críticas: X, Altas: X, Médias: X, Baixas: X
        
        ## Recomendações Gerais
        - ...
        """

        return self.run(prompt)

    def review_authentication(self, code: str, language: str = "python") -> AgentResponse:
        """
        Analisa a implementação de autenticação.

        Args:
            code: Código de autenticação
            language: Linguagem de programação

        Returns:
            AgentResponse com análise de auth
        """
        prompt = f"""
        Analise a implementação de autenticação/autorização:
        
        ```{language}
        {code}
        ```
        
        Verifique:
        
        ## Autenticação
        - [ ] Armazenamento seguro de senhas (bcrypt, argon2)
        - [ ] Proteção contra brute force
        - [ ] Multi-factor authentication
        - [ ] Recuperação de senha segura
        
        ## Sessões
        - [ ] Tokens seguros (tamanho, entropia)
        - [ ] Expiração apropriada
        - [ ] Invalidação no logout
        - [ ] Proteção contra session fixation
        
        ## Autorização
        - [ ] Verificação em cada requisição
        - [ ] Princípio do menor privilégio
        - [ ] Proteção contra escalação
        
        ## JWT (se aplicável)
        - [ ] Algoritmo seguro (não none)
        - [ ] Validação completa
        - [ ] Expiração curta
        - [ ] Refresh token seguro
        
        Forneça recomendações específicas para cada problema encontrado.
        """

        return self.run(prompt)

    def check_injection(self, code: str, language: str = "python") -> AgentResponse:
        """
        Verifica vulnerabilidades de injeção.

        Args:
            code: Código a ser verificado
            language: Linguagem de programação

        Returns:
            AgentResponse com análise de injeção
        """
        prompt = f"""
        Analise o código em busca de vulnerabilidades de INJEÇÃO:
        
        ```{language}
        {code}
        ```
        
        Tipos a verificar:
        
        ## SQL Injection
        - Concatenação de strings em queries
        - Falta de prepared statements
        - ORM mal utilizado
        
        ## Command Injection
        - Uso de os.system, subprocess com input de usuário
        - Falta de sanitização
        
        ## XSS (Cross-Site Scripting)
        - Output não escapado
        - innerHTML com dados do usuário
        - Templates não seguros
        
        ## LDAP Injection
        - Queries LDAP com input não sanitizado
        
        ## Path Traversal
        - Manipulação de caminhos de arquivo
        
        Para cada vulnerabilidade, mostre:
        1. Código vulnerável
        2. Como explorar
        3. Código corrigido
        """

        return self.run(prompt)

    def check_sensitive_data(self, code: str, language: str = "python") -> AgentResponse:
        """
        Verifica exposição de dados sensíveis.

        Args:
            code: Código a ser verificado
            language: Linguagem de programação

        Returns:
            AgentResponse com análise
        """
        prompt = f"""
        Analise o código em busca de EXPOSIÇÃO DE DADOS SENSÍVEIS:
        
        ```{language}
        {code}
        ```
        
        Verificar:
        
        ## Credenciais Hardcoded
        - API keys
        - Senhas
        - Tokens
        - Connection strings
        
        ## Dados Sensíveis em Logs
        - Passwords logados
        - Tokens em logs
        - PII em mensagens de erro
        
        ## Criptografia
        - Dados sensíveis não criptografados
        - Algoritmos fracos (MD5, SHA1 para senhas)
        - Chaves em código
        
        ## Transmissão
        - HTTP em vez de HTTPS
        - Certificados não validados
        
        ## Armazenamento
        - Dados sensíveis em cookies
        - Cache de dados sensíveis
        
        Liste todos os problemas encontrados com severidade e correção.
        """

        return self.run(prompt)

    def review_dependencies(self, dependencies: str, language: str = "python") -> AgentResponse:
        """
        Analisa dependências em busca de vulnerabilidades conhecidas.

        Args:
            dependencies: Conteúdo do requirements.txt, package.json, etc.
            language: Linguagem/ecossistema

        Returns:
            AgentResponse com análise de dependências
        """
        prompt = f"""
        Analise as dependências em busca de vulnerabilidades:
        
        ```
        {dependencies}
        ```
        
        Linguagem/Ecossistema: {language}
        
        Verificar:
        
        1. **Versões Desatualizadas**
           - Dependências muito antigas
           - Versões com CVEs conhecidos
        
        2. **Dependências Abandonadas**
           - Projetos sem manutenção
           - Última atualização há muito tempo
        
        3. **Dependências de Alto Risco**
           - Bibliotecas com histórico de vulnerabilidades
        
        4. **Recomendações**
           - Versões seguras sugeridas
           - Alternativas mais seguras
        
        Formato:
        | Dependência | Versão Atual | Risco | Versão Segura | CVEs |
        """

        return self.run(prompt)

    def generate_security_checklist(
        self, project_type: str = "web", framework: str | None = None
    ) -> AgentResponse:
        """
        Gera checklist de segurança para um tipo de projeto.

        Args:
            project_type: Tipo de projeto (web, api, mobile)
            framework: Framework utilizado

        Returns:
            AgentResponse com checklist
        """
        framework_str = f" usando {framework}" if framework else ""

        prompt = f"""
        Gere um checklist de segurança completo para um projeto {project_type}{framework_str}.
        
        O checklist deve incluir:
        
        ## Desenvolvimento Seguro
        - [ ] Item 1
        - [ ] Item 2
        
        ## Autenticação e Autorização
        - [ ] ...
        
        ## Proteção de Dados
        - [ ] ...
        
        ## Configuração e Deploy
        - [ ] ...
        
        ## Monitoramento e Logging
        - [ ] ...
        
        ## Testes de Segurança
        - [ ] ...
        
        Para cada item, inclua uma breve descrição de como verificar/implementar.
        """

        return self.run(prompt)

    def suggest_security_headers(self, framework: str = "generic") -> AgentResponse:
        """
        Sugere headers de segurança HTTP.

        Args:
            framework: Framework web utilizado

        Returns:
            AgentResponse com headers recomendados
        """
        prompt = f"""
        Sugira headers de segurança HTTP para uma aplicação {framework}.
        
        Para cada header:
        
        ## Headers Recomendados
        
        ### Content-Security-Policy
        - **Valor**: ...
        - **Propósito**: ...
        - **Implementação em {framework}**: código
        
        ### X-Frame-Options
        ...
        
        ### Strict-Transport-Security
        ...
        
        ### X-Content-Type-Options
        ...
        
        ### X-XSS-Protection
        ...
        
        ### Referrer-Policy
        ...
        
        ### Permissions-Policy
        ...
        
        Inclua código de exemplo para configurar no {framework}.
        """

        return self.run(prompt)

    def review_api_security(
        self, api_spec: str, implementation: str | None = None
    ) -> AgentResponse:
        """
        Analisa a segurança de uma API.

        Args:
            api_spec: Especificação da API (OpenAPI/Swagger)
            implementation: Código de implementação (opcional)

        Returns:
            AgentResponse com análise de segurança da API
        """
        impl_str = ""
        if implementation:
            impl_str = f"""
            
            **Implementação:**
            ```
            {implementation}
            ```
            """

        prompt = f"""
        Analise a segurança da seguinte API:
        
        **Especificação:**
        ```
        {api_spec}
        ```
        {impl_str}
        
        Verificar:
        
        ## Autenticação
        - Método de auth utilizado
        - Segurança do método
        
        ## Autorização
        - Controle de acesso por endpoint
        - Rate limiting
        
        ## Validação de Input
        - Schemas definidos
        - Validação de tipos
        
        ## Exposição de Dados
        - Campos sensíveis expostos
        - Informações em mensagens de erro
        
        ## Configuração
        - CORS configurado corretamente
        - Headers de segurança
        
        Forneça recomendações específicas para cada problema.
        """

        return self.run(prompt)
