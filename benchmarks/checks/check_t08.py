"""Check T08. Usage: python check_t08.py <workdir> <fixture_dir>."""

import ast
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _inventory_check import report, verify_tests


def uses_shared_validator(nodes: list[ast.AST]) -> bool:
    module_bindings = set()
    for node in nodes:
        if isinstance(node, ast.ImportFrom):
            source = (node.level, node.module)
            if source in {(1, "validation"), (0, "inventory.validation")} and any(
                alias.name == "validate_sku" for alias in node.names
            ):
                return True
            if source in {(1, None), (0, "inventory")}:
                module_bindings.update(
                    alias.asname or alias.name for alias in node.names
                    if alias.name == "validation"
                )
        elif isinstance(node, ast.Import):
            module_bindings.update(
                alias.asname or alias.name for alias in node.names
                if alias.name == "inventory.validation"
            )

    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "validate_sku"
        and ast.unparse(node.func.value) in module_bindings
        for node in nodes
    )


def check(workdir: Path) -> str | None:
    """Require one shared validator and exercise the public entry points."""
    inventory = workdir / "inventory"
    validation = inventory / "validation.py"
    if not validation.is_file():
        return "inventory/validation.py missing"
    if not any(
        isinstance(node, ast.FunctionDef) and node.name == "validate_sku"
        for node in ast.parse(validation.read_bytes()).body
    ):
        return "inventory/validation.py must define validate_sku"

    for name in ("store.py", "pricing.py"):
        tree = ast.parse((inventory / name).read_bytes())
        nodes = list(ast.walk(tree))
        if not uses_shared_validator(nodes):
            return f"{name} must import validate_sku directly or call it through inventory.validation"
        for node in nodes:
            if (
                isinstance(node, ast.Import) and any(alias.name == "re" for alias in node.names)
                or isinstance(node, ast.ImportFrom) and node.module == "re" and node.level == 0
                or isinstance(node, ast.Constant) and isinstance(node.value, str)
                and ("[A-Z]" in node.value or "invalid sku" in node.value.lower())
                or isinstance(node, ast.FunctionDef) and "sku" in node.name.lower()
                and any(word in node.name.lower() for word in ("valid", "check", "normal"))
            ):
                return f"{name} still contains local SKU validation"
    return verify_tests(workdir, "T08")


if __name__ == "__main__":
    try:
        reason = check(Path(sys.argv[1]).resolve())
    except (OSError, UnicodeError, SyntaxError) as exc:
        reason = str(exc)
    sys.exit(report(reason))
