"""Registration for Keymap Conflict Resolver submodule.

Registers operators, UIList, and property classes.
No sidebar panel — consuming addons embed UI via draw_utils.
"""

from __future__ import annotations

import importlib
import bpy

from . import properties as _properties_module
from . import draw_utils as _draw_utils_module
from .ops import (
    lks_ot_scan,
    lks_ot_purge_duplicates,
    lks_ot_toggle_addon_warning,
    lks_ot_show_info,
)


_classes: tuple = (
    _draw_utils_module.LKS_UL_KcrConflictGroups,
    lks_ot_scan.LKS_OT_ScanKeymapConflicts,
    lks_ot_purge_duplicates.LKS_OT_PurgeExactDuplicates,
    lks_ot_toggle_addon_warning.LKS_OT_KcrToggleAddonWarning,
    lks_ot_show_info.LKS_OT_KcrShowInfo,
)


def register() -> None:
    """Register all operator and property classes."""
    _properties_module.register()
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister all classes in reverse order."""
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    _properties_module.unregister()


def reload() -> None:
    """Reload all child modules for hot-reload during development."""
    global _classes

    # Reload deepest dependencies first
    from .util import keymap_data, keymap_query
    importlib.reload(keymap_data)
    importlib.reload(keymap_query)
    importlib.reload(_properties_module)
    importlib.reload(lks_ot_scan)
    importlib.reload(lks_ot_purge_duplicates)
    importlib.reload(lks_ot_toggle_addon_warning)
    importlib.reload(lks_ot_show_info)
    importlib.reload(_draw_utils_module)

    # Rebuild class tuple with fresh references after reload
    _classes = (
        _draw_utils_module.LKS_UL_KcrConflictGroups,
        lks_ot_scan.LKS_OT_ScanKeymapConflicts,
        lks_ot_purge_duplicates.LKS_OT_PurgeExactDuplicates,
        lks_ot_toggle_addon_warning.LKS_OT_KcrToggleAddonWarning,
        lks_ot_show_info.LKS_OT_KcrShowInfo,
    )
