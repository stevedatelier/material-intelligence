from __future__ import print_function

import glob
import os
import sys

import hou


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def safe_text(value):
    return str(value).replace("\r", " ").replace("\n", "\\n")


def interesting_parms(node):
    type_name = node.type().name().lower()
    node_name = node.name().lower()
    keywords = (
        "vellum", "popwind", "popforce", "gravity", "solver", "file", "cache",
        "wrangle", "attribvop", "material", "shader", "render", "rop", "guide",
        "hair", "constraint", "stitch", "cloth", "tear", "break",
    )
    if not any(word in type_name or word in node_name for word in keywords):
        return []

    values = []
    parm_keywords = (
        "stiff", "damp", "break", "plastic", "threshold", "gravity", "wind",
        "force", "substep", "iter", "collision", "thickness", "mass", "friction",
        "file", "path", "sopoutput", "vm_picture", "snippet", "group", "type",
        "restlength", "constraint", "activation", "enable", "output",
    )
    for parm in node.parms():
        pname = parm.name().lower()
        if not any(word in pname for word in parm_keywords):
            continue
        try:
            raw = parm.unexpandedString() if parm.parmTemplate().type() == hou.parmTemplateType.String else parm.eval()
        except Exception:
            continue
        text = safe_text(raw)
        if len(text) > 240:
            text = text[:237] + "..."
        values.append("{}={}".format(parm.name(), text))
    return values[:28]


def list_networks(root):
    networks = []
    for node in (root,) + root.allSubChildren():
        try:
            children = node.children()
        except Exception:
            continue
        if children and (node.path() == "/obj" or len(children) >= 2):
            networks.append(node)
    return networks


def inspect(path):
    print("\n" + "=" * 120)
    print("HIP {}".format(os.path.basename(path)))
    hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
    root = hou.node("/obj")
    print("VERSION {}  FPS {}  FRAME_RANGE {}".format(
        hou.applicationVersionString(), hou.fps(), hou.playbar.frameRange()))

    try:
        refs = hou.fileReferences()
    except Exception as exc:
        refs = []
        print("FILE_REFERENCES_ERROR {}".format(exc))
    for parm, ref in refs:
        try:
            expanded = hou.expandString(ref)
        except Exception:
            expanded = ref
        exists = os.path.exists(expanded)
        print("REF {} | {} | exists={}".format(
            parm.path() if parm else "<none>", safe_text(ref), exists))

    for network in list_networks(root):
        children = list(network.children())
        notes = [item for item in network.stickyNotes()]
        print("\nNET {} [{}] children={} notes={}".format(
            network.path(), network.type().name(), len(children), len(notes)))
        for note in notes:
            print("  NOTE pos={} size={} text={}".format(
                note.position(), note.size(), safe_text(note.text())[:280]))
        children.sort(key=lambda item: (-item.position().y(), item.position().x(), item.name()))
        for child in children:
            flags = "{}{}{}".format(
                " D" if getattr(child, "isDisplayFlagSet", lambda: False)() else "",
                " R" if getattr(child, "isRenderFlagSet", lambda: False)() else "",
                " B" if getattr(child, "isBypassed", lambda: False)() else "",
            )
            print("  NODE {:<34} {:<28} pos=({:7.2f},{:7.2f}){}".format(
                child.name(), child.type().name(), child.position().x(), child.position().y(), flags))
            parms = interesting_parms(child)
            if parms:
                print("    PARMS " + " | ".join(parms))


def main():
    hou.setUpdateMode(hou.updateMode.Manual)
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "*.hip")))
    for path in paths:
        inspect(os.path.abspath(path))


if __name__ == "__main__":
    main()
