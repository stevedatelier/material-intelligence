from __future__ import print_function

import os
import sys

import hou

from annotate_tutorial_notes import COLORS, INTRO_TEXT, NOTE_PREFIX, ROOT, structural_fingerprint


EXPECTED = {
    "03_Single_Infinity_Yarn_Fiber_Construction.hip": ("01adf553a0b60cd5", 20),
    "03_Three_Strand_Infinity_Yarn_and_Lint_Render.hip": ("3372454f27783030", 47),
    "04_Cached_Knit_Lace_and_Wool_Ball_Render_Setup.hip": ("623a22e867e3392d", 44),
    "04_Dynamic_Knitting_Grid_Prototype.hip": ("f495539028c6cecd", 5),
    "05_Single_Wool_Ball_Vellum_and_Fiber_Setup.hip": ("7ca20f5730c9ebde", 33),
    "05_Yarn_Ball_Vellum_and_Fiber_Render.hip": ("366ab42632b8de0e", 33),
    "07_Multicolor_Ten_Wool_Ball_Vellum_Simulation.hip": ("b3f7364da8c79461", 53),
    "08_Cloth_Tearing_and_Stitch_Failure.hip": ("9741bf1d40e50e08", 34),
}


def network_items():
    for root_path in ("/obj", "/mat", "/out", "/stage"):
        root = hou.node(root_path)
        if root is None:
            continue
        for network in (root,) + root.allSubChildren():
            try:
                notes = network.stickyNotes()
                children = network.children()
            except Exception:
                continue
            yield network, notes, children


def in_rect(point, position, size):
    return (position.x() <= point.x() <= position.x() + size.x() and
            position.y() <= point.y() <= position.y() + size.y())


def verify(path):
    name = os.path.basename(path)
    expected_hash, expected_count = EXPECTED[name]
    hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
    actual_hash = structural_fingerprint()
    errors = []
    if not actual_hash.startswith(expected_hash):
        errors.append("structural fingerprint mismatch")

    tutorial_notes = []
    overlaps = []
    palette = [tuple(color.rgb()) for color in COLORS.values()]
    for network, notes, children in network_items():
        for note in notes:
            if not note.text().startswith(NOTE_PREFIX):
                continue
            tutorial_notes.append(note)
            if tuple(note.color().rgb()) not in palette:
                errors.append("off-palette note in " + network.path())
            for child in children:
                if in_rect(child.position(), note.position(), note.size()):
                    overlaps.append("{} -> {}".format(network.path(), child.name()))

    if len(tutorial_notes) != expected_count:
        errors.append("expected {} tutorial notes, found {}".format(expected_count, len(tutorial_notes)))
    obj_notes = [note for note in hou.node("/obj").stickyNotes()
                 if note.text().startswith(NOTE_PREFIX)]
    if not any(INTRO_TEXT[name] in note.text() for note in obj_notes):
        errors.append("missing top-level introduction")
    if overlaps:
        errors.append("notes cover node positions: " + ", ".join(overlaps[:8]))
    if errors:
        raise RuntimeError("; ".join(errors))
    networks = len({note.parent().path() for note in tutorial_notes})
    print("PASS {} | notes={} | networks={} | fingerprint={}".format(
        name, len(tutorial_notes), networks, actual_hash[:16]))


def main():
    hou.setUpdateMode(hou.updateMode.Manual)
    failures = []
    for name in sorted(EXPECTED):
        path = os.path.join(ROOT, name)
        try:
            verify(path)
        except Exception as exc:
            failures.append((name, str(exc)))
            print("FAIL {} | {}".format(name, exc))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
