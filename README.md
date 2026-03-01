# LKS Keymap Conflict Resolver

A Blender 4.2+ addon that detects and resolves keymap shortcut conflicts across all active keymaps.

## Features

- **Conflict Scanner** — Scans all Blender keymaps for overlapping shortcuts (same key + modifiers in the same context).
- **Inline Conflict Resolver** — View conflicting operator assignments side-by-side and disable or remove individual bindings directly from the preferences panel.
- **Duplicate Purge** — Detect and remove exact-duplicate keymap items in one click.
- **Addon Keymap Display** — Shows the addon's own registered keymaps with inline conflict warnings when they collide with existing bindings.
- **Non-destructive** — Disabling a keymap item only toggles its `active` flag; removing deletes the binding. Both are undo-safe.

## Installation

### From Extension Zip
1. Download the latest `.zip` from the [Releases](../../releases) page.
2. In Blender: **Edit → Preferences → Get Extensions → Install from Disk** → select the zip.

### From Source (Development)
1. Clone this repository into your Blender addons directory (or create a junction):
   ```
   mklink /J "<BLENDER_SCRIPTS>/addons/lks_keymap_conflict_resolver" "<path-to-this-repo>"
   ```
2. Enable **LKS Keymap Conflict Resolver** in Blender's Add-ons preferences.

## Usage

1. Open **Edit → Preferences → Add-ons**.
2. Expand the **LKS Keymap Conflict Resolver** entry.
3. Click **Scan for Conflicts** to detect overlapping keymaps.
4. Expand any conflict group to see which operators share the same shortcut.
5. Use **Disable** or **Remove** buttons to resolve conflicts.

## Architecture

The core conflict detection logic lives in a standalone submodule (`keymap_conflict_resolver`) that can be embedded in any addon. This repository is the reference addon wrapper.

| Path | Purpose |
|------|---------|
| `register_addon.py` | Central orchestrator — properties → ops → keymaps → submodules → preferences |
| `addon_prefs.py` | Preferences panel embedding the resolver UI |
| `submodules/keymap_conflict_resolver/` | Shared conflict detection & resolution submodule |

## Requirements

- Blender 4.2.0 or later

## License

GPL-3.0-or-later
