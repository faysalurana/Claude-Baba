"""
Create a cute, stylized 3D Pikachu character in Blender.
Features: oversized yellow head, small body, pointed black-tipped ears,
large expressive eyes, red cheeks, tiny nose, smile, short arms/legs,
iconic brown zigzag tail. Clean smooth geometry, simple matte materials,
polished toy-like proportions. Studio background, ground plane, gentle
lighting, three-quarter camera angle.
"""

import bpy
import bmesh
import math
from mathutils import Vector

# ============================================================
# Utility functions
# ============================================================

def clear_scene():
    """Remove all default objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)


def create_material(name, color, roughness=0.7):
    """Create a simple matte Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Specular IOR Level'].default_value = 0.3
    return mat


def assign_material(obj, mat):
    """Assign a material to an object."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def smooth_shade(obj):
    """Apply smooth shading."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)


def add_subsurf(obj, levels=2, render_levels=3):
    """Add subdivision surface modifier."""
    mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels


def parent_to(child, parent):
    """Parent child object to parent object, keeping transforms."""
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


# ============================================================
# Setup
# ============================================================

clear_scene()

# ============================================================
# Materials
# ============================================================

mat_yellow = create_material("Pikachu_Yellow", (1.0, 0.83, 0.1, 1.0), roughness=0.55)
mat_black = create_material("Pikachu_Black", (0.015, 0.015, 0.015, 1.0), roughness=0.45)
mat_red = create_material("Pikachu_Red", (0.85, 0.08, 0.1, 1.0), roughness=0.55)
mat_brown = create_material("Pikachu_Brown", (0.4, 0.22, 0.05, 1.0), roughness=0.55)
mat_white = create_material("Pikachu_White", (1.0, 1.0, 1.0, 1.0), roughness=0.4)
mat_nose_black = create_material("Pikachu_Nose", (0.03, 0.03, 0.03, 1.0), roughness=0.35)
mat_mouth_red = create_material("Pikachu_Mouth", (0.5, 0.1, 0.08, 1.0), roughness=0.65)
mat_ground = create_material("Ground", (0.9, 0.9, 0.92, 1.0), roughness=0.95)
mat_backdrop = create_material("Backdrop", (0.78, 0.84, 0.92, 1.0), roughness=1.0)

# ============================================================
# HEAD — large, round, slightly squashed sphere
# ============================================================

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0, location=(0, 0, 2.3))
head = bpy.context.active_object
head.name = "Head"
head.scale = (1.0, 0.88, 1.0)
assign_material(head, mat_yellow)
add_subsurf(head, 2, 3)
smooth_shade(head)

# ============================================================
# BODY — smaller, pudgy sphere below head
# ============================================================

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.72, location=(0, 0, 1.05))
body = bpy.context.active_object
body.name = "Body"
body.scale = (0.88, 0.78, 1.0)
assign_material(body, mat_yellow)
add_subsurf(body, 2, 3)
smooth_shade(body)
parent_to(body, head)

# ============================================================
# EARS — pointed cones with black tips
# ============================================================

for side, x_sign in [("Left", -1), ("Right", 1)]:
    # Ear base (yellow) — long, iconic pointed ears
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.32, radius2=0.0, depth=1.8,
        location=(x_sign * 0.55, 0.05, 3.6)
    )
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.rotation_euler = (0.15, 0, x_sign * 0.35)
    ear.scale = (0.55, 0.32, 1.0)
    assign_material(ear, mat_yellow)
    add_subsurf(ear, 2, 3)
    smooth_shade(ear)
    parent_to(ear, head)

    # Ear tip (black) — prominent dark tip
    bpy.ops.mesh.primitive_cone_add(
        vertices=16, radius1=0.22, radius2=0.0, depth=0.85,
        location=(x_sign * 0.70, 0.05, 4.25)
    )
    tip = bpy.context.active_object
    tip.name = f"EarTip_{side}"
    tip.rotation_euler = (0.15, 0, x_sign * 0.35)
    tip.scale = (0.55, 0.33, 1.0)
    assign_material(tip, mat_black)
    add_subsurf(tip, 2, 3)
    smooth_shade(tip)
    parent_to(tip, head)

# ============================================================
# EYES — large black spheres with white highlights
# ============================================================

for side, x_sign in [("Left", -1), ("Right", 1)]:
    # Main eye
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, radius=0.22,
        location=(x_sign * 0.33, -0.76, 2.42)
    )
    eye = bpy.context.active_object
    eye.name = f"Eye_{side}"
    eye.scale = (0.85, 0.65, 1.1)
    assign_material(eye, mat_black)
    smooth_shade(eye)
    parent_to(eye, head)

    # Upper highlight (larger)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=0.065,
        location=(x_sign * 0.27, -0.90, 2.52)
    )
    hl1 = bpy.context.active_object
    hl1.name = f"EyeHL1_{side}"
    assign_material(hl1, mat_white)
    smooth_shade(hl1)
    parent_to(hl1, head)

    # Lower highlight (smaller)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=6, radius=0.038,
        location=(x_sign * 0.37, -0.88, 2.34)
    )
    hl2 = bpy.context.active_object
    hl2.name = f"EyeHL2_{side}"
    assign_material(hl2, mat_white)
    smooth_shade(hl2)
    parent_to(hl2, head)

# ============================================================
# RED CHEEKS
# ============================================================

for side, x_sign in [("Left", -1), ("Right", 1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, radius=0.17,
        location=(x_sign * 0.62, -0.58, 2.1)
    )
    cheek = bpy.context.active_object
    cheek.name = f"Cheek_{side}"
    cheek.scale = (1.0, 0.45, 0.8)
    assign_material(cheek, mat_red)
    smooth_shade(cheek)
    parent_to(cheek, head)

# ============================================================
# NOSE — tiny black oval
# ============================================================

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16, ring_count=8, radius=0.055,
    location=(0, -0.90, 2.2)
)
nose = bpy.context.active_object
nose.name = "Nose"
nose.scale = (1.3, 0.7, 0.7)
assign_material(nose, mat_nose_black)
smooth_shade(nose)
parent_to(nose, head)

# ============================================================
# SMILE — curved bezier
# ============================================================

bpy.ops.curve.primitive_bezier_curve_add(location=(0, -0.86, 2.06))
smile = bpy.context.active_object
smile.name = "Smile"

spline = smile.data.splines[0]
spline.bezier_points[0].co = (-0.22, 0.0, 0.0)
spline.bezier_points[0].handle_left = (-0.32, 0.0, 0.06)
spline.bezier_points[0].handle_right = (-0.12, 0.0, -0.04)
spline.bezier_points[1].co = (0.22, 0.0, 0.0)
spline.bezier_points[1].handle_left = (0.12, 0.0, -0.04)
spline.bezier_points[1].handle_right = (0.32, 0.0, 0.06)

smile.data.bevel_depth = 0.018
smile.data.bevel_resolution = 4
smile.data.fill_mode = 'FULL'
assign_material(smile, mat_mouth_red)
parent_to(smile, head)

# ============================================================
# ARMS — short stubby appendages
# ============================================================

for side, x_sign in [("Left", -1), ("Right", 1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=0.18,
        location=(x_sign * 0.78, -0.08, 1.2)
    )
    arm = bpy.context.active_object
    arm.name = f"Arm_{side}"
    arm.scale = (0.65, 0.55, 1.4)
    arm.rotation_euler = (0.25, 0, x_sign * 0.55)
    assign_material(arm, mat_yellow)
    add_subsurf(arm, 1, 2)
    smooth_shade(arm)
    parent_to(arm, body)

# ============================================================
# FEET — short rounded
# ============================================================

for side, x_sign in [("Left", -1), ("Right", 1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=0.24,
        location=(x_sign * 0.32, -0.12, 0.24)
    )
    foot = bpy.context.active_object
    foot.name = f"Foot_{side}"
    foot.scale = (0.85, 1.25, 0.55)
    assign_material(foot, mat_yellow)
    add_subsurf(foot, 1, 2)
    smooth_shade(foot)
    parent_to(foot, body)

# ============================================================
# ZIGZAG TAIL — iconic lightning bolt shape
# ============================================================

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.6, 1.1))
tail = bpy.context.active_object
tail.name = "Tail"

bpy.context.view_layer.objects.active = tail
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tail.data)
bm.clear()

# Lightning bolt zigzag profile (Y=back, Z=up)
hw = 0.14  # half-width

zigzag = [
    (0.0, 0.0),    # base at body
    (0.25, 0.55),   # zig up-right
    (0.0, 0.65),    # zag back
    (0.30, 1.15),   # zig up-right
    (0.08, 1.25),   # zag back
    (0.40, 1.75),   # top point
]

verts_pairs = []
for y, z in zigzag:
    v_l = bm.verts.new((-hw, y, z))
    v_r = bm.verts.new((hw, y, z))
    verts_pairs.append((v_l, v_r))

for i in range(len(verts_pairs) - 1):
    bl, br = verts_pairs[i]
    tl, tr = verts_pairs[i + 1]
    bm.faces.new([bl, br, tr, tl])

bmesh.update_edit_mesh(tail.data)
bpy.ops.object.mode_set(mode='OBJECT')

tail.location = (0, 0.65, 1.0)
tail.rotation_euler = (-0.15, 0, 0)

solidify = tail.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.14
solidify.offset = 0

add_subsurf(tail, 1, 2)
assign_material(tail, mat_brown)
smooth_shade(tail)
parent_to(tail, body)

# ============================================================
# STUDIO ENVIRONMENT
# ============================================================

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
assign_material(ground, mat_ground)

# Curved backdrop — seamless full-coverage background
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 14, 12))
backdrop = bpy.context.active_object
backdrop.name = "Backdrop"
backdrop.rotation_euler = (math.radians(65), 0, 0)
backdrop.scale = (2.0, 2.0, 3.0)
assign_material(backdrop, mat_backdrop)

# ============================================================
# LIGHTING — gentle three-point studio
# ============================================================

# Key light (warm)
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 5))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 200
key.data.size = 4
key.data.color = (1.0, 0.95, 0.9)
key.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-20))

# Fill light (cool)
bpy.ops.object.light_add(type='AREA', location=(4, -3, 3))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 80
fill.data.size = 5
fill.data.color = (0.85, 0.9, 1.0)
fill.rotation_euler = (math.radians(50), math.radians(20), math.radians(15))

# Rim light
bpy.ops.object.light_add(type='AREA', location=(0, 4, 4))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 120
rim.data.size = 3
rim.data.color = (1.0, 1.0, 1.0)
rim.rotation_euler = (math.radians(-45), 0, 0)

# World background
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    # Match the backdrop color so edges are invisible
    bg.inputs['Color'].default_value = (0.78, 0.84, 0.92, 1.0)
    bg.inputs['Strength'].default_value = 0.4

# ============================================================
# CAMERA — three-quarter view showing face, body, ears, tail
# ============================================================

# Three-quarter view: face + body + ears + tail all visible
bpy.ops.object.camera_add(location=(6.5, -5.5, 4.8))
camera = bpy.context.active_object
camera.name = "Camera"

target = Vector((-0.1, 0, 1.8))
direction = target - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

camera.data.lens = 45
camera.data.clip_end = 100
bpy.context.scene.camera = camera

# ============================================================
# RENDER SETTINGS
# ============================================================

scene = bpy.context.scene

# Save .blend with EEVEE settings (best for opening locally)
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 64
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False

# ============================================================
# SAVE .blend file
# ============================================================

output_blend = "/home/user/Claude-Baba/pikachu_model.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_blend)
print(f"\n✅ Pikachu model saved to: {output_blend}")

# ============================================================
# RENDER PREVIEW — switch to Cycles CPU (no GPU/EGL needed)
# ============================================================

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 96
scene.cycles.use_denoising = False
scene.render.filepath = "/home/user/Claude-Baba/pikachu_preview.png"
scene.render.resolution_percentage = 60
bpy.ops.render.render(write_still=True)
print(f"✅ Preview rendered to: {scene.render.filepath}")

# Save again with Cycles settings so it opens nicely
bpy.ops.wm.save_as_mainfile(filepath=output_blend)
print("✅ Final .blend saved.")
