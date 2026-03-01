"""Debug copytree_ignore behavior."""
from pathlib import Path
import sys
sys.path.insert(0, ".")
from addon_tools.publish_to_github import _load_ignore_patterns, _is_ignored

addon_root = Path(".").resolve()
patterns = _load_ignore_patterns(addon_root)

# Test 1: top-level iteration — submodules/ dir
rel = Path("submodules")
print(f"submodules/ dir: {'SKIP' if _is_ignored(rel, patterns) else 'COPY'}")

# Test 2: what copytree sees inside submodules/
directory = str(addon_root / "submodules")
contents = ["keymap_conflict_resolver", "README.md"]
for name in contents:
    full = Path(directory) / name
    try:
        rel = full.relative_to(addon_root)
        src = "rel_to"
    except ValueError:
        rel = Path(name)
        src = "fallback"
    result = _is_ignored(rel, patterns)
    tag = "SKIP" if result else "COPY"
    print(f"  {tag}  {name} (via {src}, rel={rel})")

# Test 3: what copytree sees when junction resolves to different abs path
# The junction target is blender_utils/submodules/keymap_conflict_resolver
junction_resolved = Path(r"C:\BTS_SSD\Work_Scripts\blender_utils\submodules\keymap_conflict_resolver")
for name in ["__init__.py", "register.py", ".git", "__pycache__", "ops"]:
    full = junction_resolved / name
    try:
        rel = full.relative_to(addon_root)
        src = "rel_to"
    except ValueError:
        rel = Path(name)
        src = "FALLBACK"
    result = _is_ignored(rel, patterns)
    tag = "SKIP" if result else "COPY"
    print(f"  {tag}  submod/{name} (via {src}, rel={rel})")
