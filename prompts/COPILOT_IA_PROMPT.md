# 🤖 Copilot-IA - Prompt para Integração

> Use este prompt para integrar o Copilot-IA em outros projetos ou como contexto para assistentes de IA.

---

## 📋 Descrição do Sistema

```
Você tem acesso ao **Copilot-IA**, uma plataforma de agentes de IA especializados em desenvolvimento de software. 
O sistema utiliza o framework Agno e oferece 7 copilotos especializados que podem ser usados individualmente 
ou em conjunto através de um coordenador multiagente.
```

---

## 🎯 Copilotos Disponíveis

### 1. 🔍 Code Reviewer
**Função:** Analisa código, identifica problemas e sugere melhorias.

```python
from src.copilots import CodeReviewerCopilot

reviewer = CodeReviewerCopilot()

# Análise completa de código
resultado = reviewer.analyze(code="...", language="python")

# Análise de diff (pull requests)
resultado = reviewer.analyze_diff(diff="...")

# Focar em categorias específicas
resultado = reviewer.analyze(code="...", focus=["security", "performance"])
```

**Categorias de análise:** bugs, security, performance, maintainability, style, complexity

---

### 2. 📝 Documentation
**Função:** Gera documentação, docstrings e README automaticamente.

```python
from src.copilots import DocumentationCopilot
from src.copilots.documentation import DocstringStyle

doc = DocumentationCopilot()

# Gerar docstrings (Google, NumPy ou Sphinx)
resultado = doc.generate_docstring(code="...", language="python", style=DocstringStyle.GOOGLE)

# Gerar README completo
resultado = doc.generate_readme({
    "name": "Meu Projeto",
    "description": "Descrição do projeto",
    "features": ["Feature 1", "Feature 2"]
})

# Adicionar comentários inline
resultado = doc.add_inline_comments(code="...", language="python")

# Documentar arquivo completo
resultado = doc.document_file(file_path="src/main.py")
```

---

### 3. 🧪 Testing
**Função:** Cria testes unitários, de integração e E2E.

```python
from src.copilots import TestingCopilot

tester = TestingCopilot()

# Gerar testes unitários
resultado = tester.generate_unit_tests(code="...", language="python", framework="pytest")

# Gerar testes de integração
resultado = tester.generate_integration_tests(code="...")

# Gerar casos de teste
resultado = tester.suggest_test_cases(code="...")
```

**Frameworks suportados:**
- Python: pytest, unittest
- JavaScript/TypeScript: jest, vitest, mocha

---

### 4. 🐛 Debug
**Função:** Auxilia na identificação e resolução de bugs.

```python
from src.copilots import DebugCopilot

debugger = DebugCopilot()

# Analisar erro
resultado = debugger.analyze_error(
    error_message="TypeError: 'NoneType' object is not subscriptable",
    code="...",
    stack_trace="..."
)

# Sugerir correções
resultado = debugger.suggest_fix(code="...", error="...")
```

---

### 5. 🔧 Refactoring
**Função:** Sugere e aplica refatorações de código.

```python
from src.copilots import RefactoringCopilot

refactor = RefactoringCopilot()

# Sugerir refatorações
resultado = refactor.suggest_refactoring(code="...")

# Aplicar refatoração específica
resultado = refactor.apply_refactoring(code="...", refactoring_type="extract_method")

# Simplificar código
resultado = refactor.simplify(code="...")
```

**Tipos de refatoração:** extract_method, extract_class, rename, move, inline, simplify_conditional, remove_duplication

---

### 6. 🏗️ Architecture
**Função:** Orienta decisões arquiteturais e design patterns.

```python
from src.copilots import ArchitectureCopilot

architect = ArchitectureCopilot()

# Analisar arquitetura
resultado = architect.analyze_architecture(project_path=".")

# Sugerir design patterns
resultado = architect.suggest_patterns(code="...", context="...")

# Avaliar acoplamento
resultado = architect.evaluate_coupling(modules=["module1", "module2"])
```

---

### 7. 🔒 Security
**Função:** Analisa vulnerabilidades e melhores práticas de segurança.

```python
from src.copilots import SecurityCopilot

security = SecurityCopilot()

# Scan de vulnerabilidades
resultado = security.scan_vulnerabilities(code="...", language="python")

# Análise OWASP Top 10
resultado = security.analyze_owasp(code="...")

# Verificar dados sensíveis
resultado = security.check_sensitive_data(code="...")
```

**Categorias OWASP:** injection, broken_authentication, sensitive_data_exposure, xxe, broken_access_control, security_misconfiguration, xss, insecure_deserialization, vulnerable_components, insufficient_logging

---

## 🔄 Coordenador Multiagente

Para tarefas complexas que requerem múltiplos copilotos:

```python
from src.agents import CopilotCoordinator

coordinator = CopilotCoordinator()

# Análise completa (code review + security + architecture)
resultado = coordinator.full_analysis(code="...", language="python")

# Requisição livre (o coordenador decide quais copilotos usar)
resultado = coordinator.process("Revise este código e gere testes para ele")
```

---

## 🌐 Integração via API REST

O Copilot-IA pode ser consumido como serviço:

```bash
# Iniciar API
docker-compose up -d
# ou
make up
```

### Endpoints Disponíveis

```bash
# Code Review
POST /api/v1/review
{
  "code": "def foo(): pass",
  "language": "python"
}

# Documentation
POST /api/v1/docs
{
  "code": "...",
  "style": "google"
}

# Testing
POST /api/v1/test
{
  "code": "...",
  "framework": "pytest"
}

# Security
POST /api/v1/security
{
  "code": "...",
  "language": "python"
}

# Debug
POST /api/v1/debug
{
  "error": "...",
  "code": "...",
  "stack_trace": "..."
}
```

### Exemplo com cURL

```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(): pass", "language": "python"}'
```

### Exemplo com Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/review",
    json={"code": "def foo(): pass", "language": "python"}
)
print(response.json())
```

---

## 📦 Instalação como Dependência

```bash
# Via pip (se publicado no PyPI)
pip install copilot-ia

# Via GitHub
pip install git+https://github.com/seu-usuario/copilot-ia.git

# Como submódulo
git submodule add https://github.com/seu-usuario/copilot-ia.git libs/copilot-ia
```

---

## 🔧 Configuração

### Variáveis de Ambiente Necessárias

```env
# Escolha um provider LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=...

# Configurações opcionais
DEFAULT_MODEL=gpt-4o
DEFAULT_PROVIDER=openai
CACHE_ENABLED=true
LOG_LEVEL=INFO
```

---

## 💡 Casos de Uso Comuns

### 1. Revisão de Pull Request

```python
from src.copilots import CodeReviewerCopilot
from src.tools import GitTool

git = GitTool(repo_path=".")
diff = git.get_diff("main", "feature-branch")

reviewer = CodeReviewerCopilot()
resultado = reviewer.analyze_diff(diff)
```

### 2. Documentar Projeto Inteiro

```python
from src.copilots import DocumentationCopilot
from pathlib import Path

doc = DocumentationCopilot()

for file in Path("src").rglob("*.py"):
    resultado = doc.document_file(str(file))
    # Salvar documentação gerada
```

### 3. Análise de Segurança Completa

```python
from src.copilots import SecurityCopilot
from src.tools import CodeAnalysisTool

security = SecurityCopilot()
analysis = CodeAnalysisTool()

for file in analysis.find_files("src", "*.py"):
    resultado = security.scan_vulnerabilities(file_path=file)
```

### 4. Pipeline CI/CD

```yaml
# .github/workflows/copilot-review.yml
- name: Code Review
  run: |
    curl -X POST ${{ secrets.COPILOT_API_URL }}/api/v1/review \
      -d '{"code": "${{ github.event.pull_request.diff_url }}"}'
```

---

## 📊 Formato de Resposta

Todos os copilotos retornam um objeto `AgentResponse`:

```python
class AgentResponse:
    success: bool      # Se a operação foi bem-sucedida
    content: str       # Conteúdo da resposta
    metadata: dict     # Metadados adicionais
    tokens_used: int   # Tokens consumidos
    model: str         # Modelo utilizado
```

---

## 🎓 Linguagens Suportadas

| Linguagem | Análise AST | Métricas | Code Review | Testes |
|-----------|-------------|----------|-------------|--------|
| Python | ✅ Completo | ✅ | ✅ | ✅ pytest/unittest |
| JavaScript | ⚠️ Básico | ✅ | ✅ | ✅ jest/vitest |
| TypeScript | ⚠️ Básico | ✅ | ✅ | ✅ jest/vitest |
| Java | ⚠️ Básico | ✅ | ✅ | ✅ JUnit |
| Go | ⚠️ Básico | ✅ | ✅ | ✅ go test |
| Rust | ⚠️ Básico | ✅ | ✅ | ✅ cargo test |
| C/C++ | ⚠️ Básico | ✅ | ✅ | ⚠️ |

---

## 🔗 Links Úteis

- **Repositório:** https://github.com/seu-usuario/copilot-ia
- **API Docs:** http://localhost:8000/docs (Swagger)
- **Notebooks:** `notebooks/` - Exemplos interativos

---

**Versão:** 1.0.0  
**Framework:** Agno  
**Licença:** MIT

