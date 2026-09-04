from __future__ import print_function

import glob
import os
import sys

import hou


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_NETWORKS = ("/obj", "/mat", "/out", "/stage")
SKIP_TYPES = {
    "cam", "VRayNodeLightDome", "VRayNodeLightDirect", "VRayNodeLightRectangle",
    "geometryvopglobal::2.0", "geometryvopoutput", "output", "subinput", "suboutput",
}


def wanted_network(node):
    if node.path() in ROOT_NETWORKS:
        return True
    if node.type().name() in SKIP_TYPES:
        return False
    if not node.children():
        return False
    path = node.path().lower()
    terms = (
        "geo", "vellum", "solver", "dop", "pop", "hair", "guide", "material",
        "shader", "render", "thread", "wool", "yarn", "string", "etiquette",
        "cloth", "knit", "lint", "subnet", "vray", "attribvop",
    )
    return any(term in path or term in node.type().name().lower() for term in terms)


def format_child(node):
    flags = ""
    if getattr(node, "isDisplayFlagSet", lambda: False)():
        flags += "[D]"
    if getattr(node, "isRenderFlagSet", lambda: False)():
        flags += "[R]"
    if getattr(node, "isBypassed", lambda: False)():
        flags += "[B]"
    return "{}<{}>{}".format(node.name(), node.type().name(), flags)


def inspect(path):
    print("\n" + "=" * 120)
    print("HIP " + os.path.basename(path))
    hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
    seen = set()
    for root_path in ROOT_NETWORKS:
        root = hou.node(root_path)
        if root is None:
            continue
        candidates = (root,) + root.allSubChildren()
        for node in candidates:
            if node.path() in seen or not wanted_network(node):
                continue
            seen.add(node.path())
            children = sorted(node.children(), key=lambda child: (-child.position().y(), child.position().x()))
            print("NET {} [{}] children={} notes={}".format(
                node.path(), node.type().name(), len(children), len(node.stickyNotes())))
            chunks = [format_child(child) for child in children]
            for start in range(0, len(chunks), 12):
                print("  " + " | ".join(chunks[start:start + 12]))


def main():
    hou.setUpdateMode(hou.updateMode.Manual)
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "*.hip")))
    for path in paths:
        inspect(os.path.abspath(path))


if __name__ == "__main__":
    main()
