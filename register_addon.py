"""Central registration orchestrator for LKS Keymap Conflict Resolver.

Registers addon preferences, local modules (properties → ops → keymaps),
and discovers/registers any submodules in the submodules/ directory.

An optional ``dev/`` package is auto-discovered for local-only mock data,
test operators, or debug panels.  It is excluded from published builds via
``.remoteignore`` and ``blender_manifest.toml``.

The conflict-resolver UI lives in Edit → Preferences → Add-ons, so no
sidebar panel is needed.
"""

from __future__ import annotations

import importlib
import traceback
from pathlib import Path

# Local modules
from . import properties
from . import ops
from . import keymaps
from . import addon_prefs

# Optional dev module (excluded from published builds)
try:
    from . import dev as _dev_module  # type: ignore[import-not-found]
except ImportError:
    _dev_module = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Submodule discovery
# ---------------------------------------------------------------------------

def _discover_submodules() -> list:
    """Find all submodule packages under submodules/ that have register/unregister."""
    submodules_dir: Path = Path(__file__).parent / "submodules"
    found: list = []

    if not submodules_dir.exists():
        return found

    package: str = __package__ or ""

    for child in sorted(submodules_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.startswith("."):
            continue
        if not (child / "__init__.py").exists():
            continue

        try:
            mod = importlib.import_module(f"{package}.submodules.{child.name}")
            if hasattr(mod, "register") and hasattr(mod, "unregister"):
                found.append(mod)
        except Exception as exc:
            print(
                f"[{package}] WARNING: Failed to import submodule '{child.name}': {exc}")

    return found


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_submodules: list = []


def register_addon() -> None:
    """Register all local modules and discovered submodules."""
    global _submodules

    # 1. Register local modules (order: properties → ops → keymaps → addon prefs)
    properties.register()
    ops.register()
    keymaps.register()

    # 2. Discover and register submodules (operators + properties only, no panels)
    _submodules = _discover_submodules()

    for submod in _submodules:
        try:
            submod.register()
        except Exception as exc:
            print(
                f"[{__package__}] ERROR registering submodule '{submod.__name__}': {exc}")
            traceback.print_exc()

    # 3. Register addon preferences last (depends on submodule draw_utils)
    addon_prefs.register()

    # 4. Dev module (optional — absent in published builds)
    if _dev_module is not None:
        try:
            _dev_module.register()
        except Exception as exc:
            print(f"[{__package__}] WARNING: dev module register failed: {exc}")
            traceback.print_exc()


def unregister_addon() -> None:
    """Unregister in reverse order: dev → prefs → submodules → local modules."""
    global _submodules

    # Dev module first (registered last, unregistered first)
    if _dev_module is not None:
        try:
            _dev_module.unregister()
        except Exception as exc:
            print(f"[{__package__}] WARNING: dev module unregister failed: {exc}")
            traceback.print_exc()

    addon_prefs.unregister()

    # Submodules in reverse
    for submod in reversed(_submodules):
        try:
            submod.unregister()
        except Exception as exc:
            print(
                f"[{__package__}] ERROR unregistering submodule '{submod.__name__}': {exc}")
            traceback.print_exc()

    _submodules.clear()

    # Local modules in reverse order
    keymaps.unregister()
    ops.unregister()
    properties.unregister()
