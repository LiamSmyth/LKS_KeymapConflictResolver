"""Keymap Conflict Resolver — Shared Blender submodule.

This module follows the submodule contract:
    register()    — Register operator and property classes
    unregister()  — Unregister all classes
    reload()      — importlib.reload all child modules

Consuming addons embed UI via the draw utilities::

    from .submodules.keymap_conflict_resolver.draw_utils import (
        draw_resolver_button,
        draw_addon_keymaps,
    )

Can be used standalone or linked into any addon via directory junction.
"""

from __future__ import annotations

import importlib


def _get_registrar():
    """Return the register module, using importlib to avoid reload-cycle ambiguity."""
    return importlib.import_module(".register", package=__package__)


def register() -> None:
    """Register all operator and property classes in this submodule."""
    _get_registrar().register()


def unregister() -> None:
    """Unregister all classes in this submodule."""
    _get_registrar().unregister()


def reload() -> None:
    """Reload all child modules for hot-reload during development."""
    _get_registrar().reload()
