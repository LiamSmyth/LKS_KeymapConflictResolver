"""Toggle the expanded state of an addon keymap conflict warning."""

from __future__ import annotations

import bpy


class LKS_OT_KcrToggleAddonWarning(bpy.types.Operator):
    """Toggle visibility of conflict details for an addon keymap item."""

    bl_idname = "wm.lks_kcr_toggle_addon_warning"
    bl_label = "Toggle Conflict Details"
    bl_options = {'INTERNAL'}

    kmi_key: bpy.props.StringProperty(
        name="KMI Key",
        description="Unique identifier for the KMI whose warning to toggle",
    )

    def execute(self, context: bpy.types.Context):
        mgr = context.window_manager.lks_kcr_resolver
        current: set[str] = _parse_expanded(mgr.expanded_addon_warnings)

        if self.kmi_key in current:
            current.discard(self.kmi_key)
        else:
            current.add(self.kmi_key)

        mgr.expanded_addon_warnings = ",".join(sorted(current))
        return {'FINISHED'}


def _parse_expanded(raw: str) -> set[str]:
    """Parse the comma-separated expanded keys string into a set."""
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}
