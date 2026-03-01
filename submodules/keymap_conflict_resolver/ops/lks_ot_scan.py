"""LKS_OT_ScanKeymapConflicts — scan the active keyconfig for conflicts."""

from __future__ import annotations

import datetime

import bpy

from ..util.keymap_query import find_conflict_groups
from ..util.keymap_data import ConflictGroup, ConflictItem


class LKS_OT_ScanKeymapConflicts(bpy.types.Operator):
    """Scan all keymaps for key signature conflicts across co-active contexts."""

    bl_idname = "wm.lks_kcr_scan"
    bl_label = "Scan Keymap Conflicts"
    bl_description = "Scan all keymaps for conflicting key bindings in overlapping contexts"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.window_manager is not None

    def execute(self, context: bpy.types.Context):
        wm: bpy.types.WindowManager = context.window_manager
        mgr = wm.lks_kcr_resolver

        kc: bpy.types.KeyConfig = wm.keyconfigs.active
        groups: list[ConflictGroup] = find_conflict_groups(kc)

        # Repopulate the PropertyGroup collection
        mgr.conflicts.clear()
        for group in groups:
            pg_group = mgr.conflicts.add()
            pg_group.name = group.signature_label
            pg_group.km_name = group.km_name
            pg_group.signature_key = str(group.signature.as_tuple())
            pg_group.resolved = group.resolved
            for item in group.items:
                pg_item = pg_group.items.add()
                pg_item.km_name = item.km_name
                pg_item.kmi_id = item.kmi_id
                pg_item.kmi_idname = item.kmi_idname
                pg_item.kmi_label = item.kmi_label
                pg_item.source = item.source
                pg_item.is_active = item.is_active

        timestamp: str = datetime.datetime.now().strftime("%H:%M:%S")
        mgr.last_scan_info = f"{len(groups)} conflict group(s) — {timestamp}"

        self.report({"INFO"}, mgr.last_scan_info)
        return {"FINISHED"}
