from __future__ import print_function

import glob
import os

import hou


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_TYPES = (
    "file", "filecache", "vrayproxy", "imagefile", "texture", "environment",
    "alembic", "usd", "agent", "volume",
)
INPUT_EXTENSIONS = (
    ".bgeo", ".bgeo.sc", ".fbx", ".obj", ".abc", ".vdb", ".vrmesh",
    ".exr", ".hdr", ".rat", ".jpg", ".jpeg", ".png", ".tif", ".tiff",
)
IGNORE_BASENAMES = {"vfhlightdome.bgeo", "defcam.bgeo"}


def is_candidate(parm, raw):
    if parm is None or not raw or raw == "None":
        return False
    if parm.path().startswith("/out/"):
        return False
    node = parm.node()
    node_type = node.type().name().lower()
    name = parm.name().lower()
    low = raw.lower().split("?")[0]
    if os.path.basename(low) in IGNORE_BASENAMES:
        return False
    return (
        any(term in node_type for term in INPUT_TYPES)
        or any(term in name for term in ("file", "tex", "map", "path"))
    ) and any(ext in low for ext in INPUT_EXTENSIONS)


def main():
    hou.setUpdateMode(hou.updateMode.Manual)
    for path in sorted(glob.glob(os.path.join(ROOT, "*.hip"))):
        hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
        print("\nHIP " + os.path.basename(path))
        found = 0
        for parm, raw in hou.fileReferences():
            raw = str(raw)
            if not is_candidate(parm, raw):
                continue
            try:
                expanded = hou.text.expandString(raw)
            except Exception:
                expanded = raw
            exists = os.path.exists(expanded)
            print("  {} | {} | exists={}".format(parm.path(), raw, exists))
            found += 1
        if not found:
            print("  <no external input files detected>")


if __name__ == "__main__":
    main()
