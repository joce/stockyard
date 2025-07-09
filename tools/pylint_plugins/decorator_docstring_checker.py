"""
Pylint plugin to exclude elements from docstring checking based on decorators.

This plugin extends the basic checker to add a new parameter
`no-docstring-decorator-rgx` that allows excluding elements decorated with specific
decorators from docstring checks.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Final

import regex
from astroid import nodes  # type: ignore[import-untyped]
from pylint.checkers.base.basic_checker import BasicChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class DecoratorDocstringChecker(BasicChecker):
    """Checker that excludes decorated elements from docstring checks."""

    name: Final[str] = "decorator-docstring"
    msgs: Final[dict[str, Any]] = {}
    options = (
        (
            "no-docstring-decorator-rgx",
            {
                "default": "",
                "type": "regexp",
                "metavar": "<regexp>",
                "help": "Regular expression which should only match decorator names "
                "that exclude the decorated element from docstring checks.",
            },
        ),
    )

    def __init__(self, linter: PyLinter) -> None:
        """Initialize the checker."""
        super().__init__(linter)
        self._decorator_pattern: regex.Pattern[str] | None = None

    @override
    def open(self) -> None:
        super().open()
        # Access config through the linter
        config_value = getattr(self.linter.config, "no_docstring_decorator_rgx", "")
        if config_value:
            self._decorator_pattern = regex.compile(config_value)
        else:
            self._decorator_pattern = None

    def _has_excluded_decorator(self, node: nodes.FunctionDef | nodes.ClassDef) -> bool:
        """
        Check if the node has any decorators that should exclude it from checks.

        Args:
            node: The function or class node to check.

        Returns:
            True if the node has an excluded decorator, False otherwise.
        """
        if not self._decorator_pattern or not node.decorators:
            return False

        for decorator in node.decorators.nodes:
            # Handle different types of decorators
            if isinstance(decorator, nodes.Name):
                decorator_name = decorator.name
            elif isinstance(decorator, nodes.Attribute):
                decorator_name = decorator.attrname
            elif isinstance(decorator, nodes.Call):
                # For decorators with arguments like @decorator()
                if isinstance(decorator.func, nodes.Name):
                    decorator_name = decorator.func.name
                elif isinstance(decorator.func, nodes.Attribute):
                    decorator_name = decorator.func.attrname
                else:
                    continue
            else:
                continue

            if self._decorator_pattern.match(decorator_name):
                return True

        return False

    @override
    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        if self._has_excluded_decorator(node):
            # Skip docstring checks for this function
            return

        # Call the parent method to perform normal checks
        super().visit_functiondef(node)

    @override
    def visit_classdef(self, node: nodes.ClassDef) -> None:  # type: ignore[override]
        if self._has_excluded_decorator(node):
            # Skip docstring checks for this class
            return

        # Call the parent method to perform normal checks
        super().visit_classdef(node)


def register(linter: PyLinter) -> None:
    """
    Register the checker with pylint.

    Args:
        linter (PyLinter): The pylint linter.
    """
    linter.register_checker(DecoratorDocstringChecker(linter))
