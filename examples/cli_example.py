#!/usr/bin/env python3
# =============================================================================
# Copilot-IA - CLI de Exemplo
# =============================================================================
"""
Interface de linha de comando para os copilotos.

Uso:
    python cli_example.py review <arquivo>
    python cli_example.py docs <arquivo>
    python cli_example.py test <arquivo>
    python cli_example.py security <arquivo>
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.copilots import (
    CodeReviewerCopilot,
    DocumentationCopilot,
    TestingCopilot,
    SecurityCopilot,
    DebugCopilot,
    RefactoringCopilot,
)
from src.utils import setup_logging

# Configurar
setup_logging(level="INFO")
app = typer.Typer(help="🤖 Copilot-IA - Copilotos de Desenvolvimento")
console = Console()


def read_file_content(file_path: str) -> tuple[str, str]:
    """Lê conteúdo de um arquivo e detecta linguagem."""
    path = Path(file_path)

    if not path.exists():
        console.print(f"[red]Erro: Arquivo não encontrado: {file_path}[/red]")
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")

    # Detectar linguagem
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
    }
    language = ext_map.get(path.suffix.lower(), "text")

    return content, language


def display_result(title: str, content: str, success: bool = True):
    """Exibe resultado formatado."""
    color = "green" if success else "red"
    icon = "✅" if success else "❌"

    console.print(f"\n[bold {color}]{icon} {title}[/bold {color}]")
    console.print("-" * 60)

    # Renderizar como Markdown
    md = Markdown(content)
    console.print(md)


@app.command()
def review(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para revisar"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Revisão rápida (top 5 issues)"),
):
    """📝 Revisa código e identifica problemas."""
    console.print(Panel.fit("🔍 Code Reviewer Copilot", style="blue"))

    content, language = read_file_content(file_path)
    reviewer = CodeReviewerCopilot()

    with console.status("Analisando código..."):
        if quick:
            result = reviewer.quick_review(content, language)
        else:
            result = reviewer.analyze_code(content, language)

    display_result("Revisão de Código", result.content, result.success)


@app.command()
def docs(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para documentar"),
    style: str = typer.Option(
        "google", "--style", "-s", help="Estilo de docstring (google/numpy/sphinx)"
    ),
):
    """📚 Gera documentação para código."""
    console.print(Panel.fit("📖 Documentation Copilot", style="blue"))

    content, language = read_file_content(file_path)
    doc_copilot = DocumentationCopilot()

    with console.status("Gerando documentação..."):
        result = doc_copilot.document_file(file_path)

    display_result("Documentação Gerada", result.content, result.success)


@app.command()
def test(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para criar testes"),
    framework: str = typer.Option("pytest", "--framework", "-f", help="Framework de teste"),
):
    """🧪 Gera testes para código."""
    console.print(Panel.fit("🧪 Testing Copilot", style="blue"))

    content, language = read_file_content(file_path)
    test_copilot = TestingCopilot()

    with console.status("Gerando testes..."):
        result = test_copilot.generate_unit_tests(content, language, framework)

    display_result("Testes Gerados", result.content, result.success)


@app.command()
def security(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para análise de segurança"),
):
    """🔒 Analisa vulnerabilidades de segurança."""
    console.print(Panel.fit("🔒 Security Copilot", style="blue"))

    content, language = read_file_content(file_path)
    security_copilot = SecurityCopilot()

    with console.status("Analisando segurança..."):
        result = security_copilot.vulnerability_scan(content, language)

    display_result("Análise de Segurança", result.content, result.success)


@app.command()
def debug(
    error_message: str = typer.Argument(..., help="Mensagem de erro para analisar"),
    file_path: Optional[str] = typer.Option(
        None, "--file", "-f", help="Arquivo com código relacionado"
    ),
):
    """🐛 Auxilia na depuração de erros."""
    console.print(Panel.fit("🐛 Debug Copilot", style="blue"))

    code = None
    language = "python"

    if file_path:
        code, language = read_file_content(file_path)

    debug_copilot = DebugCopilot()

    with console.status("Analisando erro..."):
        result = debug_copilot.analyze_error(error_message, code=code, language=language)

    display_result("Análise de Debug", result.content, result.success)


@app.command()
def refactor(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para refatorar"),
    focus: Optional[str] = typer.Option(
        None, "--focus", "-f", help="Foco da refatoração (ex: readability,performance)"
    ),
):
    """🔧 Sugere refatorações para o código."""
    console.print(Panel.fit("🔧 Refactoring Copilot", style="blue"))

    content, language = read_file_content(file_path)
    refactor_copilot = RefactoringCopilot()

    focus_list = focus.split(",") if focus else None

    with console.status("Analisando refatorações..."):
        result = refactor_copilot.suggest_refactoring(content, language, focus=focus_list)

    display_result("Sugestões de Refatoração", result.content, result.success)


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Caminho do arquivo para análise completa"),
):
    """📊 Análise completa (review + security + sugestões)."""
    console.print(Panel.fit("📊 Análise Completa", style="blue"))

    content, language = read_file_content(file_path)

    # Executar múltiplos copilotos
    results = []

    # Code Review
    with console.status("[1/3] Revisando código..."):
        reviewer = CodeReviewerCopilot()
        review_result = reviewer.quick_review(content, language)
        results.append(("Code Review", review_result))

    # Security
    with console.status("[2/3] Analisando segurança..."):
        security_copilot = SecurityCopilot()
        security_result = security_copilot.vulnerability_scan(content, language)
        results.append(("Segurança", security_result))

    # Refactoring
    with console.status("[3/3] Sugerindo melhorias..."):
        refactor_copilot = RefactoringCopilot()
        refactor_result = refactor_copilot.identify_smells(content, language)
        results.append(("Refatoração", refactor_result))

    # Exibir resultados
    for title, result in results:
        display_result(title, result.content, result.success)


if __name__ == "__main__":
    app()
