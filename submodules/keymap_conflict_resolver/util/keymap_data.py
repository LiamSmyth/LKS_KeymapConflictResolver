"""Pure Python dataclasses for keymap conflict data.

No bpy imports. Fully unit-testable outside Blender.

Conflicts are detected WITHIN a single keymap only. Two KMIs in different
keymaps are never considered conflicts because Blender resolves keymaps
hierarchically (most-specific context wins).
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class KeySignature:
    """Unique fingerprint of a keymap binding.

    Includes all fields that make a binding unique within the same keymap:
    key type, event value, modifiers, map type, and drag direction.
    """

    key_type: str       # e.g. "TAB", "RIGHTMOUSE"
    value: str          # "PRESS", "RELEASE", "CLICK", "CLICK_DRAG", etc.
    shift: bool
    ctrl: bool
    alt: bool
    oskey: bool
    key_modifier: str   # "NONE" or a key type string
    any: bool
    map_type: str       # "KEYBOARD", "MOUSE", "NDOF", "TEXTINPUT", "TIMER"
    direction: str      # "ANY", "NORTH", "SOUTH", etc. (for drag events)

    def to_string(self) -> str:
        """Human-readable label: e.g. 'Ctrl+Shift+Tab'."""
        parts: list[str] = []
        if self.any:
            parts.append("Any")
        else:
            if self.ctrl:
                parts.append("Ctrl")
            if self.shift:
                parts.append("Shift")
            if self.alt:
                parts.append("Alt")
            if self.oskey:
                parts.append("OS")
        if self.key_modifier and self.key_modifier not in ("NONE", ""):
            parts.append(self.key_modifier.replace("_", " ").title())
        parts.append(self.key_type.replace("_", " ").title())
        return "+".join(parts)

    def as_tuple(self) -> tuple:
        """Hashable representation for dict keys / set membership."""
        return (
            self.key_type,
            self.value,
            self.shift,
            self.ctrl,
            self.alt,
            self.oskey,
            self.key_modifier,
            self.any,
            self.map_type,
            self.direction,
        )


@dataclass
class ConflictItem:
    """One keymap item that participates in a conflict group."""

    km_name: str        # Keymap name (e.g. "Object Mode")
    kmi_id: int         # kmi.id for lookup via keymap_items.from_id()
    kmi_idname: str     # Operator bl_idname
    kmi_label: str      # Operator bl_label (human-readable name)
    source: str         # "blender", "addon", or "user"
    is_active: bool     # kmi.active


@dataclass
class ConflictGroup:
    """A set of keymap items sharing the same key signature within a single keymap.

    Since conflicts are only detected within the same keymap, all items
    in a group belong to the same keymap context.
    """

    km_name: str                    # Keymap where this conflict occurs
    signature: KeySignature
    signature_label: str            # e.g. "[Object Mode] Ctrl+Tab"
    items: list[ConflictItem] = field(default_factory=list)
    resolved: bool = False          # True if <= 1 item is active
