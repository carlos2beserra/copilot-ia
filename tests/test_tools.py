# =============================================================================
# Copilot-IA - Testes das Ferramentas
# =============================================================================
"""
Testes unitários para as ferramentas (tools).
"""


import pytest

from src.tools.code_analysis import CodeAnalysisTool, CodeMetrics
from src.tools.file_operations import FileOperationsTool
from src.tools.search_tools import SearchTool


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_python_code():
    """Código Python de exemplo para testes."""
    return '''
import os
from pathlib import Path

def calculate_sum(numbers: list[int]) -> int:
    """Calcula a soma de uma lista de números."""
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    """Calculadora simples."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        """Soma dois números."""
        result = a + b
        self.history.append(result)
        return result
    
    def multiply(self, a: int, b: int) -> int:
        """Multiplica dois números."""
        return a * b
'''


@pytest.fixture
def code_analysis_tool():
    """Instância da ferramenta de análise de código."""
    return CodeAnalysisTool()


@pytest.fixture
def file_operations_tool(tmp_path):
    """Instância da ferramenta de operações de arquivo."""
    return FileOperationsTool(workspace_root=str(tmp_path))


@pytest.fixture
def search_tool(tmp_path):
    """Instância da ferramenta de busca."""
    return SearchTool(workspace_root=str(tmp_path))


# -----------------------------------------------------------------------------
# Testes - CodeAnalysisTool
# -----------------------------------------------------------------------------
class TestCodeAnalysisTool:
    """Testes para CodeAnalysisTool."""

    def test_get_metrics(self, code_analysis_tool, sample_python_code):
        """Testa cálculo de métricas."""
        metrics = code_analysis_tool.get_metrics(sample_python_code, "python")

        assert isinstance(metrics, CodeMetrics)
        assert metrics.lines_of_code > 0
        assert metrics.num_functions >= 1
        assert metrics.num_classes >= 1
        assert metrics.num_imports >= 2

    def test_extract_functions(self, code_analysis_tool, sample_python_code):
        """Testa extração de funções."""
        functions = code_analysis_tool.extract_functions(sample_python_code)

        assert len(functions) >= 3  # calculate_sum, add, multiply

        func_names = [f.name for f in functions]
        assert "calculate_sum" in func_names
        assert "add" in func_names
        assert "multiply" in func_names

    def test_extract_classes(self, code_analysis_tool, sample_python_code):
        """Testa extração de classes."""
        classes = code_analysis_tool.extract_classes(sample_python_code)

        assert len(classes) >= 1
        assert classes[0].name == "Calculator"
        assert "add" in classes[0].methods
        assert "multiply" in classes[0].methods

    def test_get_imports(self, code_analysis_tool, sample_python_code):
        """Testa extração de imports."""
        imports = code_analysis_tool.get_imports(sample_python_code)

        assert "os" in imports
        assert "pathlib.Path" in imports

    def test_detect_language(self, code_analysis_tool):
        """Testa detecção de linguagem."""
        assert code_analysis_tool.detect_language("main.py") == "python"
        assert code_analysis_tool.detect_language("app.js") == "javascript"
        assert code_analysis_tool.detect_language("index.ts") == "typescript"
        assert code_analysis_tool.detect_language("Main.java") == "java"

    def test_find_patterns(self, code_analysis_tool, sample_python_code):
        """Testa busca de padrões."""
        patterns = ["def ", "class ", "return"]
        results = code_analysis_tool.find_patterns(sample_python_code, patterns)

        assert "def " in results
        assert len(results["def "]) >= 3
        assert "class " in results
        assert len(results["class "]) >= 1


# -----------------------------------------------------------------------------
# Testes - FileOperationsTool
# -----------------------------------------------------------------------------
class TestFileOperationsTool:
    """Testes para FileOperationsTool."""

    def test_read_file(self, file_operations_tool, tmp_path):
        """Testa leitura de arquivo."""
        # Criar arquivo de teste
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        content = file_operations_tool.read_file("test.py")
        assert content == "print('hello')"

    def test_read_file_not_found(self, file_operations_tool):
        """Testa erro ao ler arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            file_operations_tool.read_file("inexistente.py")

    def test_list_directory(self, file_operations_tool, tmp_path):
        """Testa listagem de diretório."""
        # Criar arquivos de teste
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "subdir").mkdir()

        items = file_operations_tool.list_directory(".")

        assert len(items) >= 3
        names = [item.name for item in items]
        assert "file1.py" in names
        assert "file2.py" in names
        assert "subdir" in names

    def test_get_directory_structure(self, file_operations_tool, tmp_path):
        """Testa geração de estrutura de diretório."""
        # Criar estrutura
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").touch()
        (tmp_path / "tests").mkdir()

        structure = file_operations_tool.get_directory_structure(".", max_depth=2)

        assert "src" in structure
        assert "tests" in structure

    def test_find_files(self, file_operations_tool, tmp_path):
        """Testa busca de arquivos por padrão."""
        # Criar arquivos
        (tmp_path / "main.py").touch()
        (tmp_path / "test_main.py").touch()
        (tmp_path / "utils.py").touch()

        py_files = file_operations_tool.find_files("*.py")
        assert len(py_files) >= 3

        test_files = file_operations_tool.find_files("test_*.py")
        assert len(test_files) >= 1


# -----------------------------------------------------------------------------
# Testes - SearchTool
# -----------------------------------------------------------------------------
class TestSearchTool:
    """Testes para SearchTool."""

    def test_search_text(self, search_tool, tmp_path):
        """Testa busca de texto."""
        # Criar arquivo com conteúdo
        test_file = tmp_path / "search_test.py"
        test_file.write_text("def hello():\n    return 'world'\n\ndef goodbye():\n    pass")

        results = search_tool.search_text("def ", ".")

        assert len(results) >= 2
        assert any("hello" in r.line_content for r in results)
        assert any("goodbye" in r.line_content for r in results)

    def test_search_regex(self, search_tool, tmp_path):
        """Testa busca com regex."""
        test_file = tmp_path / "regex_test.py"
        test_file.write_text("# TODO: implementar\n# FIXME: bug aqui\nprint('ok')")

        results = search_tool.search_regex(r"(TODO|FIXME)", ".")

        assert len(results) >= 2

    def test_find_todos(self, search_tool, tmp_path):
        """Testa busca de TODOs."""
        test_file = tmp_path / "todo_test.py"
        test_file.write_text("# TODO: fazer isso\n# FIXME: corrigir bug\n# HACK: gambiarra")

        todos = search_tool.find_todos(".")

        assert len(todos) >= 3


# -----------------------------------------------------------------------------
# Testes de Integração
# -----------------------------------------------------------------------------
class TestToolsIntegration:
    """Testes de integração entre ferramentas."""

    def test_analyze_and_search(self, code_analysis_tool, search_tool, tmp_path):
        """Testa análise combinada de código e busca."""
        # Criar arquivo Python
        code = '''
def process_data(data: list) -> dict:
    """Processa dados."""
    # TODO: adicionar validação
    result = {}
    for item in data:
        result[item] = len(item)
    return result
'''
        test_file = tmp_path / "process.py"
        test_file.write_text(code)

        # Configurar search_tool para usar o tmp_path
        search_tool.workspace_root = tmp_path

        # Analisar código
        metrics = code_analysis_tool.get_metrics(code, "python")
        assert metrics.num_functions >= 1

        # Buscar TODOs
        todos = search_tool.find_todos(".")
        assert len(todos) >= 1
