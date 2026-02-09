#!/usr/bin/env python3
# =============================================================================
# Copilot-IA - Exemplo de Uso Básico
# =============================================================================
"""
Exemplo básico de como usar os copilotos de desenvolvimento.

Este script demonstra:
- Inicialização de copilotos
- Revisão de código
- Geração de documentação
- Criação de testes
"""

import os
from pathlib import Path

# Configurar variáveis de ambiente (em produção, use .env)
# os.environ["OPENAI_API_KEY"] = "sua-chave-aqui"

from src.copilots import (
    CodeReviewerCopilot,
    DocumentationCopilot,
    TestingCopilot,
)
from src.utils import setup_logging

# Configurar logging
setup_logging(level="INFO")


def main():
    """Exemplo de uso dos copilotos."""

    # Código de exemplo para análise
    sample_code = '''
def calculate_total(items, discount=0):
    """Calcula o total com desconto."""
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    if discount > 0:
        total = total - (total * discount / 100)
    return total

def process_order(order):
    items = order["items"]
    customer = order["customer"]
    total = calculate_total(items, order.get("discount", 0))
    # TODO: implementar validação
    return {"customer": customer, "total": total, "status": "processed"}
'''

    print("=" * 60)
    print("🤖 COPILOT-IA - Demonstração")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Code Review
    # -------------------------------------------------------------------------
    print("\n📝 1. Revisão de Código")
    print("-" * 40)

    reviewer = CodeReviewerCopilot()
    review_result = reviewer.analyze_code(sample_code, language="python")

    if review_result.success:
        print(review_result.content)
    else:
        print(f"Erro: {review_result.content}")

    # -------------------------------------------------------------------------
    # 2. Geração de Documentação
    # -------------------------------------------------------------------------
    print("\n📚 2. Geração de Documentação")
    print("-" * 40)

    doc_copilot = DocumentationCopilot()
    doc_result = doc_copilot.generate_docstring(
        code="def calculate_total(items, discount=0): ...", language="python", style="google"
    )

    if doc_result.success:
        print(doc_result.content)
    else:
        print(f"Erro: {doc_result.content}")

    # -------------------------------------------------------------------------
    # 3. Geração de Testes
    # -------------------------------------------------------------------------
    print("\n🧪 3. Geração de Testes")
    print("-" * 40)

    test_copilot = TestingCopilot()
    test_result = test_copilot.generate_unit_tests(
        code=sample_code, language="python", framework="pytest"
    )

    if test_result.success:
        print(test_result.content)
    else:
        print(f"Erro: {test_result.content}")

    print("\n" + "=" * 60)
    print("✅ Demonstração concluída!")
    print("=" * 60)


if __name__ == "__main__":
    main()
