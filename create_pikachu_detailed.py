"""
Detailed stylized Pikachu character — street fashion outfit.
Reference: Yellow beanie, yellow hoodie, blue varsity jacket,
white sneakers, winking, peace sign, warm golden background.
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ============================================================
# UTILITIES
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in [bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.particles]:
        for block in coll:
            if block.users == 0:
                coll.remove(block)

def mat(name, color, rough=0.6, spec=0.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = spec
    return m

def assign(obj, material):
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

def sm(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)

def ss(obj, vp=2, rn=3):
    obj.modifiers.new("SS", 'SUBSURF')
    obj.modifiers["SS"].levels = vp
    obj.modifiers["SS"].render_levels = rn

def par(child, parent_obj):
    child.parent = parent_obj
    child.matrix_parent_inverse = parent_obj.matrix_world.inverted()

def fur(obj, count=2000, length=0.03):
    mod = obj.modifiers.new("Fur", 'PARTICLE_SYSTEM')
    ps = mod.particle_system.settings
    ps.type = 'HAIR'
    ps.count = count
    ps.hair_length = length
    ps.child_type = 'INTERPOLATED'
    ps.child_percent = 30
    ps.rendered_child_count = 8
    ps.clump_factor = 0.4
    ps.roughness_1 = 0.015
    ps.root_radius = 0.4
    ps.tip_radius = 0.08

# ============================================================
clear_scene()

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 72
scene.frame_set(1)

# ============================================================
# MATERIALS
# ============================================================
m_fur      = mat("Fur_Yellow",   (1.0, 0.82, 0.15, 1.0), 0.75)
m_cream    = mat("Fur_Cream",    (1.0, 0.93, 0.72, 1.0), 0.75)
m_black    = mat("Black",        (0.01, 0.01, 0.01, 1.0), 0.4)
m_eye      = mat("Eye_Brown",    (0.22, 0.08, 0.03, 1.0), 0.22, 0.6)
m_white    = mat("White",        (1.0, 1.0, 1.0, 1.0), 0.25, 0.7)
m_blush    = mat("Blush",        (1.0, 0.42, 0.38, 1.0), 0.7)
m_hoodie   = mat("Hoodie",       (0.95, 0.72, 0.05, 1.0), 0.88)
m_trim     = mat("HoodieTrim",   (0.6, 0.22, 0.06, 1.0), 0.82)
m_jacket   = mat("Jacket",       (0.10, 0.16, 0.32, 1.0), 0.92)
m_stripe   = mat("JacketStripe", (0.92, 0.92, 0.92, 1.0), 0.7)
m_beanie   = mat("Beanie",       (0.90, 0.70, 0.04, 1.0), 0.92)
m_shoe     = mat("Shoe",         (0.94, 0.94, 0.94, 1.0), 0.5)
m_sole     = mat("Sole",         (0.82, 0.82, 0.82, 1.0), 0.6)
m_gray     = mat("EarTipGray",   (0.32, 0.32, 0.32, 1.0), 0.72)
m_ground   = mat("Ground",       (0.82, 0.62, 0.04, 1.0), 0.95)
m_cord     = mat("Drawcord",     (0.92, 0.90, 0.85, 1.0), 0.65)

# ============================================================
# BODY SKELETON — all at origin, build upward
# Z=0 is ground level
# ============================================================

# === HEAD — oversized, the star feature ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=1.15, location=(0, 0, 4.0))
head = bpy.context.active_object
head.name = "Head"
head.scale = (1.0, 0.90, 0.97)
assign(head, m_fur)
ss(head, 2, 3)
sm(head)
fur(head, 4000, 0.04)

# === TORSO (hidden by hoodie+jacket) ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.82, location=(0, 0, 2.65))
torso = bpy.context.active_object
torso.name = "Torso"
torso.scale = (0.95, 0.80, 1.05)
assign(torso, m_fur)
ss(torso, 1, 2)
sm(torso)

# === HIPS ===
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.60, location=(0, 0, 1.7))
hips = bpy.context.active_object
hips.name = "Hips"
hips.scale = (0.88, 0.75, 0.75)
assign(hips, m_fur)
ss(hips, 1, 2)
sm(hips)

# ============================================================
# FACE
# ============================================================

# Right eye (open) — large brown iris, pushed OUT from head surface
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.28,
    location=(-0.36, -1.02, 4.05))
eye_r = bpy.context.active_object
eye_r.name = "Eye_R"
eye_r.scale = (0.82, 0.55, 1.10)
assign(eye_r, m_eye)
sm(eye_r)
par(eye_r, head)

# Eye highlights — pushed further forward
for n, r, loc in [
    ("HL1", 0.08, (-0.30, -1.18, 4.18)),
    ("HL2", 0.045, (-0.43, -1.15, 3.95)),
]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r, location=loc)
    h = bpy.context.active_object
    h.name = f"Eye_R_{n}"
    assign(h, m_white)
    sm(h)
    par(h, head)

# Left eye — wink (curved line), pushed forward
bpy.ops.curve.primitive_bezier_curve_add(location=(0.36, -1.06, 4.0))
wink = bpy.context.active_object
wink.name = "Wink"
sp = wink.data.splines[0]
sp.bezier_points[0].co = (-0.17, 0, 0)
sp.bezier_points[0].handle_left  = (-0.24, 0, 0.07)
sp.bezier_points[0].handle_right = (-0.09, 0, -0.06)
sp.bezier_points[1].co = (0.17, 0, 0)
sp.bezier_points[1].handle_left  = (0.09, 0, -0.06)
sp.bezier_points[1].handle_right = (0.24, 0, 0.07)
wink.data.bevel_depth = 0.028
wink.data.bevel_resolution = 4
wink.data.fill_mode = 'FULL'
assign(wink, m_black)
par(wink, head)

# Nose — pushed forward
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.06,
    location=(0, -1.15, 3.82))
nose = bpy.context.active_object
nose.name = "Nose"
nose.scale = (1.3, 0.6, 0.65)
assign(nose, m_black)
sm(nose)
par(nose, head)

# Mouth — slight smirk, pushed forward
bpy.ops.curve.primitive_bezier_curve_add(location=(0.04, -1.08, 3.62))
mouth = bpy.context.active_object
mouth.name = "Mouth"
sp = mouth.data.splines[0]
sp.bezier_points[0].co = (-0.14, 0, 0)
sp.bezier_points[0].handle_left  = (-0.20, 0, 0.04)
sp.bezier_points[0].handle_right = (-0.07, 0, -0.03)
sp.bezier_points[1].co = (0.14, 0, 0.02)
sp.bezier_points[1].handle_left  = (0.07, 0, -0.02)
sp.bezier_points[1].handle_right = (0.20, 0, 0.05)
mouth.data.bevel_depth = 0.016
mouth.data.bevel_resolution = 3
mouth.data.fill_mode = 'FULL'
assign(mouth, m_black)
par(mouth, head)

# Blush cheeks — pushed forward and bigger
for side, xs in [("L", 0.60), ("R", -0.60)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=0.22,
        location=(xs, -0.82, 3.65))
    ch = bpy.context.active_object
    ch.name = f"Blush_{side}"
    ch.scale = (1.0, 0.35, 0.70)
    assign(ch, m_blush)
    sm(ch)
    par(ch, head)

# ============================================================
# EARS — tall, poking through beanie
# ============================================================
for side, xs in [("L", 0.48), ("R", -0.48)]:
    # Yellow base
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.30, radius2=0.03,
        depth=1.7, location=(xs, 0.08, 5.35))
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.rotation_euler = (0.12, 0, xs * 0.65)
    ear.scale = (0.55, 0.30, 1.0)
    assign(ear, m_fur)
    ss(ear, 2, 3)
    sm(ear)
    fur(ear, 1200, 0.035)
    par(ear, head)

    # Gray/dark tip
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.19, radius2=0.02,
        depth=0.75, location=(xs * 1.35, 0.08, 6.05))
    tip = bpy.context.active_object
    tip.name = f"EarTip_{side}"
    tip.rotation_euler = (0.12, 0, xs * 0.65)
    tip.scale = (0.50, 0.28, 1.0)
    assign(tip, m_gray)
    ss(tip, 2, 3)
    sm(tip)
    fur(tip, 600, 0.03)
    par(tip, head)

    # Inner ear
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.10,
        location=(xs * 0.9, -0.06, 5.5))
    inn = bpy.context.active_object
    inn.name = f"EarIn_{side}"
    inn.scale = (0.25, 0.12, 0.7)
    inn.rotation_euler = (0.12, 0, xs * 0.65)
    assign(inn, m_cream)
    sm(inn)
    par(inn, head)

# ============================================================
# BEANIE — sits on top of head, ears poke through
# ============================================================
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1.22,
    location=(0, 0.04, 4.25))
beanie = bpy.context.active_object
beanie.name = "Beanie"
beanie.scale = (1.02, 0.94, 0.48)
assign(beanie, m_beanie)
ss(beanie, 2, 3)
sm(beanie)
par(beanie, head)

# Beanie rolled rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.12, minor_radius=0.10,
    major_segments=32, minor_segments=10, location=(0, 0.02, 3.95))
rim = bpy.context.active_object
rim.name = "BeanieRim"
rim.scale = (1.0, 0.92, 0.65)
assign(rim, m_beanie)
sm(rim)
par(rim, head)

# ============================================================
# HOODIE — yellow, visible at front and bottom
# ============================================================
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.92, depth=1.7,
    location=(0, 0, 2.65))
hoodie = bpy.context.active_object
hoodie.name = "Hoodie"
hoodie.scale = (1.0, 0.86, 1.0)
assign(hoodie, m_hoodie)
ss(hoodie, 1, 2)
sm(hoodie)

# Hood (behind head)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.82,
    location=(0, 0.58, 3.75))
hood = bpy.context.active_object
hood.name = "Hood"
hood.scale = (1.08, 0.65, 0.85)
assign(hood, m_hoodie)
ss(hood, 1, 2)
sm(hood)
par(hood, head)

# Hoodie collar
bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.13,
    major_segments=24, minor_segments=8, location=(0, -0.06, 3.28))
collar = bpy.context.active_object
collar.name = "HoodieCollar"
collar.scale = (1.0, 0.88, 0.55)
assign(collar, m_hoodie)
sm(collar)

# Hoodie bottom trim
bpy.ops.mesh.primitive_torus_add(major_radius=0.88, minor_radius=0.07,
    major_segments=24, minor_segments=8, location=(0, 0, 1.82))
h_trim = bpy.context.active_object
h_trim.name = "HoodieTrim"
assign(h_trim, m_trim)
sm(h_trim)

# Drawstrings
for side, xs in [("L", -0.12), ("R", 0.12)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.45,
        location=(xs, -0.72, 3.05))
    ds = bpy.context.active_object
    ds.name = f"Cord_{side}"
    ds.rotation_euler = (0.08, xs * 0.3, 0)
    assign(ds, m_cord)
    sm(ds)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.022,
        location=(xs, -0.74, 2.82))
    cap = bpy.context.active_object
    cap.name = f"CordCap_{side}"
    assign(cap, m_cord)
    sm(cap)

# ============================================================
# JACKET — blue varsity, over hoodie
# ============================================================
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.04, depth=1.5,
    location=(0, 0, 2.7))
jacket = bpy.context.active_object
jacket.name = "Jacket"
jacket.scale = (1.0, 0.88, 1.0)
assign(jacket, m_jacket)
ss(jacket, 1, 2)
sm(jacket)

# Jacket collar (white/cream)
bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.09,
    major_segments=24, minor_segments=8, location=(0, -0.08, 3.3))
jc = bpy.context.active_object
jc.name = "JacketCollar"
jc.scale = (1.0, 0.82, 0.48)
assign(jc, m_stripe)
sm(jc)

# Hem stripes (white bands at bottom)
for i, z in enumerate([1.98, 2.08]):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.04,
        major_segments=24, minor_segments=8, location=(0, 0, z))
    st = bpy.context.active_object
    st.name = f"HemStripe_{i}"
    assign(st, m_stripe)
    sm(st)

# Front opening — shows yellow hoodie underneath
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0, -0.88, 2.7))
opening = bpy.context.active_object
opening.name = "JacketOpening"
opening.scale = (0.45, 0.08, 1.1)
assign(opening, m_hoodie)

# ============================================================
# ARMS
# ============================================================

# RIGHT ARM — raised, peace sign
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.20, depth=0.85,
    location=(0.88, -0.25, 3.3))
arm_r = bpy.context.active_object
arm_r.name = "ArmR"
arm_r.rotation_euler = (0.25, 0, 0.75)
assign(arm_r, m_jacket)
ss(arm_r, 1, 2)
sm(arm_r)

# Right sleeve cuff stripe
bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.035,
    major_segments=16, minor_segments=6, location=(1.18, -0.42, 3.58))
cuff_r = bpy.context.active_object
cuff_r.name = "CuffR"
cuff_r.rotation_euler = (0.25, 0, 0.75)
assign(cuff_r, m_stripe)
sm(cuff_r)

# Right hand (yellow paw)
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.19,
    location=(1.28, -0.52, 3.72))
hand_r = bpy.context.active_object
hand_r.name = "HandR"
hand_r.scale = (0.80, 0.65, 0.95)
assign(hand_r, m_fur)
ss(hand_r, 1, 2)
sm(hand_r)

# Peace sign — two fingers up
for i, (fx, fy, fz, rz) in enumerate([
    (1.36, -0.58, 3.98, -0.12),
    (1.43, -0.55, 3.96, 0.18),
]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.28,
        location=(fx, fy, fz))
    f = bpy.context.active_object
    f.name = f"Finger_{i}"
    f.rotation_euler = (-0.15, rz, 0.55)
    assign(f, m_fur)
    ss(f, 1, 2)
    sm(f)
    par(f, hand_r)

    # Rounded tip
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.043,
        location=(fx + 0.06, fy - 0.02, fz + 0.14))
    ft = bpy.context.active_object
    ft.name = f"FTip_{i}"
    assign(ft, m_fur)
    sm(ft)
    par(ft, hand_r)

# LEFT ARM — hanging at side
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.20, depth=0.85,
    location=(-0.82, -0.18, 2.8))
arm_l = bpy.context.active_object
arm_l.name = "ArmL"
arm_l.rotation_euler = (0.12, 0, -0.48)
assign(arm_l, m_jacket)
ss(arm_l, 1, 2)
sm(arm_l)

# Left cuff stripe
bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.035,
    major_segments=16, minor_segments=6, location=(-1.05, -0.22, 2.52))
cuff_l = bpy.context.active_object
cuff_l.name = "CuffL"
cuff_l.rotation_euler = (0.12, 0, -0.48)
assign(cuff_l, m_stripe)
sm(cuff_l)

# Left hand
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.17,
    location=(-1.08, -0.25, 2.32))
hand_l = bpy.context.active_object
hand_l.name = "HandL"
hand_l.scale = (0.80, 0.65, 0.95)
assign(hand_l, m_fur)
ss(hand_l, 1, 2)
sm(hand_l)

# ============================================================
# LEGS — short yellow
# ============================================================
for side, xs in [("L", -0.32), ("R", 0.32)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=0.50,
        location=(xs, 0, 1.15))
    leg = bpy.context.active_object
    leg.name = f"Leg_{side}"
    assign(leg, m_fur)
    ss(leg, 1, 2)
    sm(leg)
    fur(leg, 600, 0.022)

# ============================================================
# SNEAKERS
# ============================================================
for side, xs in [("L", -0.32), ("R", 0.32)]:
    # Shoe body
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(xs, -0.06, 0.52))
    shoe = bpy.context.active_object
    shoe.name = f"Shoe_{side}"
    shoe.scale = (0.72, 1.15, 0.52)
    assign(shoe, m_shoe)
    ss(shoe, 2, 3)
    sm(shoe)

    # Sole
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(xs, -0.06, 0.30))
    sole = bpy.context.active_object
    sole.name = f"Sole_{side}"
    sole.scale = (0.78, 1.25, 0.18)
    assign(sole, m_sole)
    ss(sole, 1, 2)
    sm(sole)

    # Toe cap
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.14,
        location=(xs, -0.32, 0.42))
    toe = bpy.context.active_object
    toe.name = f"Toe_{side}"
    toe.scale = (0.95, 0.75, 0.65)
    assign(toe, m_shoe)
    sm(toe)

# ============================================================
# TAIL — zigzag
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.82, 2.0))
tail = bpy.context.active_object
tail.name = "Tail"
bpy.context.view_layer.objects.active = tail
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tail.data)
bm.clear()

hw = 0.14
for i, (y, z) in enumerate([
    (0.0, 0.0), (0.28, 0.52), (0.04, 0.62),
    (0.32, 1.12), (0.10, 1.22), (0.42, 1.72),
]):
    bm.verts.new((-hw, y, z))
    bm.verts.new((hw, y, z))

bm.verts.ensure_lookup_table()
for i in range(0, len(bm.verts) - 2, 2):
    bm.faces.new([bm.verts[i], bm.verts[i+1], bm.verts[i+3], bm.verts[i+2]])

bmesh.update_edit_mesh(tail.data)
bpy.ops.object.mode_set(mode='OBJECT')

tail.location = (0, 0.72, 1.6)
tail.rotation_euler = (-0.12, 0, 0)
sol = tail.modifiers.new("Sol", 'SOLIDIFY')
sol.thickness = 0.13
sol.offset = 0
ss(tail, 1, 2)
assign(tail, m_fur)
sm(tail)

# ============================================================
# ENVIRONMENT — warm golden
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
assign(ground, m_ground)

world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.88, 0.68, 0.10, 1.0)
bg.inputs['Strength'].default_value = 0.55

# ============================================================
# LIGHTING — warm studio, 4-light
# ============================================================
lights = [
    ("Key",  (-3.5, -5.5, 7),  280, 5.5, (1.0, 0.92, 0.75), (50, -10, -15)),
    ("Fill", (4.0, -3.5, 4.5), 110, 4.5, (1.0, 0.90, 0.78), (45, 12, 10)),
    ("Rim",  (0, 5.5, 5.5),    160, 3.5, (1.0, 0.88, 0.62), (-42, 0, 0)),
    ("Top",  (0, 0, 9),         90, 7,   (1.0, 0.95, 0.85), (0, 0, 0)),
]
for name, loc, energy, size, color, rot in lights:
    bpy.ops.object.light_add(type='AREA', location=loc)
    lt = bpy.context.active_object
    lt.name = f"Light_{name}"
    lt.data.energy = energy
    lt.data.size = size
    lt.data.color = color
    lt.rotation_euler = tuple(math.radians(r) for r in rot)

# ============================================================
# CAMERA — portrait framing, full body
# ============================================================
# Slightly angled front view — shows face, outfit, ears, sneakers
bpy.ops.object.camera_add(location=(2.0, -13.0, 4.0))
cam = bpy.context.active_object
cam.name = "Camera"
target = Vector((0, 0, 3.2))
d = target - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65
cam.data.clip_end = 60
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 13.0
cam.data.dof.aperture_fstop = 2.8
scene.camera = cam

# ============================================================
# ANIMATION — gentle bobble, wave, walk
# ============================================================

# Head bob & slight turn
for f, rz, rx in [(1, 0, 0), (18, 0.07, -0.02), (36, -0.04, 0.015),
                   (54, 0.05, -0.015), (72, 0, 0)]:
    head.rotation_euler = (rx, 0, rz)
    head.keyframe_insert(data_path="rotation_euler", frame=f)

# Vertical bounce
base_z = head.location.z
for f, dz in [(1, 0), (9, 0.05), (18, 0), (27, 0.05), (36, 0),
              (45, 0.04), (54, 0), (63, 0.04), (72, 0)]:
    head.location.z = base_z + dz
    head.keyframe_insert(data_path="location", frame=f)

# Subtle forward walk
base_y = head.location.y
for f, dy in [(1, 0), (36, -0.25), (72, -0.45)]:
    head.location.y = base_y + dy
    head.keyframe_insert(data_path="location", frame=f)

# Peace hand wave
for f, rz in [(1, 0), (12, 0.14), (24, -0.08), (36, 0.11),
              (48, -0.07), (60, 0.09), (72, 0)]:
    hand_r.rotation_euler = (0, 0, rz)
    hand_r.keyframe_insert(data_path="rotation_euler", frame=f)

# ============================================================
# RENDER
# ============================================================
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 72
scene.cycles.use_denoising = False
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.fps = 24

# Save
blend_path = "/home/user/Claude-Baba/pikachu_detailed.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"\n✅ Saved: {blend_path}")

# Render preview at 35% res
scene.frame_set(1)
scene.render.filepath = "/home/user/Claude-Baba/pikachu_detailed_preview.png"
scene.render.resolution_percentage = 50
scene.cycles.samples = 72
bpy.ops.render.render(write_still=True)
print(f"✅ Preview: {scene.render.filepath}")
