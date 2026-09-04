from __future__ import print_function

import glob
import hashlib
import os
import sys
import traceback

import hou


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE_PREFIX = "[TUTORIAL]"

COLORS = {
    "neutral": hou.Color((0.72, 0.72, 0.66)),
    "green": hou.Color((0.36, 0.68, 0.38)),
    "blue": hou.Color((0.30, 0.54, 0.80)),
    "yellow": hou.Color((0.90, 0.76, 0.28)),
    "orange": hou.Color((0.92, 0.49, 0.20)),
    "red": hou.Color((0.78, 0.23, 0.20)),
}

INTRO_TEXT = {
    "03_Single_Infinity_Yarn_Fiber_Construction.hip": (
        "INFINITY YARN: CURVE TO FIBER\n"
        "What: builds one infinity-shaped yarn system from a guide curve, then expands it into twisted strands and irregular fibers.\n"
        "Start: enter /obj/thread7 and read from line2 downward.\n"
        "Next: inspect /obj/RENDER_YARN for render-guide transfer and localized motion.\n"
        "Result: Out_Yarnad is the dense strand output; RENDER_YARN carries the shaded presentation branch."
    ),
    "03_Three_Strand_Infinity_Yarn_and_Lint_Render.hip": (
        "THREE-STRAND INFINITY YARN + LINT\n"
        "What: develops three related yarn systems (A/B/C), their render branches, and separated lint populations.\n"
        "Start: enter /obj/thread_A; B and C repeat the same construction with different placement/look choices.\n"
        "Next: compare RENDER_YARN, RENDER_YARN1, RENDER_YARN2, then the LINT objects.\n"
        "Result: three fiber-rich yarn forms with independently controllable loose-fiber layers and V-Ray materials."
    ),
    "04_Dynamic_Knitting_Grid_Prototype.hip": (
        "DYNAMIC KNITTING GRID PROTOTYPE\n"
        "What: a compact layout study that copies short curves to a 20 x 20 target field and offsets alternating rows.\n"
        "Start: enter /obj/KnitGeo and follow the two inputs into copytopoints1.\n"
        "Next: read attribwrangle2, then polywire1.\n"
        "Result: a readable interlaced-looking grid prototype, not yet a force-transmitting knitted topology."
    ),
    "04_Cached_Knit_Lace_and_Wool_Ball_Render_Setup.hip": (
        "CACHED KNIT LACE + WOOL-BALL RENDER SETUP\n"
        "What: assembles cached lace states with four wool-ball simulation/fiber branches for lighting and look development.\n"
        "Start: inspect geo1/geo2/geo3 for lace inputs, then enter Wool_ball_1 for the clearest ball pipeline.\n"
        "Next: compare the repeated Wool_ball branches and /mat.\n"
        "Result: a staged V-Ray shot combining lace geometry, fuzzy balls, cameras, lights, and a ground/backdrop."
    ),
    "05_Yarn_Ball_Vellum_and_Fiber_Render.hip": (
        "YARN BALL: VELLUM SUPPORT TO FIBER RENDER\n"
        "What: combines wrapped-yarn construction, a lightweight Vellum support, dense post-simulation fibers, and V-Ray outputs.\n"
        "Start: enter /obj/Wool_ball_setup for the simulation-to-hair path.\n"
        "Next: enter /obj/geo7 for the procedural wrapped-yarn build; /obj/thread7 contains the reusable strand recipe.\n"
        "Result: deforming yarn/wool-ball render geometry and proxy/cache-ready outputs."
    ),
    "05_Single_Wool_Ball_Vellum_and_Fiber_Setup.hip": (
        "SINGLE WOOL BALL: VELLUM + FIBER LOOKDEV\n"
        "What: tests a deformable wool-ball support and several ways to generate, clump, shade, and export surface fibers.\n"
        "Start: enter /obj/Wool_ball4 for the compact active branch; use Wool_ball_4 to compare alternate source/solver studies.\n"
        "Next: inspect the Hair Generate/Guide Process chain and /mat/WOOL_BALL.\n"
        "Result: a single fiber-rich ball plus V-Ray proxy/export variants for the final shot."
    ),
    "07_Multicolor_Ten_Wool_Ball_Vellum_Simulation.hip": (
        "TEN WOOL BALLS: COLLECTIVE VELLUM CONTACT\n"
        "What: simulates ten soft supports together, then rebuilds dense multicolor fibers for contact and packing studies.\n"
        "Start: enter /obj/Wool_ball6 and follow sphere setup -> merge -> Vellum -> groups -> hair.\n"
        "Next: inspect /obj/Wool_balls_RENDER and /mat for per-ball color/material assignment.\n"
        "Result: a ten-ball cluster whose compression, rearrangement, and final fiber look are readable in one scene."
    ),
    "08_Cloth_Tearing_and_Stitch_Failure.hip": (
        "CLOTH TEARING + STITCH FAILURE\n"
        "What: combines cloth/stitch constraints, weak-region authoring, wind/gravity, and topology-history tests to reveal damage.\n"
        "Start: enter /obj/strings_mesh for the full strength/damage pipeline.\n"
        "Next: inspect /obj/etiquette for stitched cloth variants, then /obj/Mesh_Render for shot assembly.\n"
        "Result: torn textile surfaces, exposed filament geometry, and render branches that preserve newly opened edges."
    ),
}

DEPENDENCY_TEXT = {
    "03_Single_Infinity_Yarn_Fiber_Construction.hip": (
        "DEPENDENCY WARNING\nThe studio HDRI on F:/.../simple_lighting_h.exr and the E:/Knitting_CACHE/... test_geo cache are missing. "
        "The procedural yarn branch remains inspectable; cache- or lighting-dependent results will not reproduce exactly."
    ),
    "03_Three_Strand_Infinity_Yarn_and_Lint_Render.hip": (
        "DEPENDENCY WARNING\nThe A/B/C V-Ray proxy .vrmesh files under $HIP/geo are missing, as is the F:/ studio HDRI. "
        "Use the procedural thread branches to study construction; proxy display/render branches require regeneration."
    ),
    "04_Cached_Knit_Lace_and_Wool_Ball_Render_Setup.hip": (
        "PORTABILITY / MISSING FILES\nThe absolute D:/SELF lace caches, FBX meshes, and source textures resolve on this workstation but are not portable. "
        "Several F:/ HDRIs and the $HIP/geo V-Ray proxy are missing. Do not assume this shot is self-contained."
    ),
    "05_Yarn_Ball_Vellum_and_Fiber_Render.hip": (
        "DEPENDENCY WARNING\nThe F:/ studio HDRI and several $HIP or E:/ cache/proxy targets are missing. One E:/ V-Ray proxy resolves locally. "
        "Procedural branches are still useful, but cache/proxy flags may show placeholders or fail to cook."
    ),
    "05_Single_Wool_Ball_Vellum_and_Fiber_Setup.hip": (
        "PORTABILITY / MISSING FILES\nD:/SELF source meshes and textures resolve on this workstation but are absolute and non-portable. "
        "The F:/ HDRI and $HIP/geo animated V-Ray proxy sequence are missing; regenerate exports before final rendering."
    ),
    "07_Multicolor_Ten_Wool_Ball_Vellum_Simulation.hip": (
        "PORTABILITY NOTE\nThe D:/SELF source textures resolve locally but use absolute paths. The F:/ studio HDRI is missing. "
        "The ten-ball procedural/simulation graph is present; final lighting will differ until the HDRI is restored or relinked."
    ),
    "08_Cloth_Tearing_and_Stitch_Failure.hip": (
        "DEPENDENCY WARNING\nSeveral $HIP/tex metal/smudge/rust bitmaps and the E:/ cloth displacement texture are missing. "
        "The V-Ray mesh-export target is also absent. Simulation logic remains available, but final materials cannot match the authored look."
    ),
}


class Annotator(object):
    def __init__(self, hip_name):
        self.hip_name = hip_name
        self.used = {}
        self.created = []
        self.skipped = []

    def network_bounds(self, network):
        children = list(network.children())
        if not children:
            return (-5.0, -5.0, 5.0, 5.0)
        xs = [child.position().x() for child in children]
        ys = [child.position().y() for child in children]
        return (min(xs), min(ys), max(xs), max(ys))

    def note(self, network_path, text, color="neutral", anchors=(), side="right",
             size=(13.0, 4.5), text_size=0.55):
        network = hou.node(network_path)
        if network is None:
            self.skipped.append((network_path, "missing network"))
            return None
        try:
            children = list(network.children())
        except Exception:
            self.skipped.append((network_path, "not a network"))
            return None
        anchor_nodes = [network.node(name) for name in anchors]
        anchor_nodes = [node for node in anchor_nodes if node is not None]
        xmin, ymin, xmax, ymax = self.network_bounds(network)
        if anchor_nodes:
            ay = sum(node.position().y() for node in anchor_nodes) / float(len(anchor_nodes))
            ax = sum(node.position().x() for node in anchor_nodes) / float(len(anchor_nodes))
        else:
            ay = ymax
            ax = xmin
        width, height = size
        gap = 4.0
        if side == "left":
            x = xmin - width - gap
            y = ay - height * 0.5
        elif side == "right":
            x = xmax + gap
            y = ay - height * 0.5
        elif side == "above":
            x = ax
            y = ymax + gap
        else:
            x = ax
            y = ymin - height - gap

        key = (network_path, side)
        rectangles = self.used.setdefault(key, [])
        def overlaps(rect):
            rx, ry, rw, rh = rect
            return not (x + width + 1.0 < rx or rx + rw + 1.0 < x or
                        y + height + 1.0 < ry or ry + rh + 1.0 < y)
        while any(overlaps(rect) for rect in rectangles):
            y -= height + 2.0
        rectangles.append((x, y, width, height))

        try:
            note = network.createStickyNote()
        except hou.OperationFailed:
            # Built-in HDAs such as Vellum Solver may expose their contents for
            # inspection while remaining asset-locked.  Unlocking them would be
            # a behavioral scene edit, so document them from the editable parent.
            self.skipped.append((network_path, "asset-locked network"))
            return None
        note.setText(NOTE_PREFIX + "\n" + text)
        note.setColor(COLORS[color])
        note.setTextColor(hou.Color((0.04, 0.04, 0.04)))
        note.setDrawBackground(True)
        note.setTextSize(text_size)
        note.setBounds(hou.BoundingRect(x, y, x + width, y + height))
        self.created.append(network_path)
        return note

    def intro(self):
        self.note("/obj", INTRO_TEXT[self.hip_name], "neutral", side="above",
                  size=(21.0, 7.0), text_size=0.72)
        if self.hip_name in DEPENDENCY_TEXT:
            self.note("/obj", DEPENDENCY_TEXT[self.hip_name], "red", side="left",
                      size=(17.0, 5.8), text_size=0.56)


def remove_previous_tutorial_notes():
    removed = 0
    for root_path in ("/obj", "/mat", "/out", "/stage"):
        root = hou.node(root_path)
        if root is None:
            continue
        for network in (root,) + root.allSubChildren():
            try:
                notes = [note for note in network.stickyNotes()
                         if note.text().startswith(NOTE_PREFIX)]
                for note in notes:
                    note.destroy()
                    removed += 1
            except Exception:
                pass
    return removed


def annotate_yarn_builder(a, path, output_name="Out_Yarnad", cache_warning=True):
    a.note(path,
           "STEP 1 - AUTHOR THE MASTER PATH\nline2 creates the guide; Bend closes it through 360 degrees and the second Bend adds counter-twist. "
           "attribwrangle5 applies a helical offset with twist_amount, frequency, and amplitude. In this family, frequency 0.168 and amplitude 0.02 are especially influential.",
           "green", ("line2", "bend1", "twist1", "attribwrangle5"), "left", (16, 6.4))
    a.note(path,
           "STEP 2 - REPEAT, RESAMPLE, AND MAKE A FIRST BUNDLE\ncopy1 multiplies the guide population (animated from 50 copies at frame 1 to 200 at frame 72 in the inspected source). "
           "Resampling sets segment length before sweep8 creates volume; group/blast nodes reject selected regions before later expansion.",
           "blue", ("copy1", "resample2", "sweep8", "blast2"), "right", (16, 6.2))
    a.note(path,
           "STEP 3 - SEPARATE FIBER BEHAVIORS\nGroup Expression, Blast, Attribute Noise, and color wrangles split the bundle into fuzzy populations. "
           "Different noise scales keep the surface from looking like one uniform displacement. Color wrangles use custom VEX; preserve strand identity if adapting this for deformation.",
           "blue", ("groupexpression1", "mountain1", "mountain2", "mountain3", "attribwrangle7"), "left", (16, 6.3))
    a.note(path,
           "STEP 4 - BUILD A STABLE FRAME, THEN NEST TWIST\nresample4/6 control density and polyframe3 writes tangent/orientation data so cross-sections follow the curved guide coherently. "
           "sweep18 and sweep20 create nested strand/fiber volume. These are the main geometry multipliers and can become very expensive.",
           "yellow", ("resample4", "polyframe3", "sweep18", "sweep20"), "right", (16, 6.0))
    a.note(path,
           "STEP 5 - ADD FLYAWAYS AND PRUNE\nMore group/blast/noise branches create different loose-fiber populations; pointvop22/23 add anti-aliased noise displacement before merge4 reunites them. "
           "Experiment with amplitudes and group thresholds one stage at a time: dense branches can grow to millions of points.",
           "yellow", ("pointvop22", "pointvop23", "mountain11", "merge4"), "left", (16, 6.0))
    tail = (
        "STEP 6 - CLEAN, CACHE, AND PUBLISH\nThe final branch removes attributes, creates UV/debug shading, cleans/packs geometry, and exposes {} as the intended output. ".format(output_name)
    )
    if cache_warning:
        tail += "test_geo points to an external E:/ cache that is missing here; do not enable a load-from-disk path unless the cache is restored."
        color = "red"
    else:
        tail += "Cache/proxy ROPs are optional publishing branches; the procedural output remains the source of truth."
        color = "blue"
    a.note(path, tail, color,
           ("attribdelete1", "uvproject1", "clean1", "test_geo", output_name), "right", (16, 6.2))
    for vop_name in ("pointvop22", "pointvop23"):
        vop = hou.node(path + "/" + vop_name)
        if vop is not None and vop.children():
            a.note(vop.path(),
                   "NOISE DISPLACEMENT VOP\nPosition feeds anti-aliased noise, the result is scaled/multiplied, then added back to P. "
                   "This supplies fine irregularity to selected fiber groups; amplitude is the safe artistic control, while wiring/order should remain intact.",
                   "blue", ("aanoise2", "multiply1", "add1"), "right", (13, 5.2))


def annotate_render_yarn(a, path):
    a.note(path,
           "RENDER INPUT AND TRIM\nObject Merge brings in the lighter yarn result. UV/Carve/Wrangle nodes restrict or trim the portion used for presentation so downstream shading and animation work on a controlled subset.",
           "green", ("object_merge1", "uvtexture1", "carve4", "attribwrangle2"), "left", (14, 5.2))
    a.note(path,
           "LOCALIZED PROCEDURAL MOTION\nSphere/mask branches define an influence region. The custom VEX wrangles build a binary mask and add time-varying sine/noise displacement inside it. "
           "The hard mask edge is diagnostic and can become visible; radius, frequency, amplitude, noise amplitude, and speed are the experiment controls.",
           "yellow", ("sphere1", "maskfromgeometry1", "attribwrangle12", "attribwrangle14"), "right", (15, 6.4))
    a.note(path,
           "PRESENTATION OUTPUT\nAttribute transfer/color branches carry look information to the render geometry, then Material nodes assign the V-Ray shader. "
           "OUT_Render is the clean handoff. Nearest-point color transfer is fast but can jump between nearby strands if identity is not preserved.",
           "blue", ("attribtransfer1", "material1", "material4", "OUT_Render"), "left", (15, 6.0))
    vop = hou.node(path + "/attribvop3")
    if vop is not None and vop.children():
        a.note(vop.path(),
               "MULTI-SCALE SURFACE DISPLACEMENT\nWorley and turbulent noise branches are shaped by ramps and scale controls, then fed into displacement-normal outputs. "
               "This is render detail, not the simulated support: adjust frequency/amplitude/roughness for breakup, not Vellum behavior.",
               "yellow", ("worleynoise1", "turbnoise1", "ramp1", "displacenml1"), "right", (15, 5.8))


def annotate_auto_dop_and_ground(a):
    for path in ("/obj/AutoDopNetwork",):
        if hou.node(path) is not None:
            a.note(path,
                   "SCENE COLLISION SUPPORT\nThis DOP network provides the static ground plane, gravity, and static solver used by the scene-level floor object. "
                   "The main wool/cloth dynamics live inside the Vellum Solver SOPs; this network is supporting collision infrastructure.",
                   "orange", ("groundplane1", "gravity1", "staticsolver1", "output"), "right", (15, 5.8))
    for path in ("/obj/grid1",):
        if hou.node(path) is not None:
            a.note(path,
                   "FLOOR / BACKDROP GEOMETRY\nA Grid is bent, subdivided, transformed, and shaded to make the visible floor or sweep behind the simulated object. "
                   "This is presentation geometry; it does not define the material response.",
                   "neutral", ("grid1", "bend1", "subdivide1", "material1"), "right", (13, 5.0))


def annotate_wool_pipeline(a, path, exact=""):
    if hou.node(path) is None:
        return
    a.note(path,
           "STEP 1 - BUILD THE LIGHTWEIGHT SUPPORT\nSphere/import branches establish the ball volume; Mountain and Transform nodes break the perfect silhouette and place variants. "
           "Rest/UV/color attributes are captured before simulation so later fibers and shading have a stable reference.",
           "green", ("sphere1", "sphere4", "mountain1", "merge4", "rest1"), "left", (15, 6.0))
    sim_text = (
        "STEP 2 - CONSTRAINTS AND VELLUM SOLVE\nVellum Constraints turns the lightweight surface into stretch/bend constraints; the Vellum Solver resolves self-contact, collisions, forces, and time integration. "
        "The dense rendered fibers are deliberately not simulated strand-by-strand. " + exact
    )
    a.note(path, sim_text, "orange",
           ("vellumconstraints1", "vellumconstraints2", "vellumsolver1", "vellumsolver3", "vellumsolver4"), "right", (16, 7.1))
    a.note(path,
           "STEP 3 - CACHE / HOLD THE SOLVED SUPPORT\nTime Shift and File Cache branches freeze or store the lightweight solve before expensive grooming. "
           "A missing cache is not equivalent to missing procedural setup: disable load-from-disk or regenerate with the original frame range and seeds.",
           "red", ("timeshift1", "filecache1", "subdivide1"), "left", (15, 6.1))
    a.note(path,
           "STEP 4 - GENERATE THE VISIBLE FIBERS\nHair Generate scatters curves over the solved skin. Guide Process nodes change length, direction, bend/noise, and lift; Hair Clump nodes organize fibers at several scales. "
           "This stage creates the wool appearance while inheriting the support's deformation.",
           "blue", ("hairgen2", "hairgen3", "guideprocess5", "guideprocess16", "hairclump1", "hairclump2"), "right", (16, 6.6))
    a.note(path,
           "STEP 5 - MERGE, SHADE, AND PUBLISH\nThe groom populations are merged, optional attribute/material adjustments are applied, and OUT_ball / RENDER_WOOL_FIBERS / proxy ROPs expose usable results. "
           "Display/render flags identify the current branch; do not change them merely to tidy the graph.",
           "blue", ("merge2", "material3", "OUT_ball", "RENDER_WOOL_FIBERS", "vrayProxyExport_single_sphere"), "left", (16, 6.2))
    hair = hou.node(path + "/hairgen3")
    if hair is not None and hair.children():
        a.note(hair.path(),
               "HAIR GENERATE INTERNAL FLOW\nREST_SKIN, ANIM_SKIN, and GUIDES are normalized, attributes and tangent space are prepared, points are scattered, and hairgencore emits OUTPUT_CURVES. "
               "Treat this as Houdini's implementation detail: density/mask/seed controls belong on the Hair Generate SOP interface.",
               "neutral", ("REST_SKIN", "ANIM_SKIN", "scatter2", "hairgencore", "OUTPUT_CURVES"), "right", (16, 6.3))


def annotate_vellum_internals(a):
    obj = hou.node("/obj")
    if obj is None:
        return
    for solver_sop in obj.allSubChildren():
        if solver_sop.type().name() != "vellumsolver" or not solver_sop.children():
            continue
        scene_is_cloth = a.hip_name.startswith("08_")
        subject = "cloth/stitch constraints" if scene_is_cloth else "the ball support constraints"
        a.note(solver_sop.path(),
               "VELLUM SOLVER SOP WRAPPER\nThis internal network packages inputs, resets simulation state, runs dopnet1, imports solved geometry/constraints, and publishes the SOP output. "
               "For tutorial work, inspect dopnet1; avoid editing these internal switches and import nodes because they are part of Houdini's solver wrapper.",
               "red", ("reset_frame", "dopnet1", "dopimport_geometry", "output1"), "left", (16, 6.4))
        dopnet = solver_sop.node("dopnet1")
        if dopnet is None:
            continue
        force_text = (
            "FORCES AND COLLISIONS\nThe Vellum object receives {}, then the solver combines gravity/wind or custom POP forces with self-collision, the ground plane, and any external collider. ".format(subject)
        )
        if scene_is_cloth:
            force_text += "This study uses two substeps, 100 constraint iterations, 10 smoothing iterations, 10 collision passes, three post-collision passes, gravity -9.80665/4, and wind (2, 0.5, 0)."
        else:
            force_text += "Open the Solver SOP interface to tune substeps and collision/constraint iterations; the Forces subnet contains the authored POP force nodes."
        a.note(dopnet.path(), force_text, "orange",
               ("forces", "gravity1", "groundplane", "external", "vellumsolver1"), "left", (17, 7.0))
        a.note(dopnet.path(),
               "SIMULATION FLOW\nsources creates the Vellum object/constraints, merge nodes combine collisions and forces, vellumsolver1 advances the state, and output publishes the solved result. "
               "Changing order or merge relationships changes behavior; experiment through exposed parameters instead.",
               "blue", ("sources", "merge2", "vellumsolver1", "output"), "right", (16, 6.2))
        forces = dopnet.node("forces")
        if forces is not None and forces.children():
            if scene_is_cloth:
                text = "AUTHORED FORCE SUBNET\nPOP Wind feeds the cloth solve; scene gravity is merged alongside it. Wind direction and strength drive folds and help open damaged regions after constraints release."
            else:
                text = "AUTHORED FORCE SUBNET\nPOP Attract / POP Force nodes provide directed motion beyond gravity. They act on the lightweight support, so their influence is inherited by the post-simulation fibers."
            a.note(forces.path(), text, "orange", ("popwind1", "popattract1", "popforce1", "FORCE"), "right", (14, 5.5))


def annotate_popnets(a):
    obj = hou.node("/obj")
    if obj is None:
        return
    for node in obj.allSubChildren():
        if node.type().name() != "dopnet" or not node.name().startswith("popnet"):
            continue
        a.note(node.path(),
               "POP SUPPORT SOLVE\nThe first input is sourced as particles, interaction/grains establish neighbor response, wind and gravity drive motion, and the POP Solver advances the state before output. "
               "This branch supports strand/thread motion; compare it with the Vellum branch rather than assuming both solve the same representation.",
               "orange", ("source_first_input", "popgrains1", "popwind1", "gravity1", "popsolver", "output"), "right", (16, 6.6))


def annotate_materials_and_outputs(a):
    mat = hou.node("/mat")
    if mat is not None and mat.children():
        overview = (
            "MATERIAL LIBRARY\nMaterial builders separate source color/user attributes, procedural noise/falloff, BRDF or hair response, and the V-Ray output. "
            "Many similarly named materials are look-development variants; follow the assigned Material SOP before editing a candidate."
        )
        if a.hip_name.startswith("08_"):
            overview += " Several bitmap inputs are missing, so flat/procedural colors may display while textured metal/cloth details do not."
        a.note("/mat", overview, "neutral", side="above", size=(20, 6.2), text_size=0.62)
        for material in mat.children():
            try:
                children = material.children()
            except Exception:
                continue
            if not children:
                continue
            names = {child.type().name() for child in children}
            if not any("material" in material.type().name().lower() for _ in (0,)):
                continue
            is_hair = any("Hair" in name for name in names) or "hair" in material.name().lower() or "wool" in material.name().lower()
            if is_hair:
                text = (
                    "WOOL / HAIR SHADER FLOW\nColor constants, user color, noise, mixes, and falloff shape strand variation before the V-Ray Hair/BRDF nodes. "
                    "The material output is the final handoff. Color/noise are useful look controls; preserve the BRDF-to-output connection."
                )
            elif "textile" in material.name().lower() or "filament" in material.name().lower():
                text = (
                    "TEXTILE SHADER FLOW\nColor/texture controls feed the cloth or filament BRDF and then the V-Ray output. Separate weak-cloth and filament variants make newly exposed regions readable after tearing. "
                    "Missing bitmaps affect appearance only, not the solve."
                )
            else:
                text = (
                    "MATERIAL FLOW\nSource colors or bitmaps are corrected and mixed, optional falloff/noise adds variation, the BRDF defines surface response, and the V-Ray Output publishes the shader. "
                    "Adjust upstream look controls; keep the final output wiring intact."
                )
            a.note(material.path(), text, "yellow", side="right", size=(14, 5.6))
    out = hou.node("/out")
    if out is not None and out.children():
        a.note("/out",
               "RENDER OUTPUTS\nThese ROPs store final and interactive V-Ray/Mantra render variants. Camera, frame range, resolution, image path, and AOV settings are shot-critical. "
               "Several output paths use $HIP and may point to folders that do not yet exist; that is an export destination, not necessarily a missing input dependency.",
               "neutral", side="above", size=(20, 6.3), text_size=0.62)


def annotate_scene(a):
    name = a.hip_name
    a.intro()

    if name == "04_Dynamic_Knitting_Grid_Prototype.hip":
        p = "/obj/KnitGeo"
        a.note(p,
               "STEP 1 - SOURCE STITCH SEGMENT\nThe curve/line branch defines a short three-point strand, then Transform, Resample, and UV Texture prepare a reusable piece for copying.",
               "green", ("curve1", "line1", "transform1", "resample1", "uvtexture1"), "left", (14, 5.0))
        a.note(p,
               "STEP 2 - TARGET FIELD\nGrid and Scatter create a 20 x 20 distribution with 400 target points. attribwrangle1 adds small alternating variation before placement; its strands_per_row and sine/cosine offsets control the preview rhythm.",
               "blue", ("grid1", "scatter2", "attribwrangle1"), "right", (15, 5.8))
        a.note(p,
               "STEP 3 - COPY AND OFFSET ROWS\ncopytopoints1 places one independent curve on each target. attribwrangle2 lifts alternating rows by 0.1 using floor(@ptnum / 10). "
               "That divisor is the key layout assumption: changing point order or row length changes the pattern.",
               "yellow", ("copytopoints1", "attribwrangle2"), "left", (15, 6.0))
        a.note(p,
               "STEP 4 - DISPLAY OUTPUT / LIMITATION\npolywire1 gives the curves visible thickness. The result contains 400 separate primitives with no shared stitch points, so forces cannot travel through it like a real knitted loop network. "
               "Treat this as a layout prototype, not a finished knit simulation.",
               "red", ("polywire1",), "right", (16, 6.3))

    elif name == "03_Single_Infinity_Yarn_Fiber_Construction.hip":
        a.note("/obj", "PRIMARY PROCEDURAL OBJECT\nEnter thread7 first. It contains the complete guide-to-strand-to-fiber build and publishes Out_Yarnad.", "green", ("thread7",), "right", (13, 4.5))
        a.note("/obj", "PRESENTATION BRANCH\nRENDER_YARN imports the procedural result, adds localized motion/detail, and assigns the wool material. Cameras and V-Ray lights surround these two geometry objects.", "blue", ("RENDER_YARN",), "right", (14, 5.0))
        annotate_yarn_builder(a, "/obj/thread7")
        annotate_render_yarn(a, "/obj/RENDER_YARN")

    elif name == "03_Three_Strand_Infinity_Yarn_and_Lint_Render.hip":
        a.note("/obj", "A / B / C PROCEDURAL SOURCES\nthread_A, thread_B, and thread_C repeat one yarn recipe so placement, color, and breakup can be developed independently. Start with A, then compare only the changed parameters in B/C.", "green", ("thread_A", "thread_B", "thread_C"), "left", (16, 5.6))
        a.note("/obj", "RENDER + LINT PAIRS\nEach RENDER_YARN object handles the shaded core; the neighboring LINT object isolates sparse loose fibers. This separation keeps the final fuzz tunable without rebuilding the entire strand mass.", "blue", ("RENDER_YARN", "RENDER_YARN1", "RENDER_YARN2", "LINT", "LINT1", "LINT2"), "right", (16, 5.8))
        for thread, out_name in (("thread_A", "Out_Yarn_For_animated_individual"), ("thread_B", "Out_Yarn_For_animated_individual"), ("thread_C", "Out_Yarn_For_animated_individual")):
            annotate_yarn_builder(a, "/obj/" + thread, out_name, cache_warning=False)
        for render in ("RENDER_YARN", "RENDER_YARN1", "RENDER_YARN2"):
            annotate_render_yarn(a, "/obj/" + render)
        for lint in ("LINT", "LINT1", "LINT2"):
            a.note("/obj/" + lint,
                   "LINT ISOLATION\nObject Merge imports the source's lint-marked population; Group Expression and Blast keep only the selected flyaways, and OUT_lint publishes the sparse layer. "
                   "Tune selection thresholds upstream rather than adding density after the fact.",
                   "blue", ("OUT_lint_RENDER", "groupexpression12", "blast11", "OUT_lint"), "right", (14, 5.6))

    elif name == "04_Cached_Knit_Lace_and_Wool_Ball_Render_Setup.hip":
        a.note("/obj", "LACE INPUTS\ngeo1/geo2/geo3 load three cached/proxy lace states for the shot. They are absolute D:/SELF paths that resolve here; geo2's local $HIP proxy is missing. These objects are staging inputs, not procedural lace construction.", "red", ("geo1", "geo2", "geo3"), "left", (16, 6.0))
        a.note("/obj", "WOOL-BALL VARIANTS\nWool_ball and Wool_ball_1/_2/_3 repeat the same support-sim-to-hair idea with different imported sources, positions, and materials. ball_1/_2/_3 are simple render-assignment wrappers.", "blue", ("Wool_ball", "Wool_ball_1", "Wool_ball_2", "Wool_ball_3", "ball_1", "ball_2", "ball_3"), "right", (16, 5.8))
        for path in ("/obj/Wool_ball", "/obj/Wool_ball_1", "/obj/Wool_ball_2", "/obj/Wool_ball_3"):
            annotate_wool_pipeline(a, path, "This scene uses repeated ball variants; compare constraints before assuming the values match between branches.")
        for geo in ("geo1", "geo2", "geo3"):
            if hou.node("/obj/" + geo) is not None:
                a.note("/obj/" + geo,
                       "CACHED LACE / PROXY INPUT\nFile or V-Ray Proxy nodes load a prepared lace state; Resample/export nodes adapt it for the shot. "
                       "Because this object depends on external geometry, missing files cannot be reconstructed from this network alone.",
                       "red", side="right", size=(14, 5.6))
        annotate_auto_dop_and_ground(a)

    elif name == "05_Yarn_Ball_Vellum_and_Fiber_Render.hip":
        a.note("/obj", "MAIN DEFORMATION PIPELINE\nWool_ball_setup is the clearest simulation-to-fiber branch. The internal Vellum support is light enough to solve; Hair Generate and clumping rebuild the expensive visible surface afterward.", "green", ("Wool_ball_setup",), "left", (16, 5.5))
        a.note("/obj", "WRAPPED-YARN CONSTRUCTION\ngeo7 is the large procedural yarn-ball build. thread7 supplies the reusable twisted-strand recipe; geo1/geo4/file1/geo5 are cache, deform, and V-Ray proxy staging branches.", "blue", ("geo7", "thread7", "geo1", "geo4", "file1", "geo5"), "right", (16, 5.8))
        annotate_wool_pipeline(a, "/obj/Wool_ball_setup",
                               "The V8 study records stretch stiffness 1, damping 0.001, bend stiffness 1e7, bend damping 0.01, stretch plasticity/breaking threshold 0.01; gravity is zero, solver iterations are high, and substeps rise after frame 72.")
        annotate_yarn_builder(a, "/obj/thread7")
        annotate_render_yarn(a, "/obj/RENDER_YARN")
        p = "/obj/geo7"
        a.note(p, "STEP 1 - PROCEDURAL WRAP PATHS\nLine/circle inputs and multiple custom VEX wrangles generate spiral/orbital guide paths. Bend/Twist/Copy/Sweep nodes turn those paths into repeated yarn. "
                  "The many bypassed wrangles are experiments; active flags define the authored result.", "green", ("line7", "circle3", "pointwrangle5", "bend6", "twist6", "copy8", "sweep4"), "left", (17, 6.4))
        a.note(p, "STEP 2 - SHAPE AND SUPPORT VOLUME\nScatter, Ray, Sweep, Tube, PolyFrame, and extrusion stages organize strands around a ball-like support. "
                  "VDB From Polygons / reshape / convert create a smooth proxy volume used for robust deformation and transfer.", "blue", ("scatter_points2", "ray1", "tube1", "polyframe2", "vdbfrompolygons1", "vdbreshapesdf1", "convertvdb1"), "right", (17, 6.2))
        a.note(p, "STEP 3 - DEFORM HIGH DETAIL FROM A LIGHT DRIVER\nRest, Object Merge, edits, and Point Deform transfer motion from a simpler support onto the wrapped yarn. OUT_for_RENDER exposes the deformed high-detail branch.", "orange", ("rest1", "object_merge2", "pointdeform2", "OUT_for_RENDER"), "left", (16, 5.5))
        a.note(p, "STEP 4 - SECONDARY FIBER BREAKUP\nGroup expressions, blasts, Mountain noise, and the VOP branch create loose populations and small-scale irregularity before merge5. "
                  "This is appearance detail; keep it downstream of the deformation driver for tractable iteration.", "blue", ("groupexpression13", "mountain17", "pointvop22", "merge5"), "right", (16, 5.8))
        a.note(p, "CACHE / EXPORT BOUNDARY\nThe file-cache and V-Ray proxy branches publish heavy intermediate/final geometry. Several referenced targets are missing. "
                  "ball_still_for_setup2 and out_lint are the readable handoffs; regenerate caches from the procedural branch when needed.", "red", ("test_geo", "vdb_geo2", "ball_still_for_setup1", "ball_still_for_setup_resampled", "out_lint", "vrayProxyExport_ball_preview"), "left", (17, 6.2))
        annotate_auto_dop_and_ground(a)

    elif name == "05_Single_Wool_Ball_Vellum_and_Fiber_Setup.hip":
        a.note("/obj", "COMPACT ACTIVE STUDY\nEnter Wool_ball4 first: it contains the current deformable support, post-simulation groom, and proxy outputs. Wool_ball_4 preserves broader source/solver comparisons and look-development experiments.", "green", ("Wool_ball4", "Wool_ball_4"), "left", (16, 5.8))
        a.note("/obj", "SHOT OUTPUT WRAPPERS\nball_5 assigns the final surface material; geo1 loads or exposes the V-Ray proxy sequence. The proxy sequence under $HIP/geo is missing and must be regenerated for that branch.", "red", ("ball_5", "geo1"), "right", (15, 5.4))
        exact = "This V9 study uses bend stiffness 1e-1 and disables stretch plasticity; compare that intentionally softer response with the much stiffer V8 scene."
        annotate_wool_pipeline(a, "/obj/Wool_ball4", exact)
        annotate_wool_pipeline(a, "/obj/Wool_ball_4", exact)
        annotate_auto_dop_and_ground(a)

    elif name == "07_Multicolor_Ten_Wool_Ball_Vellum_Simulation.hip":
        a.note("/obj", "SIMULATION SOURCE\nWool_ball6 builds ten support spheres, merges and solves them together, then generates fibers. This shared solve is what produces collective contact and packing.", "green", ("Wool_ball6",), "left", (15, 5.2))
        a.note("/obj", "FINAL COLOR / RENDER BRANCHES\nball_10 isolates the ten solved pieces for material assignment; Wool_balls_RENDER performs the final group/attribute/material handoff. /mat contains the colorway library.", "blue", ("ball_10", "Wool_balls_RENDER"), "right", (16, 5.5))
        p = "/obj/Wool_ball6"
        a.note(p, "STEP 1 - TEN SUPPORT OBJECTS\nTen Sphere/Mountain/Transform branches create softly irregular balls and place them for contact. UV Project/Quick Shade nodes provide per-piece look data before the branches merge.", "green", ("sphere7", "sphere13", "mountain7", "transform25", "uvproject10", "merge4"), "left", (16, 5.8))
        a.note(p, "STEP 2 - CONSTRAINTS + COLLECTIVE VELLUM SOLVE\nvellumconstraints2 creates the deformable surfaces and vellumsolver3 solves them together with self-collision and external ground contact. "
                  "The multicolor study uses bend stiffness 1e-3 with plasticity: an exploratory response, not a calibrated wool measurement.", "orange", ("vellumconstraints2", "vellumsolver3"), "right", (17, 6.2))
        a.note(p, "STEP 3 - PRESERVE PIECE IDENTITY\nBlast and Group nodes split the solved merge back into ten named populations. These groups let material and fiber attributes follow the correct ball after contact and reordering.", "blue", ("blast1", "blast15", "group1", "group15", "merge5"), "left", (16, 5.6))
        a.note(p, "STEP 4 - CACHE THE LIGHT SOLVE\nfilecache1 stores the solved supports before grooming. Regenerate with consistent frame range and seeds if the cache is absent; do not simulate the dense final hair directly.", "red", ("filecache1", "subdivide1"), "right", (15, 5.2))
        a.note(p, "STEP 5 - BUILD MULTI-SCALE WOOL\nHair Generate scatters surface curves; Guide Process changes length/direction/noise; Group/Attribute Transfer keeps each ball's colorway; Hair Clump builds larger tufts. "
                  "merge2 and null2 publish the combined fiber result.", "blue", ("hairgen2", "hairgen3", "guideprocess16", "grouptransfer1", "attribtransfer1", "hairclump2", "merge2", "null2"), "left", (17, 6.2))
        for path in ("/obj/ball_10", "/obj/Wool_balls_RENDER"):
            a.note(path, "PER-BALL LOOK ASSIGNMENT\nObject Merge imports the solved/fiber result; repeated Blast/Group nodes recover the ten pieces; merge and Material/UV nodes assign the chosen palette for final rendering. "
                     "The repeated structure is intentional because every ball can carry a distinct material.", "blue", side="right", size=(16, 5.8))
        annotate_auto_dop_and_ground(a)

    elif name == "08_Cloth_Tearing_and_Stitch_Failure.hip":
        a.note("/obj", "SIMULATION + DAMAGE ANALYSIS\nstrings_mesh contains the full cloth preparation, strength field, Vellum solve, neighbor-history damage test, and strand render build. etiquette contains a second stitched-cloth construction with explicit edited regions.", "green", ("strings_mesh", "etiquette"), "left", (17, 5.8))
        a.note("/obj", "RENDER ASSEMBLY\nMesh_Render combines textile, weak textile, and filament branches. The four small output objects assign final materials so torn surfaces and exposed threads can be shaded separately.", "blue", ("Mesh_Render", "textile", "textile_weak", "filament", "filament1"), "right", (16, 5.5))
        p = "/obj/strings_mesh"
        a.note(p, "STEP 1 - AUTHOR THE CLOTH / THREAD TOPOLOGY\nGrid, transforms, edits, groups, remesh, line conversion, subdivision, and Fuse establish the starting surface and strand structure. "
                  "The explicit groups define attachment and region boundaries used later by constraints.", "green", ("grid1", "bend2", "group7", "remesh1", "convertline1", "fuse1"), "left", (17, 6.0))
        a.note(p, "STEP 2 - WRITE PHYSICAL ATTRIBUTES\nSet_pscale and Set_restlength define collision/constraint scale. Noise_up_the_strength creates a varying strength field; Group_weak selects @weak < 0.2 and Set_strength assigns weak versus strong values. "
                  "These custom attributes control where damage begins.", "yellow", ("Set_pscale", "Set_restlength", "Noise_up_the_strength", "Group_weak", "Set_strength"), "right", (18, 6.5))
        a.note(p, "STEP 3 - CLOTH CONSTRAINTS AND SOLVE\nvellumcloth2 uses varying mass, uniform thickness, compression, and bend stiffness 1e-4. vellumsolver2 advances the surface with wind/gravity/collisions. "
                  "This is the main deformation stage; strength fields and constraint settings determine whether load remains distributed or localizes.", "orange", ("vellumcloth2", "vellumsolver2"), "left", (18, 6.3))
        a.note(p, "STEP 4 - HOLD REFERENCE STATE AND DEFORM DETAIL\nTime Shift/Rest nodes preserve the initial state; Point Deform carries the solved motion onto higher-detail geometry. "
                  "The POP branches offer a related strand/particle treatment and should be compared as a different representation.", "blue", ("timeshift1", "Hold_strength", "rest1", "pointdeform2", "popnet1", "popnet"), "right", (17, 6.0))
        a.note(p, "STEP 5 - DETECT TOPOLOGY CHANGE\nneighbour_start stores each point's initial neighbor count; neighbour_sim measures the simulated state; compare and delete_based_on_neighbours mark points whose adjacency dropped. "
                  "This assumes matching point numbers between inputs. Persistent IDs are required if caching or remeshing changes numbering.", "red", ("neighbour_start", "neighbour_sim", "compare", "delete_based_on_neighbours"), "left", (18, 6.5))
        a.note(p, "STEP 6 - BUILD VISIBLE TORN THREADS\nDelete/Isolate nodes select damaged regions; Subdivide and Sweep turn released curves into visible strands; UV, Point Deform, smoothing, normals, clean, and merge prepare OUT_FOR_RENDER / OUT_FOR_CLOSEUP_RENDER.", "blue", ("isolate_weak", "delete1", "subdivide7", "sweep3", "OUT_FOR_CLOSEUP_RENDER", "sweep4", "normal2", "merge1", "OUT_FOR_RENDER"), "right", (18, 6.2))
        vop = hou.node(p + "/Noise_up_the_strength")
        if vop is not None:
            a.note(vop.path(), "STRENGTH-NOISE VOP\nTurbulent noise is split and bound into the strength-related attribute consumed downstream. "
                   "Frequency, amplitude, roughness, attenuation, and offset control defect scale and placement; this field influences failure localization.", "yellow", ("turbnoise1", "vectofloat1", "bind1"), "right", (15, 5.6))
        q = "/obj/etiquette"
        a.note(q, "STEP 1 - SECOND CLOTH / LABEL SOURCE\nObject Merge imports a base, then a long sequence of Edit, Group, Time Shift, Rest, and Subdivide nodes sculpts and freezes explicit regions. "
                  "The edits are authored shape decisions and should not be normalized or deleted for graph cleanliness.", "green", ("object_merge1", "edit4", "group1", "timeshift1", "rest1", "edit15", "subdivide1"), "left", (17, 6.0))
        a.note(q, "STEP 2 - CLOTH + STITCH CONSTRAINTS\nThe cloth nodes create surface stretch/bend behavior. vellumstitch2 connects explicit point groups with Stitch Points constraints: mass 1, thickness 0.01, stretch stiffness 10,000, damping 0.5, rest length 0.1. "
                  "These constraints carry tension until the authored failure/release behavior changes support.", "orange", ("vellumcloth2", "vellumstitch2", "vellumconstraints1", "vellumconstraints2"), "right", (18, 7.0))
        a.note(q, "STEP 3 - SOLVER VARIANTS AND OUTPUT\nvellumsolver2/vellumsolver3 preserve alternate cloth/stitch trials; display/render flags indicate the authored result. "
                  "Use the internal DOP networks to inspect forces, but tune exposed Solver parameters rather than editing wrapper switches.", "blue", ("vellumsolver2", "vellumsolver3"), "left", (17, 5.8))
        a.note("/obj/Mesh_Render", "SHOT ASSEMBLY\nObject Merge gathers the solved textile and filament branches. Time Shift/Blast/Pack separate render pieces, Material nodes assign looks, and merge1 combines the published surfaces. "
               "OUT_RENDER is the inspection handoff; the proxy ROP is an optional export target.", "blue", ("object_merge1", "timeshift1", "blast1", "pack1", "material9", "merge1", "OUT_RENDER"), "right", (16, 6.0))
        for path in ("/obj/filament", "/obj/filament1", "/obj/textile", "/obj/textile_weak"):
            a.note(path, "FINAL SHADING WRAPPER\nObject Merge imports one logical render layer and the Material SOP assigns its dedicated shader. Keeping layers separate makes normal cloth, weak cloth, and exposed filaments independently art-directable.", "blue", side="right", size=(14, 5.2))
        annotate_popnets(a)

    annotate_vellum_internals(a)
    annotate_materials_and_outputs(a)


def update_hash(hasher, value):
    hasher.update((str(value) + "\n").encode("utf-8", "replace"))


def structural_fingerprint():
    """Hash behavior-bearing scene state while intentionally excluding sticky notes."""
    h = hashlib.sha256()
    update_hash(h, (hou.fps(), tuple(hou.playbar.frameRange()), tuple(hou.playbar.playbackRange())))
    for root_path in ("/obj", "/mat", "/out", "/stage", "/tasks"):
        root = hou.node(root_path)
        if root is None:
            continue
        nodes = (root,) + root.allSubChildren()
        for node in sorted(nodes, key=lambda item: item.path()):
            update_hash(h, (node.path(), node.type().nameWithCategory(), tuple(node.position()),
                            tuple(node.color().rgb()), node.comment()))
            update_hash(h, tuple(inp.path() if inp else None for inp in node.inputs()))
            for method in ("isDisplayFlagSet", "isRenderFlagSet", "isTemplateFlagSet", "isBypassed", "isSelectableInViewport"):
                try:
                    update_hash(h, (method, getattr(node, method)()))
                except Exception:
                    pass
            for parm in node.parms():
                try:
                    raw = parm.rawValue()
                except Exception:
                    try:
                        raw = parm.unexpandedString()
                    except Exception:
                        raw = "<unreadable>"
                update_hash(h, (parm.path(), raw, parm.isLocked()))
                try:
                    for keyframe in parm.keyframes():
                        update_hash(h, keyframe.asCode())
                except Exception:
                    pass
    return h.hexdigest()


def count_tutorial_notes():
    counts = {}
    for root_path in ("/obj", "/mat", "/out", "/stage"):
        root = hou.node(root_path)
        if root is None:
            continue
        for network in (root,) + root.allSubChildren():
            try:
                count = sum(1 for note in network.stickyNotes()
                            if note.text().startswith(NOTE_PREFIX))
            except Exception:
                continue
            if count:
                counts[network.path()] = count
    return counts


def process(path):
    path = os.path.abspath(path)
    name = os.path.basename(path)
    if name not in INTRO_TEXT:
        raise RuntimeError("No tutorial specification for " + name)
    temp_path = path + ".annotating.hip"
    if os.path.exists(temp_path):
        os.remove(temp_path)

    hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
    before = structural_fingerprint()
    removed = remove_previous_tutorial_notes()
    annotator = Annotator(name)
    annotate_scene(annotator)
    hou.hipFile.save(file_name=temp_path, save_to_recent_files=False)

    hou.hipFile.load(temp_path, suppress_save_prompt=True, ignore_load_warnings=True)
    after = structural_fingerprint()
    counts = count_tutorial_notes()
    if before != after:
        raise RuntimeError("Structural fingerprint changed: {} -> {}".format(before, after))
    if len(annotator.created) != sum(counts.values()):
        raise RuntimeError("Tutorial note count mismatch: created {}, reloaded {}".format(
            len(annotator.created), sum(counts.values())))

    os.replace(temp_path, path)
    print("OK {} | notes={} | networks={} | replaced_old={} | fingerprint={}".format(
        name, sum(counts.values()), len(counts), removed, before[:16]))
    if annotator.skipped:
        print("  skipped anchors/networks: " + repr(annotator.skipped))
    print("  annotated: " + ", ".join(sorted(counts)))


def main():
    hou.setUpdateMode(hou.updateMode.Manual)
    paths = [os.path.join(ROOT, name) for name in sorted(INTRO_TEXT)]
    failures = []
    for path in paths:
        try:
            process(path)
        except Exception as exc:
            failures.append((path, str(exc)))
            print("FAILED {}: {}".format(os.path.basename(path), exc))
            traceback.print_exc()
    if failures:
        print("\n{} file(s) failed".format(len(failures)))
        for path, message in failures:
            print("  {}: {}".format(os.path.basename(path), message))
        sys.exit(1)


if __name__ == "__main__":
    main()
