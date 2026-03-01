"""Addon keymap items for LKS Keymap Conflict Resolver.

Provides the ``addon_keymaps`` list consumed by ``draw_addon_keymaps()``.
In the published build this list is empty (no real addon keymaps).
During local development the ``dev/`` module appends mock items to it.
"""

from __future__ import annotations

import bpy

# Stores (KeyMap, KeyMapItem) tuples for the addon keymaps display.
# The dev/ module appends mock items here during local development.
addon_keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []


def register() -> None:
    """Register addon keymaps (currently none — dev/ adds mocks)."""
    pass


def unregister() -> None:
    """Remove all registered keymap items."""
    for km, kmi in reversed(addon_keymaps):
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
