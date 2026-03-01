"""LKS_OT_RemoveKeymapItem — delete a user-added keymap item."""

from __future__ import annotations

import bpy


class LKS_OT_RemoveKeymapItem(bpy.types.Operator):
    """Delete a user-added keymap item from the active keyconfig."""

    bl_idname = "wm.lks_kcr_remove_item"
    bl_label = "Delete Keymap Item"
    bl_description = (
        "Delete a user-added keymap item. "
        "Built-in items cannot be deleted — use Unmap instead"
    )
    bl_options = {"REGISTER", "INTERNAL"}

    km_name: bpy.props.StringProperty(name="Keymap Name")
    kmi_id: bpy.props.IntProperty(name="KMI ID")

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.window_manager is not None

    def execute(self, context: bpy.types.Context):
        wm: bpy.types.WindowManager = context.window_manager
        kc: bpy.types.KeyConfig = wm.keyconfigs.active

        km: bpy.types.KeyMap | None = kc.keymaps.get(self.km_name)
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

        if not kmi.is_user_defined:
            self.report(
                {"WARNING"},
                "Cannot delete built-in items — use Unmap instead.",
            )
            return {"CANCELLED"}

        item_name: str = kmi.name
        km.keymap_items.remove(kmi)
        self.report({"INFO"}, f"Deleted '{item_name}' from '{self.km_name}'")
        return {"FINISHED"}
