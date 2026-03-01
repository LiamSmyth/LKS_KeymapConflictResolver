"""UI module for Keymap Conflict Resolver submodule.

The sidebar panel has been removed.  Consuming addons should embed the
resolver UI via the drawing helpers in ``draw_utils``::

    from .submodules.keymap_conflict_resolver.draw_utils import (
        draw_resolver_button,
        draw_addon_keymaps,
    )

These are typically called from an ``AddonPreferences.draw()`` method.
"""

from __future__ import annotations
