# 🚀 Guia de Deploy - Copilot-IA

> Tutorial completo para subir o Copilot-IA como serviço e usar em outros projetos.

---

## 📋 Índice

1. [Parte 1: Subir para o GitHub](#parte-1-subir-para-o-github)
2. [Parte 2: Configurar Docker Hub](#parte-2-configurar-docker-hub)
3. [Parte 3: Rodar como Serviço](#parte-3-rodar-como-serviço)
4. [Parte 4: Integrar via API](#parte-4-integrar-via-api-em-outros-projetos)

---

## Parte 1: Subir para o GitHub

### Passo 1.1: Criar repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name**: `copilot-ia`
   - **Description**: `Copilotos de Desenvolvimento com IA`
   - **Visibilidade**: Public ou Private (sua escolha)
   - ❌ NÃO marque "Add a README file" (já temos)
5. Clique em **"Create repository"**

### Passo 1.2: Preparar o projeto local

```bash
# Entre na pasta do projeto
cd /home/zero/Workspace/Copilot-ia

# Verifique se tem um .gitignore
cat .gitignore
```

Se não tiver `.gitignore`, crie um:

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/

# Ambiente virtual
.venv/
venv/
env/

# Variáveis de ambiente (IMPORTANTE: não commitar!)
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs e cache
logs/
*.log
data/cache/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage

# Docker
*.tar

# OS
.DS_Store
Thumbs.db
EOF
```

### Passo 1.3: Inicializar Git e fazer push

```bash
# Inicializar repositório Git (se ainda não foi)
git init

# Adicionar todos os arquivos
git add .

# Verificar o que será commitado
git status

# Fazer o primeiro commit
git commit -m "🎉 Initial commit: Copilot-IA"

# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu usuário GitHub)
git remote add origin https://github.com/SEU_USUARIO/copilot-ia.git

# Enviar para o GitHub
git branch -M main
git push -u origin main
```

### Passo 1.4: Configurar Secrets no GitHub

1. No GitHub, vá até seu repositório
2. Clique em **Settings** (⚙️)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **"New repository secret"**
5. Adicione cada secret:

| Name | Value | Onde obter |
|------|-------|------------|
| `OPENAI_API_KEY` | `sk-...` | [platform.openai.com](https://platform.openai.com/api-keys) |
| `GROQ_API_KEY` | `gsk_...` | [console.groq.com](https://console.groq.com/keys) |
| `DOCKER_USERNAME` | Seu usuário | Docker Hub (próximo passo) |
| `DOCKER_PASSWORD` | Token | Docker Hub (próximo passo) |

---

## Parte 2: Configurar Docker Hub

### Passo 2.1: Criar conta no Docker Hub

1. Acesse [hub.docker.com](https://hub.docker.com)
2. Clique em **"Sign Up"** (ou faça login se já tiver conta)
3. Escolha o plano **Free** (gratuito)
4. Confirme seu email

### Passo 2.2: Criar repositório no Docker Hub

1. No Docker Hub, clique em **"Create Repository"**
2. Preencha:
   - **Name**: `copilot-ia`
   - **Description**: `Copilotos de Desenvolvimento com IA`
   - **Visibility**: Public
3. Clique em **"Create"**

### Passo 2.3: Criar Access Token

1. Clique no seu avatar → **Account Settings**
2. Vá em **Security** → **Access Tokens**
3. Clique em **"New Access Token"**
4. Preencha:
   - **Description**: `GitHub Actions CI`
   - **Permissions**: `Read, Write, Delete`
5. Clique em **"Generate"**
6. **COPIE O TOKEN** (só aparece uma vez!)

### Passo 2.4: Adicionar Docker secrets no GitHub

Volte ao GitHub (Settings → Secrets → Actions) e adicione:

- **Name**: `DOCKER_USERNAME` → **Value**: seu usuário do Docker Hub
- **Name**: `DOCKER_PASSWORD` → **Value**: o token que você copiou

### Passo 2.5: Testar build local

```bash
# No seu terminal, teste o build local
cd /home/zero/Workspace/Copilot-ia

# Build da imagem
docker build -t copilot-ia .

# Verificar se criou
docker images | grep copilot-ia
```

---

## Parte 3: Rodar como Serviço

### Passo 3.1: Configurar variáveis de ambiente

```bash
# Criar arquivo .env se não existir
cd /home/zero/Workspace/Copilot-ia

# Copiar exemplo
cp env.example .env

# Editar com suas chaves
nano .env
```

Configure pelo menos isso no `.env`:

```env
# Escolha UM provider e configure a chave
GROQ_API_KEY=gsk_SuaChaveAqui
DEFAULT_PROVIDER=groq
DEFAULT_MODEL=llama-3.1-70b-versatile

# OU use OpenAI
# OPENAI_API_KEY=sk-SuaChaveAqui
# DEFAULT_PROVIDER=openai
# DEFAULT_MODEL=gpt-4o-mini

# Cache habilitado
CACHE_ENABLED=true

# Log level
LOG_LEVEL=INFO
```

### Passo 3.2: Subir os containers

```bash
# Subir em modo background
docker-compose up -d

# Verificar se está rodando
docker-compose ps

# Ver logs (Ctrl+C para sair)
docker-compose logs -f
```

Você deve ver algo assim:
```
NAME                  STATUS    PORTS
copilot-ia-api        running   0.0.0.0:8000->8000/tcp
copilot-ia-redis      running   0.0.0.0:6379->6379/tcp
```

### Passo 3.3: Testar se está funcionando

```bash
# Teste 1: Health check
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy","version":"0.1.0"}

# Teste 2: Revisar código
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def soma(a, b):\n    return a + b",
    "language": "python"
  }'
```

### Passo 3.4: Comandos úteis do Docker

```bash
# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down

# Reiniciar
docker-compose restart

# Reconstruir após mudanças
docker-compose up -d --build

# Ver uso de recursos
docker stats
```

---

## Parte 4: Integrar via API em Outros Projetos

### Opção A: Usar via cURL/Terminal

```bash
# Em qualquer projeto, você pode chamar a API:

# Revisar um arquivo
cat meu_codigo.py | curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d @- 

# Ou com o conteúdo direto
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "'"$(cat src/main.py)"'",
    "language": "python"
  }'
```

### Opção B: Usar via Python

Crie um arquivo `copilot_client.py` no seu outro projeto:

```python
"""
Cliente simples para o Copilot-IA API.
Coloque este arquivo no seu projeto para usar o Copilot-IA.
"""
import httpx
from pathlib import Path


class CopilotClient:
    """Cliente para a API do Copilot-IA."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=120)
    
    def review(self, code: str, language: str = "python", quick: bool = False) -> dict:
        """Revisa código e retorna análise."""
        response = self.client.post(
            f"{self.base_url}/api/review",
            json={"code": code, "language": language, "quick": quick}
        )
        return response.json()
    
    def review_file(self, file_path: str) -> dict:
        """Revisa um arquivo."""
        path = Path(file_path)
        code = path.read_text()
        
        # Detectar linguagem pela extensão
        lang_map = {".py": "python", ".js": "javascript", ".ts": "typescript"}
        language = lang_map.get(path.suffix, "text")
        
        return self.review(code, language)
    
    def generate_tests(self, code: str, language: str = "python", framework: str = "pytest") -> dict:
        """Gera testes para o código."""
        response = self.client.post(
            f"{self.base_url}/api/test",
            json={"code": code, "language": language, "framework": framework}
        )
        return response.json()
    
    def security_scan(self, code: str, language: str = "python") -> dict:
        """Analisa segurança do código."""
        response = self.client.post(
            f"{self.base_url}/api/security",
            json={"code": code, "language": language}
        )
        return response.json()
    
    def generate_docs(self, code: str, language: str = "python") -> dict:
        """Gera documentação para o código."""
        response = self.client.post(
            f"{self.base_url}/api/docs",
            json={"code": code, "language": language}
        )
        return response.json()
    
    def health(self) -> dict:
        """Verifica se a API está funcionando."""
        response = self.client.get(f"{self.base_url}/health")
        return response.json()


# Exemplo de uso
if __name__ == "__main__":
    client = CopilotClient()
    
    # Verificar conexão
    print("Status:", client.health())
    
    # Revisar código
    codigo = '''
def calcular_media(notas):
    soma = 0
    for nota in notas:
        soma = soma + nota
    media = soma / len(notas)
    return media
'''
    
    resultado = client.review(codigo)
    print("\n📝 Revisão:")
    print(resultado.get("content", resultado))
```

**Como usar no seu projeto:**

```python
from copilot_client import CopilotClient

# Conectar à API
copilot = CopilotClient("http://localhost:8000")

# Revisar código
resultado = copilot.review_file("src/minha_funcao.py")
print(resultado["content"])

# Gerar testes
testes = copilot.generate_tests(open("src/utils.py").read())
print(testes["content"])
```

### Opção C: Adicionar ao Makefile de outros projetos

No Makefile do seu **outro projeto**, adicione:

```makefile
# =============================================================================
# Integração com Copilot-IA
# =============================================================================

COPILOT_API := http://localhost:8000

# Revisar código com IA
ai-review:
	@echo "🔍 Revisando código com Copilot-IA..."
	@for file in $$(find src -name "*.py"); do \
		echo "Analisando: $$file"; \
		curl -s -X POST $(COPILOT_API)/api/review \
			-H "Content-Type: application/json" \
			-d "{\"code\": \"$$(cat $$file | jq -Rs .)\", \"language\": \"python\", \"quick\": true}" \
			| jq -r '.content // .error'; \
	done

# Gerar testes com IA
ai-test:
	@echo "🧪 Gerando testes com Copilot-IA..."
	@curl -s -X POST $(COPILOT_API)/api/test \
		-H "Content-Type: application/json" \
		-d "{\"code\": \"$$(cat $(FILE) | jq -Rs .)\", \"language\": \"python\"}" \
		| jq -r '.content'

# Análise de segurança com IA
ai-security:
	@echo "🔒 Analisando segurança com Copilot-IA..."
	@curl -s -X POST $(COPILOT_API)/api/security \
		-H "Content-Type: application/json" \
		-d "{\"code\": \"$$(cat $(FILE) | jq -Rs .)\", \"language\": \"python\"}" \
		| jq -r '.content'

# Verificar se Copilot-IA está rodando
ai-status:
	@curl -s $(COPILOT_API)/health | jq .
```

**Usar:**
```bash
make ai-review              # Revisa todos os arquivos Python
make ai-test FILE=src/app.py    # Gera testes para um arquivo
make ai-security FILE=src/auth.py   # Análise de segurança
```

### Opção D: Integrar no CI/CD de outros projetos

Adicione ao `.github/workflows/ci.yml` do seu **outro projeto**:

```yaml
name: CI with AI Review

on:
  pull_request:
    branches: [main]

jobs:
  ai-review:
    name: 🤖 AI Code Review
    runs-on: ubuntu-latest
    
    services:
      # Sobe o Copilot-IA como serviço no CI
      copilot-api:
        image: SEU_USUARIO/copilot-ia:latest
        ports:
          - 8000:8000
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          DEFAULT_PROVIDER: groq
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Wait for API
        run: |
          for i in {1..30}; do
            curl -s http://localhost:8000/health && break
            sleep 2
          done
      
      - name: 🔍 AI Code Review
        run: |
          for file in $(find src -name "*.py"); do
            echo "📝 Reviewing: $file"
            curl -s -X POST http://localhost:8000/api/review \
              -H "Content-Type: application/json" \
              -d "{\"code\": \"$(cat $file)\", \"language\": \"python\", \"quick\": true}"
          done
```

---

## 🔧 Troubleshooting

### Erro: "Connection refused" ao chamar API

```bash
# Verificar se os containers estão rodando
docker-compose ps

# Se não estiverem, suba novamente
docker-compose up -d

# Verificar logs de erro
docker-compose logs api
```

### Erro: "API key not configured"

```bash
# Verificar se .env existe e tem as chaves
cat .env | grep API_KEY

# Reiniciar containers após editar .env
docker-compose down
docker-compose up -d
```

### Erro: "Port 8000 already in use"

```bash
# Ver o que está usando a porta
lsof -i :8000

# Matar o processo ou usar outra porta
# Edite docker-compose.yml e mude a porta:
# ports:
#   - "8001:8000"
```

---

## ✅ Checklist Final

- [ ] Repositório criado no GitHub
- [ ] Secrets configurados no GitHub (API keys)
- [ ] Conta no Docker Hub criada
- [ ] Token do Docker Hub gerado
- [ ] Secrets do Docker configurados no GitHub
- [ ] Build local testado (`docker build`)
- [ ] Containers rodando (`docker-compose up -d`)
- [ ] API respondendo (`curl localhost:8000/health`)
- [ ] Integração testada em outro projeto

---

**Pronto! Agora você pode usar o Copilot-IA em qualquer projeto! 🚀**

