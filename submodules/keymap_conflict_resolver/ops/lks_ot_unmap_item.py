"""LKS_OT_UnmapKeymapItem — clear a keymap item's key binding (set type to NONE)."""

from __future__ import annotations

import bpy


class LKS_OT_UnmapKeymapItem(bpy.types.Operator):
    """Clear a keymap item's key binding without deleting the item."""

    bl_idname = "wm.lks_kcr_unmap_item"
    bl_label = "Unmap Keymap Item"
    bl_description = "Clear the key binding (set to NONE) without deleting the item"
    bl_options = {"REGISTER", "INTERNAL"}

    km_name: bpy.props.StringProperty(name="Keymap Name")
    kmi_id: bpy.props.IntProperty(name="KMI ID")

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.window_manager is not None

    def execute(self, context: bpy.types.Context):
        wm: bpy.types.WindowManager = context.window_manager
        kc: bpy.types.KeyConfig = wm.keyconfigs.active

        km = kc.keymaps.get(self.km_name)
        if km is None:
            self.report({"WARNING"}, f"Keymap not found: {self.km_name}")
            return {"CANCELLED"}

        kmi = km.keymap_items.from_id(self.kmi_id)
        if kmi is None:
            self.report(
                {"WARNING"},
                f"Keymap item {self.kmi_id} not found in '{self.km_name}'",
            )
            return {"CANCELLED"}

        old_name: str = kmi.name
        try:
            kmi.type = 'NONE'
        except TypeError:
            # Mouse / NDOF items don't have 'NONE' — deactivate instead
            kmi.active = False
        self.report({"INFO"}, f"Unmapped '{old_name}' in '{self.km_name}'")
        return {"FINISHED"}
