# =============================================================================
# Copilot-IA - API REST Principal
# =============================================================================
"""
API REST para acesso aos copilotos de desenvolvimento.

Endpoints disponíveis:
- POST /api/v1/review - Revisão de código
- POST /api/v1/docs - Geração de documentação
- POST /api/v1/test - Geração de testes
- POST /api/v1/security - Análise de segurança
- POST /api/v1/debug - Assistência de debug
- POST /api/v1/refactor - Sugestões de refatoração
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.copilots import (
    CodeReviewerCopilot,
    DebugCopilot,
    DocumentationCopilot,
    RefactoringCopilot,
    SecurityCopilot,
    TestingCopilot,
)
from src.utils import get_logger, setup_logging

# Configurar logging
setup_logging(level="INFO")
logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Modelos de Request/Response
# -----------------------------------------------------------------------------
class CodeRequest(BaseModel):
    """Request com código para análise."""

    code: str = Field(..., description="Código fonte para análise")
    language: str = Field(default="python", description="Linguagem de programação")
    filename: str | None = Field(default=None, description="Nome do arquivo")


class ReviewRequest(CodeRequest):
    """Request para revisão de código."""

    quick: bool = Field(default=False, description="Revisão rápida")


class DocRequest(CodeRequest):
    """Request para geração de documentação."""

    style: str = Field(default="google", description="Estilo de docstring")
    doc_type: str = Field(default="docstring", description="Tipo de documentação")


class TestRequest(CodeRequest):
    """Request para geração de testes."""

    framework: str = Field(default="pytest", description="Framework de teste")
    test_type: str = Field(default="unit", description="Tipo de teste")


class DebugRequest(BaseModel):
    """Request para debug."""

    error_message: str = Field(..., description="Mensagem de erro")
    stack_trace: str | None = Field(default=None, description="Stack trace")
    code: str | None = Field(default=None, description="Código relacionado")
    language: str = Field(default="python", description="Linguagem")


class RefactorRequest(CodeRequest):
    """Request para refatoração."""

    focus: list[str] | None = Field(default=None, description="Áreas de foco")


class CopilotResponse(BaseModel):
    """Response padrão dos copilotos."""

    success: bool
    content: str
    model: str | None = None
    metadata: dict = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Instâncias dos Copilotos (lazy loading)
# -----------------------------------------------------------------------------
_copilots = {}


def get_copilot(copilot_type: str):
    """Obtém instância do copiloto (singleton lazy)."""
    if copilot_type not in _copilots:
        copilot_classes = {
            "reviewer": CodeReviewerCopilot,
            "documentation": DocumentationCopilot,
            "testing": TestingCopilot,
            "security": SecurityCopilot,
            "debug": DebugCopilot,
            "refactoring": RefactoringCopilot,
        }
        _copilots[copilot_type] = copilot_classes[copilot_type]()
    return _copilots[copilot_type]


# -----------------------------------------------------------------------------
# Lifecycle
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle do app."""
    logger.info("🚀 Iniciando Copilot-IA API...")
    yield
    logger.info("👋 Encerrando Copilot-IA API...")


# -----------------------------------------------------------------------------
# App FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Copilot-IA API",
    description="API REST para copilotos de desenvolvimento inteligentes",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "name": "Copilot-IA API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy"}


@app.post("/api/v1/review", response_model=CopilotResponse)
async def review_code(request: ReviewRequest):
    """
    Revisa código e identifica problemas.

    Analisa o código fornecido e retorna:
    - Bugs potenciais
    - Problemas de segurança
    - Sugestões de melhoria
    - Score de qualidade
    """
    try:
        reviewer = get_copilot("reviewer")

        if request.quick:
            result = reviewer.quick_review(request.code, request.language)
        else:
            result = reviewer.analyze_code(request.code, request.language)

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/docs", response_model=CopilotResponse)
async def generate_documentation(request: DocRequest):
    """
    Gera documentação para código.

    Tipos suportados:
    - docstring: Gera docstrings para funções/classes
    - readme: Gera README do projeto
    - api: Gera documentação de API
    """
    try:
        doc_copilot = get_copilot("documentation")

        if request.doc_type == "docstring":
            result = doc_copilot.generate_docstring(
                request.code, request.language, style=request.style
            )
        else:
            result = doc_copilot.process(
                {
                    "code": request.code,
                    "language": request.language,
                    "type": request.doc_type,
                }
            )

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em docs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/test", response_model=CopilotResponse)
async def generate_tests(request: TestRequest):
    """
    Gera testes automatizados.

    Tipos de teste:
    - unit: Testes unitários
    - integration: Testes de integração
    - e2e: Testes end-to-end
    """
    try:
        test_copilot = get_copilot("testing")

        result = test_copilot.generate_tests(
            request.code,
            request.language,
            test_type=request.test_type,
            framework=request.framework,
        )

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/security", response_model=CopilotResponse)
async def security_analysis(request: CodeRequest):
    """
    Analisa vulnerabilidades de segurança.

    Verifica:
    - OWASP Top 10
    - Vulnerabilidades de injeção
    - Exposição de dados sensíveis
    - Problemas de autenticação
    """
    try:
        security_copilot = get_copilot("security")

        result = security_copilot.vulnerability_scan(
            request.code,
            request.language,
        )

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em security: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/debug", response_model=CopilotResponse)
async def debug_error(request: DebugRequest):
    """
    Auxilia na depuração de erros.

    Analisa mensagens de erro e stack traces,
    identificando causa raiz e sugerindo correções.
    """
    try:
        debug_copilot = get_copilot("debug")

        result = debug_copilot.analyze_error(
            error_message=request.error_message,
            stack_trace=request.stack_trace,
            code=request.code,
            language=request.language,
        )

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em debug: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/refactor", response_model=CopilotResponse)
async def suggest_refactoring(request: RefactorRequest):
    """
    Sugere refatorações de código.

    Identifica code smells e sugere
    melhorias para o código.
    """
    try:
        refactor_copilot = get_copilot("refactoring")

        result = refactor_copilot.suggest_refactoring(
            request.code,
            request.language,
            focus=request.focus,
        )

        return CopilotResponse(
            success=result.success,
            content=result.content,
            model=result.model,
            metadata=result.metadata,
        )
    except Exception as e:
        logger.error(f"Erro em refactor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
