#!/usr/bin/env python3
# =============================================================================
# Copilot-IA - Cliente Python
# =============================================================================
"""
Cliente simples para integrar o Copilot-IA em outros projetos.

Copie este arquivo para o seu projeto e use assim:

    from copilot_client import CopilotClient
    
    client = CopilotClient()
    resultado = client.review_file("src/main.py")
    print(resultado)

Requisitos:
    pip install httpx
"""

import json
from pathlib import Path
from typing import Optional

try:
    import httpx
except ImportError:
    print("❌ Instale o httpx: pip install httpx")
    raise


class CopilotClient:
    """
    Cliente para a API do Copilot-IA.
    
    Permite integrar o Copilot-IA em qualquer projeto Python.
    
    Attributes:
        base_url: URL base da API (padrão: http://localhost:8000)
    
    Example:
        >>> client = CopilotClient()
        >>> result = client.review("def soma(a,b): return a+b")
        >>> print(result["content"])
    """
    
    # Mapeamento de extensões para linguagens
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
    }
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 120):
        """
        Inicializa o cliente.
        
        Args:
            base_url: URL da API do Copilot-IA
            timeout: Timeout para requisições em segundos
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout)
    
    def _detect_language(self, file_path: str) -> str:
        """Detecta a linguagem pelo caminho do arquivo."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_MAP.get(ext, "text")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Faz uma requisição à API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {"error": f"Não foi possível conectar à API em {self.base_url}. Verifique se está rodando."}
        except httpx.HTTPStatusError as e:
            return {"error": f"Erro HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    # -------------------------------------------------------------------------
    # Métodos Principais
    # -------------------------------------------------------------------------
    
    def health(self) -> dict:
        """
        Verifica se a API está funcionando.
        
        Returns:
            dict com status da API
        
        Example:
            >>> client.health()
            {"status": "healthy", "version": "0.1.0"}
        """
        return self._request("GET", "/health")
    
    def review(
        self, 
        code: str, 
        language: str = "python", 
        quick: bool = False
    ) -> dict:
        """
        Revisa código e retorna análise detalhada.
        
        Args:
            code: Código fonte para revisar
            language: Linguagem de programação
            quick: Se True, faz revisão rápida (top 5 issues)
        
        Returns:
            dict com resultado da revisão
        
        Example:
            >>> result = client.review("def soma(a,b): return a+b")
            >>> print(result["content"])
        """
        return self._request("POST", "/api/review", json={
            "code": code,
            "language": language,
            "quick": quick
        })
    
    def review_file(self, file_path: str, quick: bool = False) -> dict:
        """
        Revisa um arquivo de código.
        
        Args:
            file_path: Caminho para o arquivo
            quick: Se True, faz revisão rápida
        
        Returns:
            dict com resultado da revisão
        
        Example:
            >>> result = client.review_file("src/main.py")
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"Arquivo não encontrado: {file_path}"}
        
        code = path.read_text(encoding="utf-8")
        language = self._detect_language(file_path)
        
        return self.review(code, language, quick)
    
    def generate_tests(
        self, 
        code: str, 
        language: str = "python",
        framework: str = "pytest"
    ) -> dict:
        """
        Gera testes automaticamente para o código.
        
        Args:
            code: Código fonte
            language: Linguagem de programação
            framework: Framework de teste (pytest, unittest, jest, etc)
        
        Returns:
            dict com código de testes gerado
        
        Example:
            >>> tests = client.generate_tests(open("src/calc.py").read())
            >>> print(tests["content"])
        """
        return self._request("POST", "/api/test", json={
            "code": code,
            "language": language,
            "framework": framework
        })
    
    def generate_tests_for_file(
        self, 
        file_path: str, 
        framework: str = "pytest"
    ) -> dict:
        """
        Gera testes para um arquivo.
        
        Args:
            file_path: Caminho para o arquivo
            framework: Framework de teste
        
        Returns:
            dict com código de testes gerado
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"Arquivo não encontrado: {file_path}"}
        
        code = path.read_text(encoding="utf-8")
        language = self._detect_language(file_path)
        
        # Mapear linguagem para framework padrão
        framework_map = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
        }
        if framework == "auto":
            framework = framework_map.get(language, "pytest")
        
        return self.generate_tests(code, language, framework)
    
    def security_scan(self, code: str, language: str = "python") -> dict:
        """
        Analisa código em busca de vulnerabilidades de segurança.
        
        Args:
            code: Código fonte
            language: Linguagem de programação
        
        Returns:
            dict com análise de segurança
        
        Example:
            >>> scan = client.security_scan(open("src/auth.py").read())
            >>> print(scan["content"])
        """
        return self._request("POST", "/api/security", json={
            "code": code,
            "language": language
        })
    
    def security_scan_file(self, file_path: str) -> dict:
        """
        Analisa segurança de um arquivo.
        
        Args:
            file_path: Caminho para o arquivo
        
        Returns:
            dict com análise de segurança
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"Arquivo não encontrado: {file_path}"}
        
        code = path.read_text(encoding="utf-8")
        language = self._detect_language(file_path)
        
        return self.security_scan(code, language)
    
    def generate_docs(
        self, 
        code: str, 
        language: str = "python",
        style: str = "google"
    ) -> dict:
        """
        Gera documentação para o código.
        
        Args:
            code: Código fonte
            language: Linguagem de programação
            style: Estilo de docstring (google, numpy, sphinx)
        
        Returns:
            dict com código documentado
        
        Example:
            >>> docs = client.generate_docs("def soma(a, b): return a + b")
            >>> print(docs["content"])
        """
        return self._request("POST", "/api/docs", json={
            "code": code,
            "language": language,
            "style": style
        })
    
    def refactor(
        self, 
        code: str, 
        language: str = "python",
        focus: Optional[list] = None
    ) -> dict:
        """
        Sugere refatorações para o código.
        
        Args:
            code: Código fonte
            language: Linguagem de programação
            focus: Lista de focos (readability, performance, etc)
        
        Returns:
            dict com sugestões de refatoração
        """
        return self._request("POST", "/api/refactor", json={
            "code": code,
            "language": language,
            "focus": focus or []
        })
    
    def debug(
        self, 
        error_message: str, 
        code: Optional[str] = None,
        language: str = "python"
    ) -> dict:
        """
        Ajuda a debugar um erro.
        
        Args:
            error_message: Mensagem de erro ou stack trace
            code: Código relacionado (opcional)
            language: Linguagem de programação
        
        Returns:
            dict com análise e sugestões de correção
        
        Example:
            >>> debug = client.debug("IndexError: list index out of range")
            >>> print(debug["content"])
        """
        return self._request("POST", "/api/debug", json={
            "error": error_message,
            "code": code,
            "language": language
        })
    
    # -------------------------------------------------------------------------
    # Utilitários
    # -------------------------------------------------------------------------
    
    def is_available(self) -> bool:
        """
        Verifica se a API está disponível.
        
        Returns:
            True se a API estiver respondendo
        """
        result = self.health()
        return "error" not in result and result.get("status") == "healthy"
    
    def __repr__(self) -> str:
        return f"<CopilotClient(base_url='{self.base_url}')>"


# =============================================================================
# CLI para uso direto
# =============================================================================
def main():
    """CLI simples para testar o cliente."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cliente Copilot-IA")
    parser.add_argument("--url", default="http://localhost:8000", help="URL da API")
    
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # health
    subparsers.add_parser("health", help="Verificar status da API")
    
    # review
    review_parser = subparsers.add_parser("review", help="Revisar código")
    review_parser.add_argument("file", help="Arquivo para revisar")
    review_parser.add_argument("--quick", "-q", action="store_true", help="Revisão rápida")
    
    # test
    test_parser = subparsers.add_parser("test", help="Gerar testes")
    test_parser.add_argument("file", help="Arquivo para gerar testes")
    test_parser.add_argument("--framework", "-f", default="pytest", help="Framework de teste")
    
    # security
    security_parser = subparsers.add_parser("security", help="Análise de segurança")
    security_parser.add_argument("file", help="Arquivo para analisar")
    
    args = parser.parse_args()
    
    client = CopilotClient(args.url)
    
    if args.command == "health":
        result = client.health()
        print(json.dumps(result, indent=2))
    
    elif args.command == "review":
        result = client.review_file(args.file, quick=args.quick)
        if "content" in result:
            print(result["content"])
        else:
            print(json.dumps(result, indent=2))
    
    elif args.command == "test":
        result = client.generate_tests_for_file(args.file, framework=args.framework)
        if "content" in result:
            print(result["content"])
        else:
            print(json.dumps(result, indent=2))
    
    elif args.command == "security":
        result = client.security_scan_file(args.file)
        if "content" in result:
            print(result["content"])
        else:
            print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

