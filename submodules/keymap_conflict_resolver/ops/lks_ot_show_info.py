"""Info button operator — displays conflict detection caveats as a tooltip."""

from __future__ import annotations

import bpy


class LKS_OT_KcrShowInfo(bpy.types.Operator):
    """Conflict detection info — hover for details"""

    bl_idname: str = "wm.lks_kcr_show_info"
    bl_label: str = "Conflict Detection Info"
    bl_description: str = (
        "Conflict detection compares key bindings within the same "
        "keymap context.\n\n"
        "Known limitations:\n"
        "• False positives may appear for mouse actions and other "
        "inputs where Blender intentionally stacks multiple operators "
        "on the same key.  Blender uses each operator's poll() function "
        "to decide which one actually runs (based on selected object "
        "type, active tool, editor area, etc.), so these bindings never "
        "truly conflict at runtime.\n"
        "• Operator properties are not compared — two bindings that call "
        "different menus via the same key will appear as conflicts."
    )
    bl_options: set = {'INTERNAL'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        return {'FINISHED'}
