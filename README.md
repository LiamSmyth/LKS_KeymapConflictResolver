<img width="1291" height="1312" alt="image" src="https://github.com/user-attachments/assets/f6516822-82a6-43c2-8b0c-639225cb577e" />
The addon by itself, you can check and resolve global hotkeys

<img width="1290" height="742" alt="image" src="https://github.com/user-attachments/assets/c0574597-4474-435a-a43a-4d04662e20a6" />
An example of the submodule being used by an addon to display conflicts for addon shortcuts directly in the addon prefs. Allows users to resolve conflicts right in the window by remapping / removing conflicting items.


### Liam notes 

- The addon is meant to be a thin wrapper around the core submodule "keymap_conflict_resolver", as a shared resource so you can build addons with keymap items in the prefs that self-report conflicts, or use a global conflict detector. 

- this addon was entirely Claude-d. As such, I claim no ownership over anything in here. Use / reconfigure / fork it any way you wish.

- There are false positives. Keymap items are considered conflicting if they are identical mappings in the same context / tool space. Some default blender shortcuts, esp. mouse operations, seem to be intentionally stacked and only invoke the operator given the current object type using a set of polling fucntions. I just decided against digging into operators poll functions to see if stacking was OK, so this addon considers this sort of stacking to be conflicts. You may safely ignore these reports if they are intentional.

- It provides a builtin way to remap / remove / disable shortcuts in conflict groups to resolve the conflicts both as a global scan of the blender kemaps, but also for a selection of specific shortcuts, eg shortcuts added by an addon / extension that get displayed within the extension prefs. Using this ui, when the default addon shortcut conflicts with an exiting one, it will show immediately next to the mapped item in the prefs.

- Feel free to use this either as an addon, or rip the submodule out and use it in your own addon. I've tried to make it as easy as possible to reuse the submodule across multiple addons.

- You should be able to install it with blender 5.0+ and get updates from the releases if you add  https://liamsmyth.github.io/LKS_KeymapConflictResolver/index.json as a source (get extensions -> repositories dropdown -> + -> add that link). You can also install it the old fashioned way as an addon by downloading the zip, but if you install as an extension I can push updates.

- Now, on to the slop readme :D

# LKS Keymap Conflict Resolver

A Blender 5.0+ addon that detects and resolves keymap shortcut conflicts across all active keymaps.

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
