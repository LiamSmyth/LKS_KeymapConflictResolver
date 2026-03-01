"""LKS_OT_PurgeExactDuplicates — remove exact idname duplicates from the user keyconfig."""

from __future__ import annotations

import bpy


class LKS_OT_PurgeExactDuplicates(bpy.types.Operator):
    """Remove user keyconfig items that are exact idname+key duplicates within the same keymap."""

    bl_idname = "wm.lks_kcr_purge_duplicates"
    bl_label = "Purge Exact Duplicates"
    bl_description = (
        "Remove user keyconfig items that are exact duplicates "
        "(same key binding AND same operator) within the same keymap"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.window_manager is not None

    def execute(self, context: bpy.types.Context):
        wm: bpy.types.WindowManager = context.window_manager
        kc_user: bpy.types.KeyConfig = wm.keyconfigs.user
        removed_count: int = 0

        for km in kc_user.keymaps:
            # Group items by (signature_tuple, idname)
            seen: dict[tuple, bpy.types.KeyMapItem] = {}
            to_remove: list[bpy.types.KeyMapItem] = []

            for kmi in km.keymap_items:
                sig_key: tuple = (
                    kmi.type,
                    kmi.value,
                    kmi.shift,
                    kmi.ctrl,
                    kmi.alt,
                    getattr(kmi, "oskey", False),
                    kmi.key_modifier,
                    kmi.any,
                    kmi.idname,
                )
                if sig_key in seen:
                    to_remove.append(kmi)
                else:
                    seen[sig_key] = kmi

            for kmi in to_remove:
                km.keymap_items.remove(kmi)
                removed_count += 1

        self.report(
            {"INFO"}, f"Purged {removed_count} exact duplicate keymap item(s)")
        bpy.ops.wm.lks_kcr_scan()
        return {"FINISHED"}
