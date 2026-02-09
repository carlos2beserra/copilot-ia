#!/usr/bin/env python3
# =============================================================================
# Copilot-IA - Exemplo de Uso do Coordenador
# =============================================================================
"""
Exemplo de como usar o coordenador para orquestrar múltiplos copilotos.

Este script demonstra:
- Registro de copilotos no coordenador
- Análise completa com múltiplos copilotos
- Consolidação de resultados
"""

import os
from pathlib import Path

from src.agents import CopilotCoordinator
from src.agents.coordinator import CopilotType, CoordinatorRequest
from src.copilots import (
    CodeReviewerCopilot,
    SecurityCopilot,
    TestingCopilot,
    DocumentationCopilot,
)
from src.utils import setup_logging

# Configurar logging
setup_logging(level="INFO")


def main():
    """Exemplo de uso do coordenador multiagente."""

    print("=" * 60)
    print("🤖 COPILOT-IA - Coordenador Multiagente")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Inicializar Coordenador e Registrar Copilotos
    # -------------------------------------------------------------------------
    print("\n📋 Inicializando coordenador...")

    coordinator = CopilotCoordinator()

    # Registrar copilotos
    coordinator.register_copilot(CodeReviewerCopilot(), CopilotType.CODE_REVIEWER)
    coordinator.register_copilot(SecurityCopilot(), CopilotType.SECURITY)
    coordinator.register_copilot(TestingCopilot(), CopilotType.TESTING)
    coordinator.register_copilot(DocumentationCopilot(), CopilotType.DOCUMENTATION)

    print(f"✅ Copilotos registrados: {coordinator.get_available_copilots()}")

    # -------------------------------------------------------------------------
    # 2. Código para Análise
    # -------------------------------------------------------------------------
    sample_code = '''
import sqlite3
import hashlib

def authenticate_user(username, password):
    """Autentica um usuário no sistema."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Buscar usuário
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        # Verificar senha
        stored_password = user[2]
        if stored_password == hashlib.md5(password.encode()).hexdigest():
            return {"success": True, "user_id": user[0]}
    
    return {"success": False}


def get_user_data(user_id):
    """Obtém dados do usuário."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
'''

    # -------------------------------------------------------------------------
    # 3. Análise com Detecção Automática de Intenção
    # -------------------------------------------------------------------------
    print("\n🔍 Análise automática (detecção de intenção)...")
    print("-" * 40)

    request = CoordinatorRequest(
        message="Analise este código de autenticação para bugs e vulnerabilidades de segurança",
        context={"code": sample_code, "language": "python"},
    )

    # Detectar intenção
    intents = coordinator.detect_intent(request.message)
    print(f"Intenções detectadas: {intents}")

    # Selecionar copilotos
    selected = coordinator.select_copilots(intents)
    print(f"Copilotos selecionados: {selected}")

    # -------------------------------------------------------------------------
    # 4. Análise com Copilotos Específicos
    # -------------------------------------------------------------------------
    print("\n🎯 Análise com copilotos específicos...")
    print("-" * 40)

    request_specific = CoordinatorRequest(
        message="Faça uma análise completa de segurança e revisão de código",
        context={"code": sample_code, "language": "python"},
        preferred_copilots=[CopilotType.CODE_REVIEWER, CopilotType.SECURITY],
    )

    response = coordinator.process(request_specific)

    print(f"\n📊 Resultado:")
    print(f"  Sucesso: {response.success}")
    print(f"  Copilotos usados: {response.copilots_used}")
    print(f"\n📝 Resumo:")
    print(response.summary)

    if response.recommendations:
        print(f"\n💡 Recomendações:")
        for rec in response.recommendations:
            print(f"  • {rec}")

    # Detalhes por copiloto
    print("\n📋 Detalhes por Copiloto:")
    for copilot_name, result in response.details.items():
        print(f"\n  [{copilot_name}]")
        print(f"  Status: {'✅' if result.get('success') else '❌'}")
        content = result.get("content", "")[:500]
        print(f"  Prévia: {content}...")

    print("\n" + "=" * 60)
    print("✅ Análise coordenada concluída!")
    print("=" * 60)


if __name__ == "__main__":
    main()
