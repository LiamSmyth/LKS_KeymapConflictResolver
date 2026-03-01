"""Drawing utilities for integrating the Keymap Conflict Resolver into addon preferences.

Two public functions are provided:

``draw_conflict_resolver(layout)``
    Renders the full conflict resolver inline — scrollable conflict-group
    list on top, detail panel for the selected group below.  Embeds scan /
    purge buttons and filter controls.

``draw_addon_keymaps(layout, addon_keymaps)``
    Renders an addon's own keymap items grouped by context, with inline
    conflict warnings — similar to the Heavypoly addon preferences pattern.

Example usage in an addon's ``AddonPreferences.draw()``::

    from .submodules.keymap_conflict_resolver.draw_utils import (
        draw_conflict_resolver,
        draw_addon_keymaps,
    )

    class MyAddonPrefs(bpy.types.AddonPreferences):
        bl_idname = "my_addon"

        def draw(self, context):
            layout = self.layout
            draw_conflict_resolver(layout)
            # Optionally show your own addon keymaps with conflict badges:
            # draw_addon_keymaps(layout, my_addon_keymaps)
"""

from __future__ import annotations

import bpy
import rna_keymap_ui


# ---------------------------------------------------------------------------
# UIList (registered via register.py)
# ---------------------------------------------------------------------------

class LKS_UL_KcrConflictGroups(bpy.types.UIList):
    """Scrollable list of conflict groups with hide-resolved filtering."""

    bl_idname = "LKS_UL_kcr_conflict_groups"

    def draw_item(
        self, context: bpy.types.Context, layout: bpy.types.UILayout,
        data, item, icon: int, active_data, active_property: str,
        index: int = 0, flt_flag: int = 0,
    ) -> None:
        kc: bpy.types.KeyConfig = context.window_manager.keyconfigs.active
        resolved: bool = _is_group_resolved(item, kc)
        split = layout.split(factor=0.55)
        split.label(
            text=item.name,
            icon='CHECKMARK' if resolved else 'ERROR',
        )
        # Keymap context name in the remaining space
        sub = split.row()
        sub.alignment = 'RIGHT'
        sub.enabled = False
        sub.label(text=item.km_name)

    def filter_items(
        self, context: bpy.types.Context, data, propname: str,
    ):
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(items)

        mgr = context.window_manager.lks_kcr_resolver
        kc = context.window_manager.keyconfigs.active

        if mgr.filter.hide_resolved:
            for i, group in enumerate(items):
                if _is_group_resolved(group, kc):
                    flt_flags[i] = 0  # hide resolved

        # Text search filter
        search: str = mgr.filter.search_text.lower()
        if search:
            for i, group in enumerate(items):
                if flt_flags[i] == 0:
                    continue
                if not _group_matches_search(group, search):
                    flt_flags[i] = 0

        return flt_flags, []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def draw_conflict_resolver(layout: bpy.types.UILayout) -> None:
    """Draw the full conflict resolver inline in addon preferences.

    Uses a scrollable ``template_list`` for conflict groups with a detail
    panel below showing the KMI rows of the selected group.
    Wrapped in a collapsible header.
    """
    wm: bpy.types.WindowManager = bpy.context.window_manager
    mgr = getattr(wm, "lks_kcr_resolver", None)
    kc: bpy.types.KeyConfig = wm.keyconfigs.active

    # -- Collapsible header --
    box = layout.box()
    header = box.row(align=True)
    if mgr:
        header.prop(
            mgr, "show_resolver",
            icon='DISCLOSURE_TRI_DOWN' if mgr.show_resolver else 'DISCLOSURE_TRI_RIGHT',
            emboss=False,
        )
    else:
        header.label(text="Conflict Resolver", icon='DISCLOSURE_TRI_RIGHT')
        return

    # Info button (tooltip explains false-positive caveats)
    info_sub = header.row()
    info_sub.alignment = 'RIGHT'
    info_sub.operator("wm.lks_kcr_show_info", text="",
                      icon='INFO', emboss=False)

    if not mgr.show_resolver:
        return

    # -- Action bar --
    action_row = box.row(align=True)
    action_row.operator(
        "wm.lks_kcr_scan", text="Scan Conflicts", icon='FILE_REFRESH',
    )
    action_row.operator(
        "wm.lks_kcr_purge_duplicates", text="Purge Duplicates", icon='TRASH',
    )

    if mgr.last_scan_info:
        action_row.label(text=mgr.last_scan_info, icon='INFO')

    # -- Empty / not-yet-scanned state --
    if len(mgr.conflicts) == 0:
        box.label(text="No conflicts detected.", icon='CHECKMARK')
        return

    # -- Filter bar --
    filter_row = box.row(align=True)
    filter_row.prop(mgr.filter, "hide_resolved", toggle=True, icon='CHECKMARK')
    filter_row.prop(mgr.filter, "search_text", text="", icon='VIEWZOOM')

    box.separator()

    # -- Scrollable conflict group list --
    box.template_list(
        "LKS_UL_kcr_conflict_groups", "",
        mgr, "conflicts",
        mgr, "active_conflict_index",
        rows=8,
        maxrows=14,
    )

    # -- Detail panel for selected group --
    idx: int = mgr.active_conflict_index
    if idx < 0 or idx >= len(mgr.conflicts):
        return

    group_pg = mgr.conflicts[idx]
    resolved: bool = _is_group_resolved(group_pg, kc)
    _draw_conflict_group_detail(box, group_pg, kc, resolved)


def draw_addon_keymaps(
    layout: bpy.types.UILayout,
    addon_keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]],
) -> None:
    """Draw addon keymap items grouped by context, with inline conflict warnings.

    Modeled after the Heavypoly addon preferences keymap display.
    Wrapped in a collapsible header.

    Args:
        layout: Parent UILayout (typically a box inside AddonPreferences).
        addon_keymaps: List of ``(KeyMap, KeyMapItem)`` tuples as registered
            by the consuming addon.
    """
    wm: bpy.types.WindowManager = bpy.context.window_manager
    mgr = getattr(wm, "lks_kcr_resolver", None)
    kc: bpy.types.KeyConfig = wm.keyconfigs.addon
    kc_active: bpy.types.KeyConfig = wm.keyconfigs.active

    # -- Collapsible header --
    box = layout.box()
    header = box.row(align=True)
    if mgr:
        header.prop(
            mgr, "show_addon_keymaps",
            icon='DISCLOSURE_TRI_DOWN' if mgr.show_addon_keymaps else 'DISCLOSURE_TRI_RIGHT',
            emboss=False,
        )
    else:
        header.label(text="Addon Keymaps", icon='DISCLOSURE_TRI_RIGHT')
        return

    # Info button (tooltip explains false-positive caveats)
    info_sub = header.row()
    info_sub.alignment = 'RIGHT'
    info_sub.operator("wm.lks_kcr_show_info", text="",
                      icon='INFO', emboss=False)

    # Count total conflicts for the header badge
    conflict_count: int = _count_addon_conflicts(addon_keymaps)
    if conflict_count > 0:
        sub = header.row()
        sub.alignment = 'RIGHT'
        sub.label(text=f"{conflict_count} conflict(s)", icon='ERROR')

    if not mgr.show_addon_keymaps:
        return

    if not addon_keymaps:
        box.label(text="No addon keymaps registered", icon='INFO')
        return

    # Group by keymap context name
    groups: dict[str, list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]]] = {}
    for km, kmi in addon_keymaps:
        km_active = km.active()
        km_name: str = km_active.name if km_active else km.name
        groups.setdefault(km_name, []).append((km, kmi))

    # Draw each context group
    for km_name, items in groups.items():
        _draw_addon_keymap_group(box, km_name, items, kc, kc_active)


# ---------------------------------------------------------------------------
# Conflict-resolver internals
# ---------------------------------------------------------------------------

def _source_badge(source: str) -> str:
    """Return a short display label for a source string."""
    if source == "user":
        return "User"
    if source == "blender":
        return "Blender"
    if source == "addon":
        return "Add-on"
    if source.startswith("addon:"):
        return "Add-on"
    return source


def _is_group_resolved(group_pg, kc: bpy.types.KeyConfig) -> bool:
    """Return True if <= 1 KMI still actively conflicts.

    A KMI counts as still-conflicting only when it is:
    - found in the keymap
    - active
    - has a non-NONE type
    - its current key signature still matches the group's original signature
      (a remapped KMI no longer participates in this conflict)
    """
    from .util.keymap_query import make_signature

    km = kc.keymaps.get(group_pg.km_name)
    original_sig: str = group_pg.signature_key
    active_bound: int = 0
    for item_pg in group_pg.items:
        live_kmi = None
        if km is not None:
            live_kmi = km.keymap_items.from_id(item_pg.kmi_id)
        if live_kmi is None or not live_kmi.active or live_kmi.type == 'NONE':
            continue
        # Only count if the KMI still has the same key as the original conflict
        current_sig: str = str(make_signature(live_kmi).as_tuple())
        if current_sig == original_sig:
            active_bound += 1
    return active_bound <= 1


def _group_matches_search(group_pg, search: str) -> bool:
    """Return True if a conflict group matches the search filter."""
    if search in group_pg.name.lower():
        return True
    if search in group_pg.km_name.lower():
        return True
    for item in group_pg.items:
        if search in item.kmi_label.lower() or search in item.kmi_idname.lower():
            return True
    return False


def _draw_conflict_group_detail(
    layout: bpy.types.UILayout,
    group_pg,
    kc: bpy.types.KeyConfig,
    resolved: bool,
) -> None:
    """Draw the detail panel for the selected conflict group."""
    box = layout.box()

    # -- Header --
    header = box.row(align=True)
    header.label(
        text=group_pg.name,
        icon='CHECKMARK' if resolved else 'ERROR',
    )
    sub = header.row()
    sub.alignment = 'RIGHT'
    sub.label(text=group_pg.km_name)

    km = kc.keymaps.get(group_pg.km_name)

    # -- KMI rows --
    for item_pg in group_pg.items:
        live_kmi = None
        if km is not None:
            live_kmi = km.keymap_items.from_id(item_pg.kmi_id)

        if live_kmi is None:
            row = box.row(align=True)
            row.label(text=f"{item_pg.kmi_label} (not found)", icon='QUESTION')
            continue

        row = box.row(align=True)

        # Source badge (narrow column)
        badge = row.row()
        badge.scale_x = 0.4
        badge.label(text=_source_badge(item_pg.source))

        # Operator label
        row.label(text=live_kmi.name)

        # Editable key binding
        row.prop(live_kmi, "type", text="", full_event=True)

        # Active toggle
        row.prop(
            live_kmi, "active", text="",
            icon='HIDE_OFF' if live_kmi.active else 'HIDE_ON',
        )

        # Unmap button
        unmap_op = row.operator(
            "wm.lks_kcr_unmap_item", text="", icon='PANEL_CLOSE',
        )
        unmap_op.km_name = item_pg.km_name
        unmap_op.kmi_id = item_pg.kmi_id

        # Delete button (user items only)
        if live_kmi.is_user_defined:
            del_op = row.operator(
                "wm.lks_kcr_remove_item", text="", icon='X',
            )
            del_op.km_name = item_pg.km_name
            del_op.kmi_id = item_pg.kmi_id


# ---------------------------------------------------------------------------
# Addon-keymaps internals
# ---------------------------------------------------------------------------

def _kmi_signature_matches(
    kmi: bpy.types.KeyMapItem,
    kmi_other: bpy.types.KeyMapItem,
) -> bool:
    """Return True if two KMIs have the same key binding."""
    return (
        kmi_other.type == kmi.type
        and kmi_other.value == kmi.value
        and kmi_other.shift == kmi.shift
        and kmi_other.ctrl == kmi.ctrl
        and kmi_other.alt == kmi.alt
        and getattr(kmi_other, "oskey", False) == getattr(kmi, "oskey", False)
        and kmi_other.key_modifier == kmi.key_modifier
        and kmi_other.any == kmi.any
    )


def _count_addon_conflicts(
    addon_keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]],
) -> int:
    """Count keymap conflicts for addon items.

    Checks two sources:
    - The merged active keymap (user/default bindings) via ``km.active()``
    - The addon keymap itself (inter-addon conflicts) via ``km.keymap_items``
    """
    count: int = 0
    for km, kmi in addon_keymaps:
        if not kmi.active:
            continue
        # 1. Check merged keymap (user + default bindings)
        km_active = km.active()
        if km_active:
            for kmi_other in km_active.keymap_items:
                if kmi_other.active and kmi_other.idname != kmi.idname:
                    if _kmi_signature_matches(kmi, kmi_other):
                        count += 1
        # 2. Check addon keymap (other addon bindings in same keymap)
        for kmi_other in km.keymap_items:
            if kmi_other is not kmi and kmi_other.active and kmi_other.idname != kmi.idname:
                if _kmi_signature_matches(kmi, kmi_other):
                    count += 1
    return count


def _draw_addon_keymap_group(
    layout: bpy.types.UILayout,
    km_name: str,
    keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]],
    kc: bpy.types.KeyConfig,
    kc_active: bpy.types.KeyConfig,
) -> None:
    """Draw a context group of keymaps with inline conflict warnings."""
    group_box = layout.box()

    # Context header
    icon: str = "OBJECT_DATA" if "Object" in km_name else "EDITMODE_HLT"
    group_box.label(text=km_name, icon=icon)

    # Two-column layout for compact display
    split = group_box.split(factor=0.5)
    col_left = split.column()
    col_right = split.column()

    for i, (km, kmi) in enumerate(keymaps):
        km_active = km.active()
        if not km_active:
            continue

        col = col_left if i % 2 == 0 else col_right
        col.context_pointer_set("keymap", km_active)
        rna_keymap_ui.draw_kmi([], kc, km_active, kmi, col, 0)

        # Inline conflict warnings (check merged + addon keymaps)
        _draw_addon_conflict_warning(col, km, km_active, kmi, kc, kc_active)


def _draw_addon_conflict_warning(
    layout: bpy.types.UILayout,
    km_addon: bpy.types.KeyMap,
    km_active: bpy.types.KeyMap,
    kmi: bpy.types.KeyMapItem,
    kc: bpy.types.KeyConfig,
    kc_active: bpy.types.KeyConfig,
) -> None:
    """Draw a collapsible conflict summary for a single addon KMI.

    Shows a compact \"N conflicts detected\" row that expands to reveal
    detailed conflict information when clicked.
    """
    if not kmi.active:
        return

    # -- Collect all conflicts --
    conflicts: list[tuple[bpy.types.KeyMap,
                          bpy.types.KeyMapItem, bpy.types.KeyConfig]] = []

    if km_active:
        for kmi_other in km_active.keymap_items:
            if kmi_other.active and kmi_other.idname != kmi.idname:
                if _kmi_signature_matches(kmi, kmi_other):
                    conflicts.append((km_active, kmi_other, kc_active))

    for kmi_other in km_addon.keymap_items:
        if kmi_other is not kmi and kmi_other.active and kmi_other.idname != kmi.idname:
            if _kmi_signature_matches(kmi, kmi_other):
                conflicts.append((km_addon, kmi_other, kc))

    if not conflicts:
        return

    # -- Collapse state --
    mgr = bpy.context.window_manager.lks_kcr_resolver
    kmi_key: str = f"{km_addon.name}:{kmi.idname}:{kmi.type}"
    expanded: bool = kmi_key in _parse_expanded(mgr.expanded_addon_warnings)

    # -- Header row --
    warn_box = layout.box()
    warn_box.alert = True
    header = warn_box.row(align=True)
    toggle = header.operator(
        "wm.lks_kcr_toggle_addon_warning",
        text=f"\u26a0 {len(conflicts)} conflict(s) detected",
        icon='DISCLOSURE_TRI_DOWN' if expanded else 'DISCLOSURE_TRI_RIGHT',
        emboss=False,
    )
    toggle.kmi_key = kmi_key

    if not expanded:
        return

    # -- Detail rows --
    for km_source, kmi_other, kc_source in conflicts:
        sub = warn_box.box()
        sub.label(
            text=f"Conflicts with: {kmi_other.name}",
            icon='ERROR',
        )
        sub.context_pointer_set("keymap", km_source)
        rna_keymap_ui.draw_kmi(
            [], kc_source, km_source, kmi_other, sub, 0,
        )


def _parse_expanded(raw: str) -> set[str]:
    """Parse the comma-separated expanded keys string into a set."""
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}
