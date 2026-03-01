"""Blender PropertyGroups for Keymap Conflict Resolver.

Registration order matters: child PropertyGroups before their parents.
    LKS_PG_KcrConflictItem → LKS_PG_KcrConflictGroup → LKS_PG_KcrFilterState → LKS_PG_KcrResolver

The resolver root is attached to bpy.types.WindowManager.lks_kcr_resolver.
"""

from __future__ import annotations

import bpy


class LKS_PG_KcrConflictItem(bpy.types.PropertyGroup):
    """A single keymap item participating in a conflict."""
    km_name: bpy.props.StringProperty(name="Keymap Name")
    kmi_id: bpy.props.IntProperty(name="KMI ID")
    kmi_idname: bpy.props.StringProperty(name="Operator IDName")
    kmi_label: bpy.props.StringProperty(name="Operator Label")
    # "blender", "addon:<id>", "user"
    source: bpy.props.StringProperty(name="Source")
    is_active: bpy.props.BoolProperty(name="Active", default=True)


class LKS_PG_KcrConflictGroup(bpy.types.PropertyGroup):
    """A group of keymap items that share the same key signature within a single keymap."""
    # name: built-in StringProperty — used as the signature_label
    km_name: bpy.props.StringProperty(name="Keymap Name")
    signature_key: bpy.props.StringProperty(
        name="Signature Key",
        description="Original key signature tuple as string, for live comparison",
    )
    resolved: bpy.props.BoolProperty(name="Resolved", default=False)
    items: bpy.props.CollectionProperty(type=LKS_PG_KcrConflictItem)


class LKS_PG_KcrFilterState(bpy.types.PropertyGroup):
    """Filter/search state for the conflict list UI."""
    search_text: bpy.props.StringProperty(
        name="Search",
        description="Filter conflicts by key name or operator name",
        default="",
    )
    hide_resolved: bpy.props.BoolProperty(
        name="Hide Resolved",
        description="Hide conflict groups that have been resolved",
        default=False,
    )


class LKS_PG_KcrResolver(bpy.types.PropertyGroup):
    """Root resolver state stored on the WindowManager."""
    conflicts: bpy.props.CollectionProperty(type=LKS_PG_KcrConflictGroup)
    active_conflict_index: bpy.props.IntProperty(
        name="Active Conflict",
        description="Index of the selected conflict group in the list",
        default=0,
    )
    filter: bpy.props.PointerProperty(type=LKS_PG_KcrFilterState)
    last_scan_info: bpy.props.StringProperty(
        name="Last Scan",
        description="Info string from the last scan (count + timestamp)",
        default="",
    )
    show_resolver: bpy.props.BoolProperty(
        name="Conflict Resolver",
        description="Show or hide the global conflict resolver section",
        default=False,
    )
    show_addon_keymaps: bpy.props.BoolProperty(
        name="Addon Keymaps",
        description="Show or hide the addon keymaps section",
        default=True,
    )
    expanded_addon_warnings: bpy.props.StringProperty(
        name="Expanded Addon Warnings",
        description="Comma-separated KMI keys whose conflict details are expanded",
        default="",
    )


# ---------------------------------------------------------------------------
# Registration helpers
# ---------------------------------------------------------------------------

_classes: tuple = (
    LKS_PG_KcrConflictItem,
    LKS_PG_KcrConflictGroup,
    LKS_PG_KcrFilterState,
    LKS_PG_KcrResolver,
)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.lks_kcr_resolver = bpy.props.PointerProperty(
        type=LKS_PG_KcrResolver
    )


def unregister() -> None:
    del bpy.types.WindowManager.lks_kcr_resolver
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
