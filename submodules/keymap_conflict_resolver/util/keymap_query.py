"""Read-only bpy query functions for keymap conflict detection.

Conflicts are detected WITHIN a single keymap only. Two KMIs in different
keymaps are never considered conflicts because Blender resolves keymaps
hierarchically (most-specific context wins).

All functions are pure readers — they never write to properties, call
operators, or modify keymaps.
"""

from __future__ import annotations

import bpy

from .keymap_data import (
    ConflictGroup,
    ConflictItem,
    KeySignature,
)


def make_signature(kmi: bpy.types.KeyMapItem) -> KeySignature:
    """Extract a KeySignature from a live KeyMapItem."""
    return KeySignature(
        key_type=kmi.type,
        value=kmi.value,
        shift=bool(kmi.shift),
        ctrl=bool(kmi.ctrl),
        alt=bool(kmi.alt),
        oskey=bool(getattr(kmi, "oskey", False)),
        key_modifier=str(kmi.key_modifier) if kmi.key_modifier else "NONE",
        any=bool(kmi.any),
        map_type=kmi.map_type,
        direction=getattr(kmi, "direction", "ANY"),
    )


def get_kmi_source(kmi: bpy.types.KeyMapItem) -> str:
    """Determine where a keymap item originates.

    Returns:
        "user"    — is_user_defined or is_user_modified
        "addon"   — operator idname contains addon-style namespace (heuristic)
        "blender" — built-in Blender default
    """
    if kmi.is_user_defined:
        return "user"
    if kmi.is_user_modified:
        return "user"
    return "blender"


def iter_real_kmis(km: bpy.types.KeyMap):
    """Yield keymap items that have a real (non-NONE) key type.

    Skips items with type NONE or TEXTINPUT.
    Does NOT filter by kmi.active — we want to show inactive items too
    so the user can see the full picture.
    """
    for kmi in km.keymap_items:
        if kmi.type in {"NONE", "TEXTINPUT"}:
            continue
        yield kmi


def find_conflict_groups(kc: bpy.types.KeyConfig) -> list[ConflictGroup]:
    """Scan a keyconfig and return all conflict groups.

    A conflict group is created when 2+ items WITHIN THE SAME KEYMAP share
    the same key signature. Items in different keymaps are never considered
    conflicts because Blender resolves keymaps hierarchically.

    Modal keymaps are skipped (tool-specific modal event mappings).
    """
    groups: list[ConflictGroup] = []

    for km in kc.keymaps:
        if km.is_modal:
            continue

        # Build per-keymap signature index
        sig_index: dict[tuple, list[bpy.types.KeyMapItem]] = {}
        for kmi in iter_real_kmis(km):
            sig: KeySignature = make_signature(kmi)
            sig_tuple: tuple = sig.as_tuple()
            if sig_tuple not in sig_index:
                sig_index[sig_tuple] = []
            sig_index[sig_tuple].append(kmi)

        # Create conflict groups for signatures with 2+ items
        for sig_tuple, kmis in sig_index.items():
            if len(kmis) < 2:
                continue

            sig = make_signature(kmis[0])
            label: str = f"[{km.name}] {sig.to_string()}"

            items: list[ConflictItem] = []
            for kmi in kmis:
                items.append(ConflictItem(
                    km_name=km.name,
                    kmi_id=kmi.id,
                    kmi_idname=kmi.idname,
                    kmi_label=kmi.name,
                    source=get_kmi_source(kmi),
                    is_active=kmi.active,
                ))

            active_count: int = sum(1 for it in items if it.is_active)
            resolved: bool = active_count <= 1

            groups.append(ConflictGroup(
                km_name=km.name,
                signature=sig,
                signature_label=label,
                items=items,
                resolved=resolved,
            ))

    return groups


def is_group_resolved(group: ConflictGroup) -> bool:
    """Return True if the group is resolved (at most 1 active item)."""
    return sum(1 for item in group.items if item.is_active) <= 1


def build_group_label(sig: KeySignature, km_name: str) -> str:
    """Build a human-readable label for a conflict group."""
    return f"[{km_name}] {sig.to_string()}"
