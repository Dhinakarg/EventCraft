"""Architectural boundary tests enforcing unidirectional dependency layers."""

import ast
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent / "app" / "engine"
SERVICES_DIR = Path(__file__).resolve().parent.parent / "app" / "services"

FORBIDDEN_ENGINE_PREFIXES = ("app.api", "app.services", "app.ai")
FORBIDDEN_SERVICES_PREFIXES = ("app.api",)


def _get_imports_from_file(file_path: Path) -> list[str]:
    """Parse python source using AST and extract all module import targets."""
    tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def test_engine_has_no_dependencies_on_higher_layers() -> None:
    """Verify app.engine never imports from app.api, app.services, or app.ai."""
    assert ENGINE_DIR.exists(), f"Engine directory not found at {ENGINE_DIR}"
    py_files = list(ENGINE_DIR.rglob("*.py"))
    assert len(py_files) >= 5, "Expected engine modules to be present"

    violations: list[str] = []
    for py_file in py_files:
        imported_modules = _get_imports_from_file(py_file)
        for mod in imported_modules:
            for forbidden in FORBIDDEN_ENGINE_PREFIXES:
                if mod == forbidden or mod.startswith(f"{forbidden}."):
                    rel_path = py_file.relative_to(ENGINE_DIR.parent.parent)
                    violations.append(f"{rel_path} imports forbidden '{mod}'")

    assert not violations, "Layer boundary violations detected:\n" + "\n".join(violations)


def test_services_has_no_dependencies_on_api_layer() -> None:
    """Verify app.services never imports from app.api."""
    assert SERVICES_DIR.exists(), f"Services directory not found at {SERVICES_DIR}"
    py_files = list(SERVICES_DIR.rglob("*.py"))
    assert len(py_files) >= 2, "Expected services modules to be present"

    violations: list[str] = []
    for py_file in py_files:
        imported_modules = _get_imports_from_file(py_file)
        for mod in imported_modules:
            for forbidden in FORBIDDEN_SERVICES_PREFIXES:
                if mod == forbidden or mod.startswith(f"{forbidden}."):
                    rel_path = py_file.relative_to(SERVICES_DIR.parent.parent)
                    violations.append(f"{rel_path} imports forbidden '{mod}'")

    assert not violations, "Layer boundary violations detected:\n" + "\n".join(violations)
