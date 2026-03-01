"""Debug: list all dirs and simulate copy."""
from pathlib import Path
import sys
sys.path.insert(0, ".")
from addon_tools.publish_to_github import _load_ignore_patterns, _is_ignored

addon_root = Path(".").resolve()
patterns = _load_ignore_patterns(addon_root)

print("=== Top-level dirs ===")
for item in sorted(addon_root.iterdir(), key=lambda x: x.name):
    if not item.is_dir():
        continue
    junc = item.is_junction() if hasattr(item, "is_junction") else False
    children = len(list(item.iterdir()))
    rel = item.relative_to(addon_root)
    ignored = _is_ignored(rel, patterns)
    print(f"  {'SKIP' if ignored else 'COPY'}  {item.name} (junction={junc}, children={children})")

print("\n=== Simulated copy of submodules/ ===")
sub_dir = addon_root / "submodules"
for child in sorted(sub_dir.iterdir()):
    rel = child.relative_to(addon_root)
    ignored = _is_ignored(rel, patterns)
    is_dir = child.is_dir()
    junc = child.is_junction() if hasattr(child, "is_junction") else False
    print(f"  {'SKIP' if ignored else 'COPY'}  {child.name} (dir={is_dir}, junction={junc})")
    if is_dir and not ignored:
        for f in sorted(child.iterdir()):
            try:
                frel = f.relative_to(addon_root)
            except ValueError:
                frel = Path(f.name)
            fignored = _is_ignored(frel, patterns)
            print(f"    {'SKIP' if fignored else 'COPY'}  {f.name} (rel={frel})")
