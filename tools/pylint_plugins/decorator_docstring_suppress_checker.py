"""Pylint plugin to mute warnings about missing docstrings on overridden methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from astroid import MANAGER, Const, FunctionDef  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from pylint.lint import PyLinter


def register(_: PyLinter) -> None:
    """Auto registers the transformer during initialization."""


DISABLING_DECORATORS = {"typing.override", "typing_extensions.override"}


def should_add_docstring(func: FunctionDef) -> bool:
    """
    Check if the function should have a docstring.

    Args:
        func: The function to check.

    Returns:
        True if the function should have a docstring, False otherwise.
    """

    return (
        any(decorator in func.decoratornames() for decorator in DISABLING_DECORATORS)
        and not func.doc_node
    )


def generate_docstring(func: FunctionDef) -> str:
    """
    Generate a docstring for the function.

    Args:
        func: The function to generate a docstring for.

    Returns:
        The docstring for the function.
    """

    res = f"Overrides base class method {func.name}.\n"
    if func.args:
        res += "\nArgs:\n"
        cnt = 1
        for arg in func.args.args:  # type: ignore[attr-defined]
            res += f"    {arg.name}: the arg number {cnt}.\n"
            cnt += 1
    if func.returns:  # type: ignore[attr-defined]
        res += "\nReturns:\n    Some value needed.\n"
    return res


def transform(
    node: FunctionDef,
    infer_function: Any = None,  # noqa: ARG001, ANN401 pylint: disable=unused-argument
) -> FunctionDef | None:
    """
    Transform the function to add a docstring.

    Args:
        node: The function to transform.
        infer_function: Unused inference function parameter.
    """

    if should_add_docstring(node):
        docstring_content = generate_docstring(node)
        # Create a new Const node for the docstring
        docstring_node = Const(value=docstring_content)
        docstring_node.parent = node

        # Set the doc_node attribute directly
        node.doc_node = docstring_node


MANAGER.register_transform(FunctionDef, transform)
