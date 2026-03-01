"""Addon preferences for LKS Keymap Conflict Resolver.

The full conflict resolver is embedded inline in
Edit → Preferences → Add-ons → LKS Keymap Conflict Resolver dropdown.
"""

from __future__ import annotations

import bpy


class LKS_KCR_AddonPreferences(bpy.types.AddonPreferences):
    """Preferences panel for the Keymap Conflict Resolver addon."""

    bl_idname: str = __package__  # matches the addon module name

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Import lazily so the draw call works even if the submodule
        # was reloaded after registration.
        from .submodules.keymap_conflict_resolver.draw_utils import (
            draw_conflict_resolver,
            draw_addon_keymaps,
        )
        from . import keymaps

        # Path 1: Blender-wide conflict resolver
        draw_conflict_resolver(layout)

        layout.separator()

        # Path 2: Per-addon keymap display with inline conflict warnings
        draw_addon_keymaps(layout, keymaps.addon_keymaps)


_classes: tuple = (
    LKS_KCR_AddonPreferences,
)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
