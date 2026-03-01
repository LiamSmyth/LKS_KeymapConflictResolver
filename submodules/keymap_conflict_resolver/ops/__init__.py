"""Operators for Keymap Conflict Resolver submodule."""

from .lks_ot_scan import LKS_OT_ScanKeymapConflicts
from .lks_ot_purge_duplicates import LKS_OT_PurgeExactDuplicates
from .lks_ot_toggle_addon_warning import LKS_OT_KcrToggleAddonWarning
from .lks_ot_show_info import LKS_OT_KcrShowInfo

__all__ = [
    "LKS_OT_ScanKeymapConflicts",
    "LKS_OT_PurgeExactDuplicates",
    "LKS_OT_KcrToggleAddonWarning",
    "LKS_OT_KcrShowInfo",
]
